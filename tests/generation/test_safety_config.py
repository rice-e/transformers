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

from transformers.generation.safety import SafetyConfig


class TestSafetyConfig(unittest.TestCase):
    """Test suite for SafetyConfig."""

    def test_default_config(self):
        """Test SafetyConfig with default values."""
        config = SafetyConfig()

        # Check default values
        self.assertFalse(config.enabled)
        self.assertEqual(config.checkers, ["toxicity"])
        self.assertEqual(config.thresholds, {"toxicity": 0.7})
        self.assertEqual(config.toxicity_model, "unitary/toxic-bert")
        self.assertIsNone(config.device)
        self.assertFalse(config.return_violations)
        self.assertFalse(config.return_metadata)

    def test_custom_config(self):
        """Test SafetyConfig with custom values."""
        config = SafetyConfig(
            enabled=True,
            checkers=["toxicity"],
            thresholds={"toxicity": 0.8},
            toxicity_model="custom/model",
            device="cuda",
            return_violations=True,
            return_metadata=True,
        )

        self.assertTrue(config.enabled)
        self.assertEqual(config.checkers, ["toxicity"])
        self.assertEqual(config.thresholds, {"toxicity": 0.8})
        self.assertEqual(config.toxicity_model, "custom/model")
        self.assertEqual(config.device, "cuda")
        self.assertTrue(config.return_violations)
        self.assertTrue(config.return_metadata)

    def test_serialization_round_trip(self):
        """Test serialization and deserialization."""
        original_config = SafetyConfig(
            enabled=True,
            checkers=["toxicity"],
            thresholds={"toxicity": 0.6},
            toxicity_model="test/model",
            device="cpu",
            return_violations=True,
            return_metadata=False,
        )

        # Serialize to dict
        config_dict = original_config.to_dict()

        # Check dict contents
        expected_dict = {
            "enabled": True,
            "checkers": ["toxicity"],
            "thresholds": {"toxicity": 0.6},
            "toxicity_model": "test/model",
            "device": "cpu",
            "cache_size": 100,  # Default value
            "unsafe_hash_limit": 1000,  # Default value
            "sliding_window_size": 512,  # Default value
            "incremental_checking": True,  # Default value
            "prefix_lengths": [100, 75, 50],  # Default value
            "min_text_length_for_prefix": 50,  # Default value
            "return_violations": True,
            "return_metadata": False,
        }
        self.assertEqual(config_dict, expected_dict)

        # Deserialize from dict
        restored_config = SafetyConfig.from_dict(config_dict)

        # Check all attributes match
        self.assertEqual(restored_config.enabled, original_config.enabled)
        self.assertEqual(restored_config.checkers, original_config.checkers)
        self.assertEqual(restored_config.thresholds, original_config.thresholds)
        self.assertEqual(restored_config.toxicity_model, original_config.toxicity_model)
        self.assertEqual(restored_config.device, original_config.device)
        self.assertEqual(restored_config.return_violations, original_config.return_violations)
        self.assertEqual(restored_config.return_metadata, original_config.return_metadata)

    def test_validation_success(self):
        """Test validation with valid configuration."""
        # Valid default config
        config = SafetyConfig()
        config.validate()  # Should not raise

        # Valid custom config
        config = SafetyConfig(
            enabled=True, checkers=["toxicity"], thresholds={"toxicity": 0.5}, return_violations=True
        )
        config.validate()  # Should not raise

    def test_validation_enabled_type(self):
        """Test validation of enabled field."""
        config = SafetyConfig(enabled="true")  # Wrong type
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("enabled must be a boolean", str(context.exception))

    def test_validation_checkers_type(self):
        """Test validation of checkers field."""
        config = SafetyConfig(checkers="toxicity")  # Wrong type, should be list
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("checkers must be a list", str(context.exception))

    def test_validation_thresholds_type(self):
        """Test validation of thresholds field."""
        config = SafetyConfig(thresholds=0.7)  # Wrong type, should be dict
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("thresholds must be a dictionary", str(context.exception))

    def test_validation_threshold_values(self):
        """Test validation of threshold values."""
        # Threshold too high
        config = SafetyConfig(thresholds={"toxicity": 1.5})
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("thresholds must be numbers between 0.0 and 1.0", str(context.exception))

        # Threshold too low
        config = SafetyConfig(thresholds={"toxicity": -0.1})
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("thresholds must be numbers between 0.0 and 1.0", str(context.exception))

        # Valid boundary values
        config = SafetyConfig(thresholds={"toxicity": 0.0})
        config.validate()  # Should not raise

        config = SafetyConfig(thresholds={"toxicity": 1.0})
        config.validate()  # Should not raise

    def test_validation_unsupported_checkers(self):
        """Test validation with unsupported checkers."""
        config = SafetyConfig(checkers=["toxicity", "nonexistent"])
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("Unsupported checkers", str(context.exception))
        self.assertIn("nonexistent", str(context.exception))

    def test_validation_missing_thresholds(self):
        """Test validation with missing thresholds for configured checkers."""
        config = SafetyConfig(checkers=["toxicity"], thresholds={})
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("Missing threshold for checker: toxicity", str(context.exception))

    def test_validation_output_config_types(self):
        """Test validation of output configuration types."""
        # Wrong return_violations type
        config = SafetyConfig(return_violations="true")
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("return_violations must be a boolean", str(context.exception))

        # Wrong return_metadata type
        config = SafetyConfig(return_metadata=1)
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("return_metadata must be a boolean", str(context.exception))

    def test_get_checker_config(self):
        """Test get_checker_config method."""
        config = SafetyConfig(
            checkers=["toxicity"], thresholds={"toxicity": 0.8}, toxicity_model="test/model", device="cuda"
        )

        checker_config = config.get_checker_config("toxicity")
        expected_config = {"threshold": 0.8, "device": "cuda", "model_name": "test/model"}
        self.assertEqual(checker_config, expected_config)

    def test_get_checker_config_not_configured(self):
        """Test get_checker_config with unconfigured checker."""
        config = SafetyConfig(checkers=["toxicity"])

        with self.assertRaises(ValueError) as context:
            config.get_checker_config("bias")
        self.assertIn("Checker 'bias' not configured", str(context.exception))

    def test_is_checker_enabled(self):
        """Test is_checker_enabled method."""
        # Disabled config
        config = SafetyConfig(enabled=False, checkers=["toxicity"])
        self.assertFalse(config.is_checker_enabled("toxicity"))

        # Enabled config with configured checker
        config = SafetyConfig(enabled=True, checkers=["toxicity"])
        self.assertTrue(config.is_checker_enabled("toxicity"))

        # Enabled config with unconfigured checker
        self.assertFalse(config.is_checker_enabled("bias"))

    def test_create_default_moderate(self):
        """Test create_default with moderate level."""
        config = SafetyConfig.create_default("moderate")

        self.assertTrue(config.enabled)
        self.assertEqual(config.checkers, ["toxicity"])
        self.assertEqual(config.thresholds, {"toxicity": 0.7})
        self.assertFalse(config.return_violations)
        self.assertFalse(config.return_metadata)

    def test_create_default_strict(self):
        """Test create_default with strict level."""
        config = SafetyConfig.create_default("strict")

        self.assertTrue(config.enabled)
        self.assertEqual(config.checkers, ["toxicity"])
        self.assertEqual(config.thresholds, {"toxicity": 0.5})
        self.assertTrue(config.return_violations)
        self.assertTrue(config.return_metadata)

    def test_create_default_lenient(self):
        """Test create_default with lenient level."""
        config = SafetyConfig.create_default("lenient")

        self.assertTrue(config.enabled)
        self.assertEqual(config.checkers, ["toxicity"])
        self.assertEqual(config.thresholds, {"toxicity": 0.9})
        self.assertFalse(config.return_violations)
        self.assertFalse(config.return_metadata)

    def test_create_default_no_level(self):
        """Test create_default with no level specified (should default to moderate)."""
        config = SafetyConfig.create_default()

        # Should be same as moderate
        moderate_config = SafetyConfig.create_default("moderate")
        self.assertEqual(config.enabled, moderate_config.enabled)
        self.assertEqual(config.thresholds, moderate_config.thresholds)
        self.assertEqual(config.return_violations, moderate_config.return_violations)

    def test_create_default_invalid_level(self):
        """Test create_default with invalid safety level."""
        with self.assertRaises(ValueError) as context:
            SafetyConfig.create_default("invalid_level")

        self.assertIn("Unknown safety level: 'invalid_level'", str(context.exception))
        self.assertIn("Available levels:", str(context.exception))
        self.assertIn("strict", str(context.exception))
        self.assertIn("moderate", str(context.exception))
        self.assertIn("lenient", str(context.exception))

    def test_comprehensive_workflow(self):
        """Test a complete workflow with SafetyConfig."""
        # Create configuration
        config = SafetyConfig.create_default("strict")

        # Validate configuration
        config.validate()

        # Check if checker is enabled
        self.assertTrue(config.is_checker_enabled("toxicity"))

        # Get checker configuration
        checker_config = config.get_checker_config("toxicity")
        self.assertEqual(checker_config["threshold"], 0.5)
        self.assertEqual(checker_config["model_name"], "unitary/toxic-bert")

        # Serialize and deserialize
        config_dict = config.to_dict()
        restored_config = SafetyConfig.from_dict(config_dict)

        # Verify consistency
        self.assertEqual(config.enabled, restored_config.enabled)
        self.assertEqual(config.thresholds, restored_config.thresholds)

        # Validate restored configuration
        restored_config.validate()

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Empty checkers list
        config = SafetyConfig(enabled=True, checkers=[], thresholds={})
        config.validate()  # Should be valid

        # Multiple identical checkers (unusual but should work)
        config = SafetyConfig(checkers=["toxicity", "toxicity"], thresholds={"toxicity": 0.7})
        config.validate()  # Should be valid

        # Integer thresholds (should be accepted)
        config = SafetyConfig(thresholds={"toxicity": 1})  # Integer 1 instead of 1.0
        config.validate()  # Should be valid since isinstance(1, (int, float)) is True

    def test_immutable_defaults(self):
        """Test that default factory functions create independent instances."""
        config1 = SafetyConfig()
        config2 = SafetyConfig()

        # Modify one config's lists/dicts
        config1.checkers.append("new_checker")
        config1.thresholds["new_threshold"] = 0.5

        # Other config should be unaffected
        self.assertEqual(config2.checkers, ["toxicity"])
        self.assertEqual(config2.thresholds, {"toxicity": 0.7})

    def test_cache_size_configuration(self):
        """Test cache size configuration and validation."""
        # Test default cache size
        config = SafetyConfig()
        self.assertEqual(config.cache_size, 100)

        # Test custom cache size
        config = SafetyConfig(cache_size=50)
        self.assertEqual(config.cache_size, 50)

        # Test cache size validation - must be positive integer (now caught in __post_init__)
        with self.assertRaises(ValueError):
            SafetyConfig(cache_size=0)

        with self.assertRaises(ValueError):
            SafetyConfig(cache_size=-1)

        with self.assertRaises(TypeError):  # Type errors now caught immediately
            SafetyConfig(cache_size=3.14)

        with self.assertRaises(TypeError):  # Type errors now caught immediately
            SafetyConfig(cache_size="100")

    def test_unsafe_hash_limit_configuration(self):
        """Test unsafe hash limit configuration and validation."""
        # Test default unsafe hash limit
        config = SafetyConfig()
        self.assertEqual(config.unsafe_hash_limit, 1000)

        # Test custom unsafe hash limit
        config = SafetyConfig(unsafe_hash_limit=500)
        self.assertEqual(config.unsafe_hash_limit, 500)

        # Test unsafe hash limit validation - must be positive integer (now caught in __post_init__)
        with self.assertRaises(ValueError):
            SafetyConfig(unsafe_hash_limit=0)

        with self.assertRaises(ValueError):
            SafetyConfig(unsafe_hash_limit=-1)

        with self.assertRaises(TypeError):  # Type errors now caught immediately
            SafetyConfig(unsafe_hash_limit=2.5)

        with self.assertRaises(TypeError):  # Type errors now caught immediately
            SafetyConfig(unsafe_hash_limit="1000")

    def test_large_cache_size_warning(self):
        """Test warning for potentially inefficient cache sizes."""
        import warnings

        # Test cache size warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            SafetyConfig(cache_size=20000).validate()
            self.assertEqual(len(w), 1)
            self.assertTrue("cache_size > 10000" in str(w[0].message))

        # Test unsafe hash limit warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            SafetyConfig(unsafe_hash_limit=200000).validate()
            self.assertEqual(len(w), 1)
            self.assertTrue("unsafe_hash_limit > 100000" in str(w[0].message))

    def test_default_levels_include_cache_config(self):
        """Test that default safety levels include appropriate cache configurations."""
        strict_config = SafetyConfig.create_default("strict")
        self.assertEqual(strict_config.cache_size, 50)
        self.assertEqual(strict_config.unsafe_hash_limit, 500)

        moderate_config = SafetyConfig.create_default("moderate")
        self.assertEqual(moderate_config.cache_size, 100)
        self.assertEqual(moderate_config.unsafe_hash_limit, 1000)

        lenient_config = SafetyConfig.create_default("lenient")
        self.assertEqual(lenient_config.cache_size, 200)
        self.assertEqual(lenient_config.unsafe_hash_limit, 2000)

    def test_serialization_includes_cache_config(self):
        """Test that serialization includes cache configuration."""
        config = SafetyConfig(cache_size=75, unsafe_hash_limit=750)
        config_dict = config.to_dict()

        self.assertEqual(config_dict["cache_size"], 75)
        self.assertEqual(config_dict["unsafe_hash_limit"], 750)

        # Test round-trip
        restored_config = SafetyConfig.from_dict(config_dict)
        self.assertEqual(restored_config.cache_size, 75)
        self.assertEqual(restored_config.unsafe_hash_limit, 750)

    def test_sliding_window_configuration(self):
        """Test sliding window configuration parameters."""
        # Test default values
        config = SafetyConfig()
        self.assertEqual(config.sliding_window_size, 512)
        self.assertTrue(config.incremental_checking)

        # Test custom values
        config = SafetyConfig(sliding_window_size=256, incremental_checking=False)
        self.assertEqual(config.sliding_window_size, 256)
        self.assertFalse(config.incremental_checking)

    def test_sliding_window_validation(self):
        """Test validation of sliding window parameters."""
        # Test valid sliding window size
        config = SafetyConfig(sliding_window_size=100)
        config.validate()  # Should not raise

        # Test valid disabled sliding window
        config = SafetyConfig(sliding_window_size=-1)
        config.validate()  # Should not raise

        # Test invalid sliding window size (0)
        with self.assertRaises(ValueError) as context:
            SafetyConfig(sliding_window_size=0)
        self.assertIn("sliding_window_size must be a positive integer or -1 to disable", str(context.exception))

        # Test invalid sliding window size (negative but not -1)
        with self.assertRaises(ValueError) as context:
            SafetyConfig(sliding_window_size=-5)
        self.assertIn("sliding_window_size must be a positive integer or -1 to disable", str(context.exception))

        # Test invalid incremental_checking type
        with self.assertRaises(TypeError) as context:
            SafetyConfig(incremental_checking="true")
        self.assertIn("incremental_checking must be a boolean", str(context.exception))

    def test_sliding_window_serialization(self):
        """Test serialization of sliding window parameters."""
        config = SafetyConfig(
            sliding_window_size=256, incremental_checking=False, cache_size=50, unsafe_hash_limit=500
        )

        # Test to_dict includes sliding window parameters
        config_dict = config.to_dict()
        self.assertEqual(config_dict["sliding_window_size"], 256)
        self.assertEqual(config_dict["incremental_checking"], False)

        # Test round-trip serialization
        restored_config = SafetyConfig.from_dict(config_dict)
        self.assertEqual(restored_config.sliding_window_size, 256)
        self.assertFalse(restored_config.incremental_checking)
        self.assertEqual(restored_config.cache_size, 50)
        self.assertEqual(restored_config.unsafe_hash_limit, 500)

    def test_sliding_window_default_levels(self):
        """Test that default safety levels work with sliding window parameters."""
        # All default levels should have sliding window parameters
        for level in ["strict", "moderate", "lenient"]:
            config = SafetyConfig.create_default(level)
            self.assertEqual(config.sliding_window_size, 512)  # Default value
            self.assertTrue(config.incremental_checking)  # Default value

    def test_sliding_window_edge_cases(self):
        """Test edge cases for sliding window configuration."""
        # Test very large sliding window size
        config = SafetyConfig(sliding_window_size=10000)
        config.validate()  # Should be valid

        # Test minimum sliding window size
        config = SafetyConfig(sliding_window_size=1)
        config.validate()  # Should be valid

        # Test both sliding window and incremental checking disabled
        config = SafetyConfig(sliding_window_size=-1, incremental_checking=False)
        config.validate()  # Should be valid
