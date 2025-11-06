"""
Main injection detector that combines multiple guardrails
"""
import logging
from typing import Dict, Any, List

from guardrails.patterns import PatternGuardrail

logger = logging.getLogger(__name__)


class InjectionDetector:
    """
    Main detector that orchestrates multiple guardrails
    """

    def __init__(self, use_patterns: bool = True, additional_patterns: List[str] = None):
        self.guardrails = []

        if use_patterns:
            self.guardrails.append(PatternGuardrail(additional_patterns=additional_patterns))

        logger.info(f"Initialized InjectionDetector with {len(self.guardrails)} guardrail(s)")

    def check_input(self, text: str) -> Dict[str, Any]:
        """Check user input for injections"""
        return self._check(text, "input")

    def check_output(self, text: str) -> Dict[str, Any]:
        """Check agent output for injections"""
        return self._check(text, "output")

    def check_content(self, text: str) -> Dict[str, Any]:
        """Check retrieved content for injections"""
        return self._check(text, "content")

    def _check(self, text: str, check_type: str) -> Dict[str, Any]:
        """
        Run all guardrails on text.

        Args:
            text: Text to check
            check_type: Type of check (input, output, content)

        Returns:
            Dict with overall result and details from each guardrail
        """
        if not self.guardrails:
            return {
                "passed": True,
                "check_type": check_type,
                "guardrail_results": []
            }

        results = []
        overall_passed = True

        for guardrail in self.guardrails:
            result = guardrail.check(text)
            results.append({
                "guardrail": guardrail.name,
                "passed": result["passed"],
                "reason": result.get("reason"),
                "metadata": result.get("metadata", {})
            })

            if not result["passed"]:
                overall_passed = False
                logger.warning(
                    f"Guardrail '{guardrail.name}' failed on {check_type}: {result.get('reason')}"
                )

        return {
            "passed": overall_passed,
            "check_type": check_type,
            "guardrail_results": results
        }
