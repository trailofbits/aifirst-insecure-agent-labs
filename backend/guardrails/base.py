"""
Base guardrail interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseGuardrail(ABC):
    """Abstract base class for guardrails"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def check(self, text: str) -> Dict[str, Any]:
        """
        Check text for violations.

        Args:
            text: Text to check

        Returns:
            Dict with:
                - passed: bool (True if safe, False if violation)
                - reason: str (explanation if failed)
                - metadata: dict (additional info)
        """
        pass
