# Copyright 2024 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from collections import OrderedDict

import torch

from ..logits_process import LogitsProcessor
from ..stopping_criteria import StoppingCriteria
from .base import SafetyChecker, SafetyResult, SafetyViolation
from .configuration import SafetyConfig


logger = logging.getLogger(__name__)


class SafetyLogitsProcessor(LogitsProcessor):
    """
    [`LogitsProcessor`] that blocks generation when unsafe content is detected.

    This processor checks the current sequence for safety violations and blocks
    further generation by suppressing all tokens when unsafe content is detected.
    It integrates with the transformers safety framework to provide real-time
    content blocking.

    Args:
        safety_checker ([`SafetyChecker`]):
            The safety checker to use for content evaluation.
        tokenizer ([`PreTrainedTokenizer`]):
            The tokenizer used for decoding sequences.
        safety_config ([`SafetyConfig`]):
            Configuration for safety checking.
        check_interval (`int`, *optional*, defaults to 1):
            Check safety every N tokens. Must be positive.
        suppress_threshold (`float`, *optional*, defaults to negative infinity):
            Logit value for suppressing unsafe tokens.

    Examples:

    ```python
    >>> from transformers import AutoTokenizer, AutoModelForCausalLM
    >>> from transformers.generation.safety import SafetyLogitsProcessor, BasicToxicityChecker, SafetyConfig

    >>> # Initialize model and tokenizer
    >>> model = AutoModelForCausalLM.from_pretrained("gpt2")
    >>> tokenizer = AutoTokenizer.from_pretrained("gpt2")
    >>> tokenizer.pad_token = tokenizer.eos_token

    >>> # Create safety components
    >>> safety_config = SafetyConfig.create_default("moderate")
    >>> safety_checker = BasicToxicityChecker()
    >>> safety_processor = SafetyLogitsProcessor(
    ...     safety_checker=safety_checker,
    ...     tokenizer=tokenizer,
    ...     safety_config=safety_config
    ... )

    >>> # Generate with safety filtering
    >>> inputs = tokenizer("Tell me about", return_tensors="pt")
    >>> outputs = model.generate(
    ...     **inputs,
    ...     logits_processor=[safety_processor],
    ...     max_new_tokens=50,
    ...     do_sample=True
    ... )
    >>> generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    ```
    """

    def __init__(
        self,
        safety_checker: SafetyChecker,
        tokenizer,
        safety_config: SafetyConfig,
        check_interval: int = 1,
        suppress_threshold: float = -float("inf"),
    ):
        """
        Initialize the SafetyLogitsProcessor.

        Args:
            safety_checker: The safety checker to use for content evaluation
            tokenizer: The tokenizer used for decoding sequences
            safety_config: Configuration for safety checking
            check_interval: Check safety every N tokens (default: 1, must be positive)
            suppress_threshold: Logit value for suppressing unsafe tokens

        Raises:
            ValueError: If check_interval is not positive
        """
        # Input validation
        if not isinstance(check_interval, int) or check_interval < 1:
            raise ValueError(f"check_interval must be a positive integer, got {check_interval}")

        self.safety_checker = safety_checker
        self.tokenizer = tokenizer
        self.safety_config = safety_config
        self.check_interval = check_interval
        self.suppress_threshold = suppress_threshold
        self._step_count = 0
        self._sequence_cache = OrderedDict()  # LRU cache for recently checked sequences

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        """
        Apply safety filtering to token scores.

        Args:
            input_ids: Current sequence tokens [batch_size, seq_len]
            scores: Token logits [batch_size, vocab_size]

        Returns:
            Modified scores with unsafe tokens suppressed
        """
        self._step_count += 1

        # Only check safety at specified intervals for performance
        if self._step_count % self.check_interval != 0:
            return scores

        batch_size = input_ids.shape[0]
        modified_scores = scores.clone()

        for i in range(batch_size):
            # Convert current sequence to text
            current_sequence = input_ids[i]
            current_text = self.tokenizer.decode(current_sequence, skip_special_tokens=True)

            # Check cache first (using more robust cache key)
            cache_key = f"{len(current_text)}:{current_text[:100]}"
            if cache_key in self._sequence_cache:
                # Move to end for LRU behavior
                safety_result = self._sequence_cache.pop(cache_key)
                self._sequence_cache[cache_key] = safety_result
            else:
                # Check safety of current sequence
                try:
                    safety_result = self.safety_checker.check_safety(current_text)
                except Exception as e:
                    logger.warning(f"Safety check failed for sequence: {e}")
                    # Fail safe - assume unsafe if we can't check
                    from .base import SafetyResult, SafetyViolation

                    safety_result = SafetyResult(
                        is_safe=False,
                        confidence=0.0,
                        violations=[SafetyViolation("unknown", 0.0, "high", "Safety check failed")],
                        metadata={"error": str(e)},
                    )

                # Cache the result with LRU behavior
                if len(self._sequence_cache) >= 100:
                    # Remove oldest entry
                    self._sequence_cache.popitem(last=False)
                self._sequence_cache[cache_key] = safety_result

            if not safety_result.is_safe:
                # Apply suppression strategy
                tokens_to_suppress = self._get_tokens_to_suppress(scores[i], safety_result)

                # Suppress tokens
                if len(tokens_to_suppress) > 0:
                    # Ensure tensors are on the same device
                    device = scores.device
                    if isinstance(tokens_to_suppress, list):
                        tokens_to_suppress = torch.tensor(tokens_to_suppress, device=device)

                    modified_scores[i, tokens_to_suppress] = self.suppress_threshold
                    logger.debug(
                        f"Suppressed {len(tokens_to_suppress)} tokens using blocking strategy "
                        f"for sequence: {current_text[:50]}..."
                    )

        return modified_scores

    def _get_tokens_to_suppress(self, scores: torch.FloatTensor, safety_result) -> torch.Tensor:
        """
        Determine which tokens to suppress when unsafe content is detected.

        Args:
            scores: Token logits for a single sequence [vocab_size]
            safety_result: The safety assessment result (unused for blocking strategy)

        Returns:
            Tensor of token indices to suppress (all tokens for blocking)
        """
        # Block strategy: suppress all tokens to force generation to stop
        return torch.arange(scores.size(0), device=scores.device)


