"""
Base chatbot class with LangGraph integration
"""
import logging
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from chatbot.state import ChatbotState

logger = logging.getLogger(__name__)


class BaseChatbot(ABC):
    """
    Abstract base class for chatbots with LangGraph workflow.

    Provides:
    - Message handling
    - Tool integration
    - Guardrail hooks
    - State management
    """

    def __init__(
        self,
        name: str = "Chatbot",
        use_guardrails: bool = True,
        system_prompt: Optional[str] = None
    ):
        self.name = name
        self.use_guardrails = use_guardrails
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.graph = None
        self.tools = []
        self.guardrails = None

        logger.info(f"Initialized {self.name} (guardrails={'enabled' if use_guardrails else 'disabled'})")

    def _default_system_prompt(self) -> str:
        """Default system prompt"""
        return (
            "You are a helpful AI assistant. "
            "Answer questions accurately and concisely. "
            "If you need to fetch information from a URL, use the fetch_url tool."
        )

    @abstractmethod
    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow. Must be implemented by subclasses."""
        pass

    def add_tool(self, tool):
        """Add a tool to the chatbot"""
        self.tools.append(tool)
        logger.info(f"Added tool: {tool.name}")

    def set_guardrails(self, guardrails):
        """Set the guardrails module"""
        self.guardrails = guardrails
        logger.info("Guardrails configured")

    async def chat(
        self,
        message: str,
        conversation_history: Optional[List[BaseMessage]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and return response.

        Args:
            message: User message
            conversation_history: Previous messages

        Returns:
            Dict with response, metadata, and guardrail info
        """
        if not self.graph:
            raise RuntimeError("Graph not built. Call build_graph() first.")

        # Prepare initial state
        messages = conversation_history or []
        messages.append(HumanMessage(content=message))

        initial_state: ChatbotState = {
            "messages": messages,
            "use_regex_guardrails": self.use_guardrails,
            "use_nemo_guardrails": getattr(self, 'use_nemo_guardrails', False),
            "guardrails_triggered": False,
            "regex_guardrail_triggered": False,
            "nemo_guardrail_triggered": False,
            "injection_detected": False,
            "metadata": {}
        }

        # Build tags for LangSmith tracing
        tags = []

        # Check if this is a LangGraphChatbot with dual guardrail support
        if hasattr(self, 'regex_detector') and self.regex_detector:
            tags.append("regex-guardrails-enabled")
        if hasattr(self, 'nemo_detector') and self.nemo_detector:
            tags.append("nemo-guardrails-enabled")

        # Create config with tags
        config = RunnableConfig(tags=tags) if tags else None

        # Run the graph
        try:
            result = await self.graph.ainvoke(initial_state, config=config)

            # Extract response
            last_message = result["messages"][-1]
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)

            return {
                "response": response_content,
                "guardrails_triggered": result.get("guardrails_triggered", False),
                "regex_guardrail_triggered": result.get("regex_guardrail_triggered", False),
                "nemo_guardrail_triggered": result.get("nemo_guardrail_triggered", False),
                "injection_detected": result.get("injection_detected", False),
                "metadata": result.get("metadata", {}),
                "messages": result["messages"]
            }

        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            return {
                "response": f"Error: {str(e)}",
                "guardrails_triggered": False,
                "injection_detected": False,
                "metadata": {"error": str(e)},
                "messages": messages
            }

    def chat_sync(self, message: str, conversation_history: Optional[List[BaseMessage]] = None) -> Dict[str, Any]:
        """Synchronous version of chat"""
        import asyncio
        return asyncio.run(self.chat(message, conversation_history))
