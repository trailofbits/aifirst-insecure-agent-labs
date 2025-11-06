"""
LLM provider factory
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_llm(provider: str = "ollama", model: str = "llama3", **kwargs):
    """
    Get an LLM instance based on provider.

    Args:
        provider: Provider name (ollama, openai, anthropic)
        model: Model name
        **kwargs: Additional provider-specific arguments

    Returns:
        LLM instance
    """
    if provider == "ollama":
        from langchain_ollama import ChatOllama

        base_url = kwargs.get("base_url") or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        temperature = kwargs.get("temperature", 0.7)

        logger.info(f"Initializing Ollama LLM: {model} at {base_url}")

        return ChatOllama(
            model=model,
            base_url=base_url,
            temperature=temperature,
            num_predict=6096  # Increase max output tokens for longer responses
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI

        api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")

        logger.info(f"Initializing OpenAI LLM: {model}")

        return ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=kwargs.get("temperature", 0.7)
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        api_key = kwargs.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key required")

        logger.info(f"Initializing Anthropic LLM: {model}")

        return ChatAnthropic(
            model=model,
            api_key=api_key,
            temperature=kwargs.get("temperature", 0.7)
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
