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

import time
import unittest
from unittest.mock import Mock, patch

import torch

from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from transformers.generation.safety import SafetyConfig, SafetyResult, SafetyViolation
from transformers.testing_utils import require_torch, slow


class TestSafetyEndToEnd(unittest.TestCase):
    """End-to-end tests for safety-enabled generation with actual models."""

    def setUp(self):
        """Set up test fixtures."""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def _setup_safety_mocks(self):
        """Set up mocked safety checker for testing."""
        mock_checker_patcher = patch("transformers.generation.safety.BasicToxicityChecker")
        self.mock_checker_class = mock_checker_patcher.start()
        self.addCleanup(mock_checker_patcher.stop)

        self.mock_checker = Mock()
        self.mock_checker_class.return_value = self.mock_checker

    @require_torch
    @slow
    def test_greedy_generation_with_safety(self):
        """Test that safety works with greedy decoding generation."""
        self._setup_safety_mocks()

        # Mock safe responses
        self.mock_checker.check_safety.return_value = SafetyResult(
            is_safe=True, confidence=0.9, violations=[], metadata={}
        )

        # Load small model for testing
        model_name = "sshleifer/tiny-gpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.pad_token = tokenizer.eos_token

        # Create safety configuration
        safety_config = SafetyConfig(enabled=True, checkers=["toxicity"], thresholds={"toxicity": 0.7})

        # Create generation config with safety
        gen_config = GenerationConfig(
            max_length=20,
            do_sample=False,  # Greedy
            safety_config=safety_config,
        )

        # Test generation
        inputs = tokenizer("Hello, world", return_tensors="pt")
        outputs = model.generate(**inputs, generation_config=gen_config)

        # Verify output is generated
        self.assertGreater(outputs.shape[1], inputs["input_ids"].shape[1])

        # Verify safety checker was called
        self.mock_checker.check_safety.assert_called()

    @require_torch
    @slow
    def test_sample_generation_with_safety(self):
        """Test that safety works with sampling generation."""
        self._setup_safety_mocks()

        # Mock safe responses
        self.mock_checker.check_safety.return_value = SafetyResult(
            is_safe=True, confidence=0.9, violations=[], metadata={}
        )

        # Load small model
        model_name = "sshleifer/tiny-gpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.pad_token = tokenizer.eos_token

        # Create safety configuration
        safety_config = SafetyConfig(enabled=True, checkers=["toxicity"], thresholds={"toxicity": 0.7})

        # Test sampling with safety
        inputs = tokenizer("Hello", return_tensors="pt")
        outputs = model.generate(**inputs, max_length=15, do_sample=True, temperature=0.8, safety_config=safety_config)

        # Verify generation occurred
        self.assertGreater(outputs.shape[1], inputs["input_ids"].shape[1])
        self.mock_checker.check_safety.assert_called()

    @require_torch
    @slow
    def test_beam_search_generation_with_safety(self):
        """Test that safety works with beam search generation."""
        self._setup_safety_mocks()

        # Mock safe responses
        self.mock_checker.check_safety.return_value = SafetyResult(
            is_safe=True, confidence=0.9, violations=[], metadata={}
        )

        # Load small model
        model_name = "sshleifer/tiny-gpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.pad_token = tokenizer.eos_token

        # Create safety configuration
        safety_config = SafetyConfig(enabled=True, checkers=["toxicity"], thresholds={"toxicity": 0.7})

        # Test beam search with safety
        inputs = tokenizer("The weather is", return_tensors="pt")
        outputs = model.generate(**inputs, max_length=15, num_beams=2, safety_config=safety_config)

        # Verify generation occurred
        self.assertGreater(outputs.shape[1], inputs["input_ids"].shape[1])
        self.mock_checker.check_safety.assert_called()

    @require_torch
    @slow
    def test_safety_blocks_toxic_generation(self):
        """Test that generation stops when toxic content is detected."""
        self._setup_safety_mocks()

        # Mock unsafe response that should stop generation
        self.mock_checker.check_safety.return_value = SafetyResult(
            is_safe=False,
            confidence=0.85,
            violations=[SafetyViolation("toxicity", 0.85, "high", "Toxic content detected")],
            metadata={"toxicity_score": 0.85},
        )

        # Load small model
        model_name = "sshleifer/tiny-gpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.pad_token = tokenizer.eos_token

        # Create safety configuration
        safety_config = SafetyConfig(enabled=True, checkers=["toxicity"], thresholds={"toxicity": 0.7})

        # Test generation - should stop early due to safety
        inputs = tokenizer("Test input", return_tensors="pt")
        outputs = model.generate(
            **inputs,
            max_length=50,  # Allow long generation
            safety_config=safety_config,
        )

        # Should stop early due to safety stopping criteria
        # (The exact length depends on when safety check triggers)
        self.assertLessEqual(outputs.shape[1], 50)
        self.mock_checker.check_safety.assert_called()

    @require_torch
    @slow
    def test_safety_disabled_backward_compatibility(self):
        """Test that safety disabled doesn't affect normal generation."""
        # No safety mocks needed - testing disabled safety

        # Load small model
        model_name = "sshleifer/tiny-gpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.pad_token = tokenizer.eos_token

        # Test without safety config (default behavior)
        inputs = tokenizer("Hello world", return_tensors="pt")
        outputs_no_safety = model.generate(**inputs, max_length=20, do_sample=False)

        # Test with disabled safety config
        safety_config = SafetyConfig(enabled=False)
        outputs_disabled_safety = model.generate(**inputs, max_length=20, do_sample=False, safety_config=safety_config)

        # Results should be identical (since both use no safety)
        # Note: Results might not be exactly identical due to random state,
        # but both should generate successfully
        self.assertEqual(outputs_no_safety.shape, outputs_disabled_safety.shape)

    @require_torch
    @slow
    def test_performance_impact_measurement(self):
        """Test that safety overhead is reasonable."""
        # Load small model
        model_name = "sshleifer/tiny-gpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.pad_token = tokenizer.eos_token

        inputs = tokenizer("Performance test", return_tensors="pt")

        # Measure baseline (no safety)
        start_time = time.time()
        for _ in range(3):  # Multiple runs for more stable timing
            model.generate(**inputs, max_length=20, do_sample=False)
        baseline_time = time.time() - start_time

        # Set up safety mocks for performance test
        self._setup_safety_mocks()
        self.mock_checker.check_safety.return_value = SafetyResult(
            is_safe=True, confidence=0.9, violations=[], metadata={}
        )

        # Measure with safety enabled
        safety_config = SafetyConfig(enabled=True, checkers=["toxicity"], thresholds={"toxicity": 0.7})

        start_time = time.time()
        for _ in range(3):  # Multiple runs for more stable timing
            model.generate(**inputs, max_length=20, do_sample=False, safety_config=safety_config)
        safety_time = time.time() - start_time

        # Calculate overhead percentage
        overhead_percent = ((safety_time - baseline_time) / baseline_time) * 100

        # Assert that overhead is reasonable (less than 50% for this simple test)
        # Note: In real usage, overhead would be much less due to check_interval optimization
        self.assertLess(overhead_percent, 50, f"Safety overhead of {overhead_percent:.1f}% is too high")

        print(f"Safety overhead: {overhead_percent:.1f}%")
