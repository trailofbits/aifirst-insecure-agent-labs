"""
NeMo Guardrails wrapper for integration with LangGraph chatbot
"""
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class NeMoGuardrailWrapper:
    """
    Wrapper around NVIDIA NeMo Guardrails for integration with existing chatbot.

    Provides a compatible interface with the previous InjectionDetector while
    using NeMo's guardrail capabilities.
    """

    def __init__(self, config_path: Optional[str] = None, use_light_config: bool = False):
        """
        Initialize NeMo Guardrails.

        Args:
            config_path: Path to NeMo config directory. Defaults to config/nemo
            use_light_config: Use lightweight config (heuristics only, faster)
        """
        try:
            from nemoguardrails import RailsConfig
            from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails

            # Determine config path
            if config_path is None:
                base_dir = Path(__file__).parent.parent
                config_path = base_dir / "config" / "nemo"
            else:
                config_path = Path(config_path)

            # Choose config file
            if use_light_config:
                config_file = config_path / "config.light.yml"
                if not config_file.exists():
                    config_file = config_path / "config.yml"
                    logger.warning("Light config not found, using full config")
            else:
                config_file = config_path / "config.yml"

            if not config_file.exists():
                raise FileNotFoundError(f"NeMo config not found at: {config_file}")

            logger.info(f"Loading NeMo Guardrails config from: {config_file}")

            # Load configuration
            self.config = RailsConfig.from_path(str(config_path))

            # Create RunnableRails instance
            # passthrough=True means we get detailed information about what was blocked
            self.rails = RunnableRails(
                config=self.config,
                passthrough=True,
                verbose=False
            )

            self.enabled = True
            logger.info("NeMo Guardrails initialized successfully")

        except ImportError as e:
            logger.error(f"NeMo Guardrails not installed: {e}")
            logger.warning("Falling back to no guardrails (pass-through mode)")
            self.enabled = False
            self.rails = None

        except Exception as e:
            logger.error(f"Error initializing NeMo Guardrails: {e}", exc_info=True)
            logger.warning("Falling back to no guardrails (pass-through mode)")
            self.enabled = False
            self.rails = None

    def check_input(self, text: str) -> Dict[str, Any]:
        """
        Check user input for policy violations using NeMo input rails.

        Args:
            text: User input text to check

        Returns:
            Dict with:
                - passed: bool (True if safe, False if blocked)
                - check_type: str ("input")
                - guardrail_results: list of results from each rail
        """
        if not self.enabled or not self.rails:
            return {
                "passed": True,
                "check_type": "input",
                "guardrail_results": []
            }

        try:
            # Invoke NeMo rails on the input
            result = self.rails.invoke({
                "input": text,
                "messages": [{"role": "user", "content": text}]
            })

            # Log the full result for debugging
            logger.info(f"NeMo check_input result: {result}")

            # Check if input was blocked by looking at the output
            # When NeMo blocks, it typically returns a canned response or None
            output = result.get("output")

            # NeMo blocks by either:
            # 1. Returning None for output
            # 2. Returning a stop/refusal message
            # 3. Setting a flag in the result
            blocked = (
                output is None or
                output == "" or
                "can't respond" in str(output).lower() or
                "cannot respond" in str(output).lower() or
                "sorry" in str(output).lower() and ("policy" in str(output).lower() or "cannot" in str(output).lower())
            )

            # Extract violation information
            violations = []
            if blocked:
                # NeMo may provide explanation in output or metadata
                reason = str(output) if output else "Input violated guardrail policy"
                violations.append({
                    "guardrail": "nemo_input_rails",
                    "passed": False,
                    "reason": reason,
                    "metadata": result.get("log", {})
                })

            return {
                "passed": not blocked,
                "check_type": "input",
                "guardrail_results": violations if violations else [
                    {
                        "guardrail": "nemo_input_rails",
                        "passed": True,
                        "reason": None,
                        "metadata": {}
                    }
                ]
            }

        except Exception as e:
            logger.error(f"Error checking input with NeMo: {e}", exc_info=True)
            # On error, fail open (allow) but log the error
            return {
                "passed": True,
                "check_type": "input",
                "guardrail_results": [{
                    "guardrail": "nemo_input_rails",
                    "passed": True,
                    "reason": None,
                    "metadata": {"error": str(e)}
                }]
            }

    def check_output(self, text: str) -> Dict[str, Any]:
        """
        Check bot output for policy violations using NeMo output rails.

        Args:
            text: Bot output text to check

        Returns:
            Dict with:
                - passed: bool (True if safe, False if blocked)
                - check_type: str ("output")
                - guardrail_results: list of results from each rail
        """
        if not self.enabled or not self.rails:
            return {
                "passed": True,
                "check_type": "output",
                "guardrail_results": []
            }

        try:
            # For output checking, we need to simulate a conversation
            # where the bot just generated this output
            result = self.rails.invoke({
                "messages": [
                    {"role": "user", "content": "previous user message"},
                    {"role": "assistant", "content": text}
                ]
            })

            # Check if output was blocked
            blocked = result.get("output") != text

            violations = []
            if blocked:
                reason = result.get("output", "Output violated guardrail policy")
                violations.append({
                    "guardrail": "nemo_output_rails",
                    "passed": False,
                    "reason": reason,
                    "metadata": result.get("log", {})
                })

            return {
                "passed": not blocked,
                "check_type": "output",
                "guardrail_results": violations if violations else [
                    {
                        "guardrail": "nemo_output_rails",
                        "passed": True,
                        "reason": None,
                        "metadata": {}
                    }
                ]
            }

        except Exception as e:
            logger.error(f"Error checking output with NeMo: {e}", exc_info=True)
            # On error, fail open (allow) but log the error
            return {
                "passed": True,
                "check_type": "output",
                "guardrail_results": [{
                    "guardrail": "nemo_output_rails",
                    "passed": True,
                    "reason": None,
                    "metadata": {"error": str(e)}
                }]
            }

    def check_content(self, text: str) -> Dict[str, Any]:
        """
        Check retrieved content (e.g., from web fetch) for injections.

        This uses the same input rails since content from external sources
        should be treated as potentially malicious input.

        Args:
            text: Content text to check

        Returns:
            Dict with:
                - passed: bool (True if safe, False if blocked)
                - check_type: str ("content")
                - guardrail_results: list of results from each rail
        """
        # Use input checking for content
        result = self.check_input(text)
        result["check_type"] = "content"
        return result
