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

from typing import Optional

from ...utils import is_torch_available
from .base import SafetyChecker
from .configuration import SafetyConfig


def create_safety_checker_from_config(config: SafetyConfig, checker_type: str = "toxicity") -> Optional[SafetyChecker]:
    """
    Create a safety checker instance from configuration.

    Args:
        config (`SafetyConfig`): Configuration object containing checker parameters.
        checker_type (`str`, *optional*, defaults to `"toxicity"`): Type of checker to create.

    Returns:
        `Optional[SafetyChecker]`: Safety checker instance, or None if not enabled or torch unavailable.

    Raises:
        ValueError: If the checker type is not supported or not configured.
        ImportError: If required dependencies are not available.

    Example:
    ```python
    from transformers.generation.safety import SafetyConfig, create_safety_checker_from_config

    config = SafetyConfig.create_default("strict")
    checker = create_safety_checker_from_config(config, "toxicity")

    if checker:
        result = checker.check_safety("Some text to check")
        print(f"Is safe: {result.is_safe}")
    ```
    """
    if not config.enabled:
        return None

    if not config.is_checker_enabled(checker_type):
        return None

    if not is_torch_available():
        raise ImportError("PyTorch is required to use safety checkers. Please install PyTorch: pip install torch")

    if checker_type == "toxicity":
        from .checkers import BasicToxicityChecker

        checker_config = config.get_checker_config(checker_type)
        return BasicToxicityChecker(**checker_config)
    else:
        raise ValueError(f"Unsupported checker type: {checker_type}")


def validate_safety_config(config: SafetyConfig) -> bool:
    """
    Validate a safety configuration and return whether it's valid.

    Args:
        config (`SafetyConfig`): Configuration to validate.

    Returns:
        `bool`: True if configuration is valid, False otherwise.

    Example:
    ```python
    config = SafetyConfig(enabled=True, thresholds={"toxicity": 0.5})
    if validate_safety_config(config):
        print("Configuration is valid")
    ```
    """
    try:
        config.validate()
        return True
    except (ValueError, TypeError):
        return False
