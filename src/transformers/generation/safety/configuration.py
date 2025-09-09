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

import warnings
from dataclasses import dataclass, field
from typing import Any, Optional


# Constants for validation warnings
WARNING_CACHE_SIZE_LIMIT = 10000
WARNING_UNSAFE_HASH_LIMIT = 100000


@dataclass
class SafetyConfig:
    """
    Configuration for safety checking in text generation.

    This class manages all safety-related parameters including which checkers to use,
    their thresholds, model configurations, and output preferences.

    Args:
        enabled (`bool`, *optional*, defaults to `False`):
            Whether safety checking is enabled.
        checkers (`List[str]`, *optional*, defaults to `["toxicity"]`):
            List of safety checkers to use (e.g., ["toxicity", "bias"]).
        thresholds (`Dict[str, float]`, *optional*, defaults to `{"toxicity": 0.7}`):
            Threshold values for each checker. Values should be between 0.0 and 1.0.
        toxicity_model (`str`, *optional*, defaults to `"unitary/toxic-bert"`):
            The model to use for toxicity detection.
        device (`str`, *optional*):
            Device to run models on. If None, automatically selects CUDA if available.
        cache_size (`int`, *optional*, defaults to `100`):
            Maximum number of safety check results to cache. Larger values use more memory
            but can improve performance for repetitive content.
        unsafe_hash_limit (`int`, *optional*, defaults to `1000`):
            Maximum number of unsafe sequence hashes to remember. Prevents memory leaks
            in long-running applications with many unsafe sequences.
        sliding_window_size (`int`, *optional*, defaults to `512`):
            Maximum number of tokens to check for safety instead of the full sequence.
            Helps improve performance for long sequences while maintaining safety effectiveness.
            Set to -1 to disable sliding window (check full sequence).
        incremental_checking (`bool`, *optional*, defaults to `True`):
            Whether to enable incremental safety checking that tracks state between checks
            to avoid redundant processing. Improves performance for long generations.
        return_violations (`bool`, *optional*, defaults to `False`):
            Whether to return detailed violation information in results.
        return_metadata (`bool`, *optional*, defaults to `False`):
            Whether to return additional metadata in results.

    Examples:
    ```python
    # Basic configuration
    config = SafetyConfig(enabled=True)

    # Strict toxicity checking
    config = SafetyConfig(
        enabled=True,
        thresholds={"toxicity": 0.5},
        return_violations=True
    )

    # Custom model configuration
    config = SafetyConfig(
        enabled=True,
        toxicity_model="custom/toxicity-model",
        device="cuda"
    )
    ```
    """

    # Checker configuration
    enabled: bool = False
    checkers: list[str] = field(default_factory=lambda: ["toxicity"])
    thresholds: dict[str, float] = field(default_factory=lambda: {"toxicity": 0.7})

    # Model configuration
    toxicity_model: str = "unitary/toxic-bert"
    device: Optional[str] = None

    # Performance configuration
    cache_size: int = 100
    unsafe_hash_limit: int = 1000
    sliding_window_size: int = 512
    incremental_checking: bool = True
    prefix_lengths: list[int] = field(default_factory=lambda: [100, 75, 50])
    min_text_length_for_prefix: int = 50

    # Output configuration
    return_violations: bool = False
    return_metadata: bool = False

    def __post_init__(self):
        """Perform immediate validation after initialization."""
        # Basic type checking for critical parameters
        if not isinstance(self.cache_size, int):
            raise TypeError(f"cache_size must be an integer, got {type(self.cache_size).__name__}")

        if not isinstance(self.unsafe_hash_limit, int):
            raise TypeError(f"unsafe_hash_limit must be an integer, got {type(self.unsafe_hash_limit).__name__}")

        # Range validation
        if self.cache_size < 1:
            raise ValueError("cache_size must be a positive integer")

        if self.unsafe_hash_limit < 1:
            raise ValueError("unsafe_hash_limit must be a positive integer")

        # Validate sliding window size
        if not isinstance(self.sliding_window_size, int):
            raise TypeError(f"sliding_window_size must be an integer, got {type(self.sliding_window_size).__name__}")

        if self.sliding_window_size < -1 or self.sliding_window_size == 0:
            raise ValueError("sliding_window_size must be a positive integer or -1 to disable")

        # Validate incremental checking
        if not isinstance(self.incremental_checking, bool):
            raise TypeError(f"incremental_checking must be a boolean, got {type(self.incremental_checking).__name__}")

        # Validate prefix configuration
        if not isinstance(self.prefix_lengths, list):
            raise TypeError(f"prefix_lengths must be a list, got {type(self.prefix_lengths).__name__}")

        if not all(isinstance(length, int) and length > 0 for length in self.prefix_lengths):
            raise ValueError("All prefix_lengths must be positive integers")

        if not isinstance(self.min_text_length_for_prefix, int) or self.min_text_length_for_prefix < 1:
            raise ValueError("min_text_length_for_prefix must be a positive integer")

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for serialization.

        Returns:
            `Dict[str, Any]`: Dictionary representation of the configuration.
        """
        return {
            "enabled": self.enabled,
            "checkers": self.checkers,
            "thresholds": self.thresholds,
            "toxicity_model": self.toxicity_model,
            "device": self.device,
            "cache_size": self.cache_size,
            "unsafe_hash_limit": self.unsafe_hash_limit,
            "sliding_window_size": self.sliding_window_size,
            "incremental_checking": self.incremental_checking,
            "prefix_lengths": self.prefix_lengths,
            "min_text_length_for_prefix": self.min_text_length_for_prefix,
            "return_violations": self.return_violations,
            "return_metadata": self.return_metadata,
        }

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "SafetyConfig":
        """
        Create SafetyConfig from dictionary.

        Args:
            config_dict (`Dict[str, Any]`): Dictionary containing configuration parameters.

        Returns:
            `SafetyConfig`: Instance created from the dictionary.
        """
        return cls(**config_dict)

    def validate(self) -> None:
        """
        Validate configuration parameters.

        Raises:
            ValueError: If any configuration parameter is invalid.
        """
        # Validate enabled is boolean
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be a boolean")

        # Validate checkers is a list
        if not isinstance(self.checkers, list):
            raise ValueError("checkers must be a list")

        # Validate thresholds
        if not isinstance(self.thresholds, dict):
            raise ValueError("thresholds must be a dictionary")

        if not all(isinstance(t, (int, float)) and 0.0 <= t <= 1.0 for t in self.thresholds.values()):
            raise ValueError("All thresholds must be numbers between 0.0 and 1.0")

        # Validate supported checkers
        supported_checkers = {"toxicity"}  # Expandable in future phases
        if not all(c in supported_checkers for c in self.checkers):
            unsupported = set(self.checkers) - supported_checkers
            raise ValueError(f"Unsupported checkers: {unsupported}")

        # Validate consistency between checkers and thresholds
        for checker in self.checkers:
            if checker not in self.thresholds:
                raise ValueError(f"Missing threshold for checker: {checker}")

        # Warn about potentially inefficient configurations (validation done in __post_init__)
        if self.cache_size > WARNING_CACHE_SIZE_LIMIT:
            warnings.warn(f"cache_size > {WARNING_CACHE_SIZE_LIMIT} may use excessive memory", UserWarning)

        if self.unsafe_hash_limit > WARNING_UNSAFE_HASH_LIMIT:
            warnings.warn(f"unsafe_hash_limit > {WARNING_UNSAFE_HASH_LIMIT} may use excessive memory", UserWarning)

        # Validate output configuration
        if not isinstance(self.return_violations, bool):
            raise ValueError("return_violations must be a boolean")

        if not isinstance(self.return_metadata, bool):
            raise ValueError("return_metadata must be a boolean")

    def get_checker_config(self, checker_name: str) -> dict[str, Any]:
        """
        Get configuration for a specific checker.

        Args:
            checker_name (`str`): Name of the checker to get configuration for.

        Returns:
            `Dict[str, Any]`: Configuration parameters for the specified checker.

        Raises:
            ValueError: If the checker is not configured.
        """
        if checker_name not in self.checkers:
            raise ValueError(f"Checker '{checker_name}' not configured")

        config = {"threshold": self.thresholds.get(checker_name, 0.7), "device": self.device}

        # Add checker-specific configuration
        if checker_name == "toxicity":
            config["model_name"] = self.toxicity_model

        return config

    def is_checker_enabled(self, checker_name: str) -> bool:
        """
        Check if a specific checker is enabled.

        Args:
            checker_name (`str`): Name of the checker to check.

        Returns:
            `bool`: True if the checker is enabled, False otherwise.
        """
        return self.enabled and checker_name in self.checkers

    @classmethod
    def create_default(cls, level: str = "moderate") -> "SafetyConfig":
        """
        Create a default configuration with predefined safety levels.

        Args:
            level (`str`, *optional*, defaults to `"moderate"`):
                Safety level. One of "strict", "moderate", or "lenient".

        Returns:
            `SafetyConfig`: Pre-configured SafetyConfig instance.

        Raises:
            ValueError: If the safety level is not recognized.

        Examples:
        ```python
        # Moderate safety (default)
        config = SafetyConfig.create_default()

        # Strict safety
        config = SafetyConfig.create_default("strict")

        # Lenient safety
        config = SafetyConfig.create_default("lenient")
        ```
        """
        configs = {
            "strict": {
                "threshold": 0.5,
                "return_violations": True,
                "return_metadata": True,
                "cache_size": 50,
                "unsafe_hash_limit": 500,
            },
            "moderate": {
                "threshold": 0.7,
                "return_violations": False,
                "return_metadata": False,
                "cache_size": 100,
                "unsafe_hash_limit": 1000,
            },
            "lenient": {
                "threshold": 0.9,
                "return_violations": False,
                "return_metadata": False,
                "cache_size": 200,
                "unsafe_hash_limit": 2000,
            },
        }

        if level not in configs:
            available_levels = list(configs.keys())
            raise ValueError(f"Unknown safety level: '{level}'. Available levels: {available_levels}")

        level_config = configs[level]
        return cls(
            enabled=True,
            thresholds={"toxicity": level_config["threshold"]},
            cache_size=level_config["cache_size"],
            unsafe_hash_limit=level_config["unsafe_hash_limit"],
            return_violations=level_config["return_violations"],
            return_metadata=level_config["return_metadata"],
        )