class SafetyStoppingCriteria(StoppingCriteria):
    """
    [`StoppingCriteria`] that halts generation when unsafe content is detected.

    This provides a sequence-level safety check that can stop generation before
    unsafe content is returned to the user. It works as a final safety gate
    after token-level filtering by SafetyLogitsProcessor.

    Args:
        safety_checker ([`SafetyChecker`]):
            The safety checker to use for content evaluation.
        tokenizer ([`PreTrainedTokenizer`]):
            The tokenizer used for decoding sequences.
        safety_config ([`SafetyConfig`]):
            Configuration for safety checking.
        check_final_only (`bool`, *optional*, defaults to `False`):
            If True, only check safety on the final call (when all sequences are complete).
            If False, check safety on every call during generation.

    Examples:

    ```python
    >>> from transformers import AutoTokenizer, AutoModelForCausalLM
    >>> from transformers.generation.safety import SafetyStoppingCriteria, BasicToxicityChecker, SafetyConfig

    >>> # Initialize model and tokenizer
    >>> model = AutoModelForCausalLM.from_pretrained("gpt2")
    >>> tokenizer = AutoTokenizer.from_pretrained("gpt2")
    >>> tokenizer.pad_token = tokenizer.eos_token

    >>> # Create safety components
    >>> safety_config = SafetyConfig.create_default("moderate")
    >>> safety_checker = BasicToxicityChecker()
    >>> safety_stopping = SafetyStoppingCriteria(
    ...     safety_checker=safety_checker,
    ...     tokenizer=tokenizer,
    ...     safety_config=safety_config
    ... )

    >>> # Generate with safety stopping
    >>> inputs = tokenizer("Tell me about", return_tensors="pt")
    >>> outputs = model.generate(
    ...     **inputs,
    ...     stopping_criteria=[safety_stopping],
    ...     max_new_tokens=50,
    ...     do_sample=True
    ... )
    >>> generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    ```
    """

    def __init__(
        self, safety_checker: SafetyChecker, tokenizer, safety_config: SafetyConfig, check_final_only: bool = False
    ):
        """
        Initialize the SafetyStoppingCriteria.

        Args:
            safety_checker: The safety checker to use for content evaluation
            tokenizer: The tokenizer used for decoding sequences
            safety_config: Configuration for safety checking
            check_final_only: If True, only check when generation is complete

        Raises:
            ValueError: If safety_checker is None
        """
        if safety_checker is None:
            raise ValueError("safety_checker cannot be None")

        self.safety_checker = safety_checker
        self.tokenizer = tokenizer
        self.safety_config = safety_config
        self.check_final_only = check_final_only
        self._unsafe_sequence_hashes = set()  # Track unsafe sequences by content hash
        self._sequence_cache = OrderedDict()  # Cache safety results

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> torch.BoolTensor:
        """
        Check if generation should stop due to safety violations.

        Args:
            input_ids: Current sequences [batch_size, seq_len]
            scores: Token scores [batch_size, vocab_size]

        Returns:
            Boolean tensor indicating which sequences should stop [batch_size]
        """
        batch_size = input_ids.shape[0]

        # Initialize should_stop tensor
        should_stop = torch.zeros(batch_size, dtype=torch.bool, device=input_ids.device)

        # If check_final_only is True, skip safety checks during generation
        # This will be handled by other safety mechanisms or post-generation checks
        if self.check_final_only and not kwargs.get("is_final_call", False):
            return should_stop

        # Check each sequence for safety violations
        for i in range(batch_size):
            # Convert current sequence to text
            current_sequence = input_ids[i]
            current_text = self.tokenizer.decode(current_sequence, skip_special_tokens=True)

            # Create sequence hash for tracking
            sequence_hash = f"{len(current_text)}:{hash(current_text) % (10**8)}"  # Stable hash

            # Check if this sequence content is already known to be unsafe
            if sequence_hash in self._unsafe_sequence_hashes:
                should_stop[i] = True
                continue

            # Check cache first (using same cache key format as SafetyLogitsProcessor)
            cache_key = f"{len(current_text)}:{current_text[:100]}"
            if cache_key in self._sequence_cache:
                # Move to end for LRU behavior
                safety_result = self._sequence_cache.pop(cache_key)
                self._sequence_cache[cache_key] = safety_result
            else:
                # Perform safety check with error handling
                try:
                    safety_result = self.safety_checker.check_safety(current_text)
                except Exception as e:
                    logger.warning(f"Safety check failed during stopping criteria: {e}")
                    # Fail safe - assume unsafe if we can't check
                    safety_result = SafetyResult(
                        is_safe=False,
                        confidence=0.0,
                        violations=[SafetyViolation("unknown", 0.0, "high", "Safety check failed")],
                        metadata={"error": str(e)},
                    )

                # Cache the result with LRU behavior
                if len(self._sequence_cache) >= 100:
                    # Remove oldest entry
                    self._sequence_cache.popitem(last=False)
                self._sequence_cache[cache_key] = safety_result

            # If unsafe, mark sequence for stopping
            if not safety_result.is_safe:
                self._unsafe_sequence_hashes.add(sequence_hash)  # Track by content hash
                should_stop[i] = True

                # Log safety violation for debugging
                violation_categories = [v.category for v in safety_result.violations]
                logger.warning(
                    f"Generation stopped for sequence {i} due to safety violations: {violation_categories}. "
                    f"Text: {current_text[:100]}..."
                )

        return should_stop
