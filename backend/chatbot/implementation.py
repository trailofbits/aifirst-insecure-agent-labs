"""
Main LangGraph chatbot implementation
"""
import os
import logging
from typing import Optional, Dict, Any

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from chatbot.base import BaseChatbot
from chatbot.state import ChatbotState
from llm.provider import get_llm
from tools.registry import ToolRegistry
from guardrails.detector import InjectionDetector
from guardrails.nemo_wrapper import NeMoGuardrailWrapper

logger = logging.getLogger(__name__)


class LangGraphChatbot(BaseChatbot):
    """
    LangGraph-based chatbot with guardrails integration
    """

    def __init__(
        self,
        name: str = "LangGraph Chatbot",
        use_guardrails: bool = True,
        use_nemo_guardrails: bool = True,
        system_prompt: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(name, use_guardrails, system_prompt)

        self.config = config or {}
        self.use_nemo_guardrails = use_nemo_guardrails

        # Initialize LLM
        llm_config = self.config.get('llm', {})
        provider = llm_config.get('provider', 'ollama')
        model = llm_config.get('model', 'llama3')

        self.llm = get_llm(provider=provider, model=model)

        # Initialize tools
        tool_names = self.config.get('tools', ['web_fetch'])
        self.tools = ToolRegistry.get_tools(tool_names)

        # Bind tools to LLM (llama3-groq-tool-use supports native tool calling)
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Initialize guardrails - support both types independently
        # Regex detector (legacy)
        if use_guardrails:
            logger.info("Initializing regex-based guardrails")
            self.regex_detector = InjectionDetector(use_patterns=True)
        else:
            self.regex_detector = None

        # NeMo detector (new)
        if use_nemo_guardrails:
            use_light_config = os.getenv("NEMO_LIGHT_CONFIG", "false").lower() == "true"
            logger.info("Initializing NeMo Guardrails")
            self.nemo_detector = NeMoGuardrailWrapper(use_light_config=use_light_config)
            if not self.nemo_detector.enabled:
                logger.warning("NeMo Guardrails initialization failed")
                self.nemo_detector = None
        else:
            self.nemo_detector = None

        # Legacy detector for backward compatibility
        self.detector = self.regex_detector or self.nemo_detector

        # Build the graph
        self.graph = self.build_graph()

        logger.info(f"Initialized {name} with {len(self.tools)} tool(s) (regex={use_guardrails}, nemo={use_nemo_guardrails})")

    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""

        workflow = StateGraph(ChatbotState)

        # Check if any guardrails are enabled
        any_guardrails_enabled = self.use_guardrails or self.use_nemo_guardrails

        # Add nodes
        if any_guardrails_enabled:
            workflow.add_node("check_input", self.check_input_guardrails)
            workflow.add_node("check_output", self.check_output_guardrails)

        workflow.add_node("agent", self.call_agent)
        workflow.add_node("tools", ToolNode(self.tools))

        # Define flow
        if any_guardrails_enabled:
            workflow.set_entry_point("check_input")
            workflow.add_conditional_edges(
                "check_input",
                self.route_after_input_check,
                {"continue": "agent", "blocked": END}
            )
        else:
            workflow.set_entry_point("agent")

        # Agent can call tools or end
        workflow.add_conditional_edges(
            "agent",
            self.route_after_agent,
            {"continue": "tools", "end": "check_output" if any_guardrails_enabled else END}
        )

        # Tools return to agent
        workflow.add_edge("tools", "agent")

        # Output check
        if any_guardrails_enabled:
            workflow.add_conditional_edges(
                "check_output",
                self.route_after_output_check,
                {"continue": END, "blocked": END}
            )

        return workflow.compile()

    def check_input_guardrails(self, state: ChatbotState) -> ChatbotState:
        """Check user input for injections using both regex and NeMo detectors"""
        if not self.regex_detector and not self.nemo_detector:
            return state

        # Get the last user message
        last_message = state["messages"][-1]
        user_input = last_message.content

        # Check with regex detector
        regex_blocked = False
        if self.regex_detector:
            result = self.regex_detector.check_input(user_input)
            if not result["passed"]:
                logger.warning(f"Regex guardrail triggered: {result}")
                state["guardrails_triggered"] = True
                state["regex_guardrail_triggered"] = True
                state["injection_detected"] = True
                state["metadata"]["regex_input_check"] = result
                regex_blocked = True

        # Check with NeMo detector
        nemo_blocked = False
        if self.nemo_detector:
            result = self.nemo_detector.check_input(user_input)
            if not result["passed"]:
                logger.warning(f"NeMo guardrail triggered: {result}")
                state["guardrails_triggered"] = True
                state["nemo_guardrail_triggered"] = True
                state["injection_detected"] = True
                state["metadata"]["nemo_input_check"] = result
                nemo_blocked = True

        # Block if either detector flagged the input
        if regex_blocked or nemo_blocked:
            blocking_system = []
            if regex_blocked:
                blocking_system.append("regex patterns")
            if nemo_blocked:
                blocking_system.append("NeMo Guardrails")

            state["messages"].append(
                AIMessage(content=f"I cannot process this request. The input was blocked by: {', '.join(blocking_system)}.")
            )

        return state

    def call_agent(self, state: ChatbotState) -> ChatbotState:
        """Call the LLM agent"""
        messages = state["messages"]

        # Add system prompt if first call
        if len(messages) == 1 or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=self.system_prompt)] + list(messages)

        # Call LLM with tool binding
        try:
            response = self.llm_with_tools.invoke(messages)
            state["messages"].append(response)
        except Exception as e:
            logger.error(f"Error calling LLM: {e}", exc_info=True)
            state["messages"].append(
                AIMessage(content=f"I encountered an error: {str(e)}")
            )

        return state

    def check_output_guardrails(self, state: ChatbotState) -> ChatbotState:
        """Check agent output for injections using both regex and NeMo detectors"""
        if not self.regex_detector and not self.nemo_detector:
            return state

        # Get the last AI message
        last_message = state["messages"][-1]
        output_text = last_message.content if hasattr(last_message, 'content') else str(last_message)

        # Check with regex detector
        regex_blocked = False
        if self.regex_detector:
            result = self.regex_detector.check_output(output_text)
            if not result["passed"]:
                logger.warning(f"Regex output guardrail triggered: {result}")
                state["guardrails_triggered"] = True
                state["regex_guardrail_triggered"] = True
                state["injection_detected"] = True
                state["metadata"]["regex_output_check"] = result
                regex_blocked = True

        # Check with NeMo detector
        nemo_blocked = False
        if self.nemo_detector:
            result = self.nemo_detector.check_output(output_text)
            if not result["passed"]:
                logger.warning(f"NeMo output guardrail triggered: {result}")
                state["guardrails_triggered"] = True
                state["nemo_guardrail_triggered"] = True
                state["injection_detected"] = True
                state["metadata"]["nemo_output_check"] = result
                nemo_blocked = True

        # Replace output if either detector flagged it
        if regex_blocked or nemo_blocked:
            blocking_system = []
            if regex_blocked:
                blocking_system.append("regex patterns")
            if nemo_blocked:
                blocking_system.append("NeMo Guardrails")

            state["messages"][-1] = AIMessage(
                content=f"I cannot provide this response. The output was blocked by: {', '.join(blocking_system)}."
            )

        return state

    def route_after_input_check(self, state: ChatbotState) -> str:
        """Route after input guardrail check"""
        if state.get("guardrails_triggered"):
            return "blocked"
        return "continue"

    def route_after_agent(self, state: ChatbotState) -> str:
        """Route after agent call"""
        last_message = state["messages"][-1]

        # Check if there are tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"  # Call tools
        return "end"  # Done

    def route_after_output_check(self, state: ChatbotState) -> str:
        """Route after output guardrail check"""
        return "continue"  # Always continue to END
