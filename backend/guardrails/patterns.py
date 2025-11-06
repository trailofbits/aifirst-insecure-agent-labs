"""
Pattern-based guardrail using regex and keywords
"""
import re
import logging
from typing import Dict, Any, List

from guardrails.base import BaseGuardrail

logger = logging.getLogger(__name__)


class PatternGuardrail(BaseGuardrail):
    """Guardrail using regex patterns to detect prompt injections"""

    # Common injection patterns
    INJECTION_PATTERNS = [
        # Instruction override
        r'ignore\s+(all\s+)?previous\s+instructions?',
        r'disregard\s+(all\s+)?previous\s+instructions?',
        r'forget\s+(all\s+)?previous\s+instructions?',
        r'ignore\s+(all\s+)?above',

        # System commands
        r'system\s+(override|command|message|update)',
        r'new\s+(role|instruction|directive|task)',
        r'you\s+are\s+now\s+(a|an|in|operating)',
        r'switch\s+to\s+.*\s+mode',

        # Data extraction
        r'reveal\s+(your\s+)?(system\s+)?prompt',
        r'show\s+(me\s+)?(your\s+)?(system\s+)?prompt',
        r'extract\s+(all\s+)?(conversation|history|data)',
        r'exfiltrat(e|ed|ion)',

        # Authority impersonation
        r'(system\s+)?administrator\s+(notice|command)',
        r'urgent\s+(system|security)\s+(message|update)',
        r'authorized\s+(system\s+)?command',

        # Credential harvesting
        r'(api\s+)?key',
        r'credentials?',
        r'password',
        r'token',
        r'environment\s+variables?',

        # Guardrail bypass
        r'disable\s+(all\s+)?(safety|guardrail|restriction)',
        r'remove\s+(all\s+)?(safety|guardrail|restriction)',
        r'bypass\s+(safety|security)',
        r'unrestricted\s+mode',
        r'developer\s+mode',
        r'debug\s+mode',
    ]

    def __init__(self, additional_patterns: List[str] = None):
        super().__init__("PatternGuardrail")

        patterns = self.INJECTION_PATTERNS.copy()
        if additional_patterns:
            patterns.extend(additional_patterns)

        # Compile patterns (case-insensitive)
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in patterns
        ]

        logger.info(f"Initialized PatternGuardrail with {len(self.compiled_patterns)} patterns")

    def check(self, text: str) -> Dict[str, Any]:
        """
        Check text for injection patterns.

        Args:
            text: Text to check

        Returns:
            Dict with passed status and matched patterns
        """
        if not text:
            return {"passed": True, "reason": None, "metadata": {}}

        matched_patterns = []

        for pattern in self.compiled_patterns:
            match = pattern.search(text)
            if match:
                matched_patterns.append({
                    "pattern": pattern.pattern,
                    "match": match.group(0),
                    "position": match.start()
                })

        if matched_patterns:
            return {
                "passed": False,
                "reason": f"Detected {len(matched_patterns)} potential injection pattern(s)",
                "metadata": {
                    "matched_patterns": matched_patterns,
                    "pattern_count": len(matched_patterns)
                }
            }

        return {
            "passed": True,
            "reason": None,
            "metadata": {}
        }
