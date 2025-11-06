"""
Factory for creating chatbots from configuration
"""
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from chatbot.implementation import LangGraphChatbot

logger = logging.getLogger(__name__)


class ChatbotFactory:
    """Factory for creating chatbot instances"""

    @staticmethod
    def from_config(config_path: str) -> "LangGraphChatbot":
        """
        Create a chatbot from a YAML configuration file.

        Args:
            config_path: Path to YAML config file

        Returns:
            Configured chatbot instance
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        logger.info(f"Loading chatbot from config: {config_path}")

        chatbot_config = config.get('chatbot', {})
        name = chatbot_config.get('name', 'Chatbot')
        use_guardrails = chatbot_config.get('guardrails', {}).get('enabled', True)
        system_prompt = chatbot_config.get('system_prompt')

        # Create chatbot
        chatbot = LangGraphChatbot(
            name=name,
            use_guardrails=use_guardrails,
            system_prompt=system_prompt,
            config=config
        )

        return chatbot

    @staticmethod
    def create(
        name: str = "Chatbot",
        use_guardrails: bool = True,
        use_nemo_guardrails: bool = True,
        system_prompt: Optional[str] = None,
        llm_provider: str = "ollama",
        llm_model: str = "llama3",
        tools: Optional[list] = None,
        **kwargs
    ) -> "LangGraphChatbot":
        """
        Create a chatbot programmatically.

        Args:
            name: Chatbot name
            use_guardrails: Enable regex-based guardrails
            use_nemo_guardrails: Enable NeMo Guardrails
            system_prompt: System prompt
            llm_provider: LLM provider (ollama, openai, etc.)
            llm_model: Model name
            tools: List of tool names to enable
            **kwargs: Additional config

        Returns:
            Configured chatbot instance
        """
        config = {
            'chatbot': {
                'name': name,
                'system_prompt': system_prompt,
                'guardrails': {'enabled': use_guardrails}
            },
            'llm': {
                'provider': llm_provider,
                'model': llm_model
            },
            'tools': tools or ['web_fetch']
        }
        config.update(kwargs)

        return LangGraphChatbot(
            name=name,
            use_guardrails=use_guardrails,
            use_nemo_guardrails=use_nemo_guardrails,
            system_prompt=system_prompt,
            config=config
        )
