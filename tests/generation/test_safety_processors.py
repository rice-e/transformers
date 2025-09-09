# coding=utf-8
# Copyright 2024 The HuggingFace Inc. team.
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

import unittest
from unittest.mock import Mock

import torch

from transformers.generation.safety import SafetyConfig, SafetyResult, SafetyViolation
from transformers.generation.safety.processors import SafetyLogitsProcessor, SafetyStoppingCriteria
from transformers.testing_utils import require_torch


@require_torch
class TestSafetyLogitsProcessor(unittest.TestCase):
    """Test SafetyLogitsProcessor functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock safety checker
        self.mock_checker = Mock()
        self.mock_checker.check_safety.return_value = SafetyResult(
            is_safe=True, confidence=0.9, violations=[], metadata={}
        )

        # Mock tokenizer
        self.mock_tokenizer = Mock()
        self.mock_tokenizer.decode.return_value = "test text"

        # Safety config
        self.safety_config = SafetyConfig(enabled=True, checkers=["toxicity"], thresholds={"toxicity": 0.7})

    def test_safe_content_no_suppression(self):
        """Test that safe content passes through without modification."""
        processor = SafetyLogitsProcessor(
            safety_checker=self.mock_checker, tokenizer=self.mock_tokenizer, safety_config=self.safety_config
        )

        # Test safe content (mock already returns safe result)
        input_ids = torch.tensor([[1, 2, 3, 4]])
        scores = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0]])
        original_scores = scores.clone()

        # Process
        modified_scores = processor(input_ids, scores)

        # Scores should be unchanged for safe content
        torch.testing.assert_close(modified_scores, original_scores)

        # Verify safety check was called
        self.mock_checker.check_safety.assert_called_once()

    def test_unsafe_content_blocking(self):
        """Test that unsafe content gets all tokens suppressed (blocking)."""
        processor = SafetyLogitsProcessor(
            safety_checker=self.mock_checker, tokenizer=self.mock_tokenizer, safety_config=self.safety_config
        )

        # Mock unsafe result
        self.mock_checker.check_safety.return_value = SafetyResult(
            is_safe=False, confidence=0.8, violations=[SafetyViolation("toxicity", 0.8, "high")], metadata={}
        )

        # Test data
        input_ids = torch.tensor([[1, 2, 3, 4]])
        scores = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0]])
        vocab_size = scores.shape[-1]

        # Process
        modified_scores = processor(input_ids, scores)

        # All tokens should be suppressed (blocking strategy)
        for i in range(vocab_size):
            self.assertEqual(modified_scores[0, i], float("-inf"))

    def test_check_interval(self):
        """Test that safety checking respects check_interval parameter."""
        processor = SafetyLogitsProcessor(
            safety_checker=self.mock_checker,
            tokenizer=self.mock_tokenizer,
            safety_config=self.safety_config,
            check_interval=3,  # Only check every 3rd call
        )

        input_ids = torch.tensor([[1, 2, 3, 4]])
        scores = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0]])

        # First call (step 1) - no check
        processor(input_ids, scores)
        self.assertEqual(self.mock_checker.check_safety.call_count, 0)

        # Second call (step 2) - no check
        processor(input_ids, scores)
        self.assertEqual(self.mock_checker.check_safety.call_count, 0)

        # Third call (step 3) - check should happen
        processor(input_ids, scores)
        self.assertEqual(self.mock_checker.check_safety.call_count, 1)

    def test_batch_processing(self):
        """Test that processor handles batched inputs correctly."""
        processor = SafetyLogitsProcessor(
            safety_checker=self.mock_checker, tokenizer=self.mock_tokenizer, safety_config=self.safety_config
        )

        # Mock mixed safety results for batch
        def mock_check_safety(text):
            if "unsafe" in text:
                return SafetyResult(
                    is_safe=False, confidence=0.8, violations=[SafetyViolation("toxicity", 0.8, "high")], metadata={}
                )
            else:
                return SafetyResult(is_safe=True, confidence=0.9, violations=[], metadata={})

        self.mock_checker.check_safety.side_effect = mock_check_safety

        # Mock tokenizer to return different text for different sequences
        def mock_decode(sequence, skip_special_tokens=True):
            if torch.equal(sequence, torch.tensor([1, 2, 3, 4])):
                return "safe text"
            else:
                return "unsafe text"

        self.mock_tokenizer.decode.side_effect = mock_decode

        # Batch with mixed safety
        input_ids = torch.tensor([[1, 2, 3, 4], [5, 6, 7, 8]])  # [safe, unsafe]
        scores = torch.tensor([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]])

        # Process
        modified_scores = processor(input_ids, scores)

        # First sequence (safe) should be unchanged
        torch.testing.assert_close(modified_scores[0], scores[0])

        # Second sequence (unsafe) should be suppressed
        for i in range(scores.shape[-1]):
            self.assertEqual(modified_scores[1, i], float("-inf"))

    def test_safety_check_failure(self):
        """Test graceful handling when safety check fails."""
        processor = SafetyLogitsProcessor(
            safety_checker=self.mock_checker, tokenizer=self.mock_tokenizer, safety_config=self.safety_config
        )

        # Mock safety checker to raise exception
        self.mock_checker.check_safety.side_effect = Exception("Safety check failed")

        input_ids = torch.tensor([[1, 2, 3, 4]])
        scores = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0]])

        # Process - should not raise, should assume unsafe and suppress
        modified_scores = processor(input_ids, scores)

        # Should suppress all tokens when safety check fails (fail-safe behavior)
        for i in range(scores.shape[-1]):
            self.assertEqual(modified_scores[0, i], float("-inf"))


@require_torch
class TestSafetyStoppingCriteria(unittest.TestCase):
    """Test SafetyStoppingCriteria functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock safety checker
        self.mock_checker = Mock()
        self.mock_checker.check_safety.return_value = SafetyResult(
            is_safe=True, confidence=0.9, violations=[], metadata={}
        )

        # Mock tokenizer
        self.mock_tokenizer = Mock()
        self.mock_tokenizer.decode.return_value = "test text"

        # Safety config
        self.safety_config = SafetyConfig(enabled=True, checkers=["toxicity"], thresholds={"toxicity": 0.7})

    def test_safe_content_continue_generation(self):
        """Test that safe content allows generation to continue."""
        criteria = SafetyStoppingCriteria(
            safety_checker=self.mock_checker, tokenizer=self.mock_tokenizer, safety_config=self.safety_config
        )

        input_ids = torch.tensor([[1, 2, 3, 4]])
        scores = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0]])

        # Call stopping criteria
        should_stop = criteria(input_ids, scores)

        # Should not stop for safe content
        self.assertFalse(should_stop[0])
        self.mock_checker.check_safety.assert_called_once()

    def test_unsafe_content_stop_generation(self):
        """Test that unsafe content stops generation."""
        criteria = SafetyStoppingCriteria(
            safety_checker=self.mock_checker, tokenizer=self.mock_tokenizer, safety_config=self.safety_config
        )

        # Mock unsafe result
        self.mock_checker.check_safety.return_value = SafetyResult(
            is_safe=False, confidence=0.8, violations=[SafetyViolation("toxicity", 0.8, "high")], metadata={}
        )

        input_ids = torch.tensor([[1, 2, 3, 4]])
        scores = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0]])

        # Call stopping criteria
        should_stop = criteria(input_ids, scores)

        # Should stop for unsafe content
        self.assertTrue(should_stop[0])

    def test_check_final_only_mode(self):
        """Test check_final_only parameter functionality."""
        criteria = SafetyStoppingCriteria(
            safety_checker=self.mock_checker,
            tokenizer=self.mock_tokenizer,
            safety_config=self.safety_config,
            check_final_only=True,
        )

        input_ids = torch.tensor([[1, 2, 3, 4]])
        scores = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0]])

        # Call without is_final_call - should not check
        should_stop = criteria(input_ids, scores)
        self.assertFalse(should_stop[0])
        self.assertEqual(self.mock_checker.check_safety.call_count, 0)

        # Call with is_final_call=True - should check
        should_stop = criteria(input_ids, scores, is_final_call=True)
        self.assertFalse(should_stop[0])  # Safe content
        self.assertEqual(self.mock_checker.check_safety.call_count, 1)

    def test_batch_stopping_criteria(self):
        """Test stopping criteria with batched inputs."""
        criteria = SafetyStoppingCriteria(
            safety_checker=self.mock_checker, tokenizer=self.mock_tokenizer, safety_config=self.safety_config
        )

        # Mock mixed safety results
        def mock_check_safety(text):
            if "unsafe" in text:
                return SafetyResult(
                    is_safe=False, confidence=0.8, violations=[SafetyViolation("toxicity", 0.8, "high")], metadata={}
                )
            else:
                return SafetyResult(is_safe=True, confidence=0.9, violations=[], metadata={})

        self.mock_checker.check_safety.side_effect = mock_check_safety

        # Mock tokenizer for batch
        def mock_decode(sequence, skip_special_tokens=True):
            if torch.equal(sequence, torch.tensor([1, 2, 3, 4])):
                return "safe text"
            else:
                return "unsafe text"

        self.mock_tokenizer.decode.side_effect = mock_decode

        # Batch input
        input_ids = torch.tensor([[1, 2, 3, 4], [5, 6, 7, 8]])  # [safe, unsafe]
        scores = torch.tensor([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]])

        # Call stopping criteria
        should_stop = criteria(input_ids, scores)

        # First sequence (safe) should continue, second (unsafe) should stop
        self.assertFalse(should_stop[0])
        self.assertTrue(should_stop[1])

    def test_none_safety_checker_raises(self):
        """Test that None safety_checker raises ValueError."""
        with self.assertRaises(ValueError):
            SafetyStoppingCriteria(
                safety_checker=None, tokenizer=self.mock_tokenizer, safety_config=self.safety_config
            )


if __name__ == "__main__":
    unittest.main()
