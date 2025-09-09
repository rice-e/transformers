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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Union


@dataclass
class SafetyViolation:
    """
    Represents a single safety violation detected in text.

    Args:
        category (`str`):
            The category of safety violation (e.g., "toxicity", "bias", "pii").
        confidence (`float`):
            Confidence score for the violation detection, ranging from 0.0 to 1.0.
        severity (`str`, *optional*, defaults to `"medium"`):
            Severity level of the violation. One of "low", "medium", "high", "critical".
        description (`str`, *optional*, defaults to `""`):
            Human-readable description of the violation.
        span (`tuple[int, int]`, *optional*):
            Character span in the original text where the violation occurs, if applicable.
    """

    category: str
    confidence: float
    severity: str = "medium"
    description: str = ""
    span: Optional[tuple[int, int]] = None


@dataclass
class SafetyResult:
    """
    Result of a safety checking operation.

    Args:
        is_safe (`bool`):
            Whether the checked text is considered safe overall.
        confidence (`float`):
            Overall confidence in the safety assessment, ranging from 0.0 to 1.0.
        violations (`List[SafetyViolation]`):
            List of safety violations detected in the text.
        metadata (`Dict[str, Any]`):
            Additional checker-specific information and context.
    """

    is_safe: bool
    confidence: float
    violations: list[SafetyViolation]
    metadata: dict[str, Any]


class SafetyChecker(ABC):
    """
    Abstract base class for all safety checkers.

    Safety checkers are responsible for analyzing text content and detecting various types of safety violations
    such as toxicity, bias, personally identifiable information, or other harmful content.
    """

    @abstractmethod
    def check_safety(self, text: Union[str, list[str]], **kwargs) -> Union[SafetyResult, list[SafetyResult]]:
        """
        Check text(s) for safety violations.

        Args:
            text (`Union[str, List[str]]`):
                Single text string or list of texts to check for safety violations.
            **kwargs:
                Additional checker-specific parameters.

        Returns:
            `Union[SafetyResult, List[SafetyResult]]`:
                SafetyResult for single text input, List[SafetyResult] for multiple texts.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is an abstract class. Only classes inheriting this class can be called."
        )

    @property
    @abstractmethod
    def supported_categories(self) -> list[str]:
        """
        Return list of safety categories this checker supports.

        Returns:
            `List[str]`: List of supported safety categories (e.g., ["toxicity", "bias"]).
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is an abstract class. Only classes inheriting this class can be called."
        )

    def get_config(self) -> dict[str, Any]:
        """
        Return checker configuration for serialization.

        Returns:
            `Dict[str, Any]`: Dictionary containing the checker's configuration parameters.
        """
        return {"checker_type": self.__class__.__name__}
