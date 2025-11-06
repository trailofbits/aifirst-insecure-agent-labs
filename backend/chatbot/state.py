"""
Chatbot state management for LangGraph
"""
from typing import Annotated, Sequence, Optional, Dict, Any
from typing_extensions import TypedDict
import operator

from langchain_core.messages import BaseMessage


class ChatbotState(TypedDict):
    """State for the chatbot workflow"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    use_regex_guardrails: bool
    use_nemo_guardrails: bool
    guardrails_triggered: bool
    regex_guardrail_triggered: bool
    nemo_guardrail_triggered: bool
    injection_detected: bool
    metadata: Dict[str, Any]
