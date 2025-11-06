"""
Pydantic models for API requests/responses
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request"""
    messages: List[Message] = Field(..., description="Conversation history")
    guardrails_enabled: bool = Field(default=True, description="Enable regex-based guardrails (legacy)")
    nemo_guardrails_enabled: bool = Field(default=True, description="Enable NeMo Guardrails")
    department: str = Field(default="hr", description="Department context: 'hr' or 'payroll'")
    scenario_id: Optional[str] = Field(None, description="Scenario ID to load")
    stream: bool = Field(default=True, description="Stream response")


class ChatResponse(BaseModel):
    """Chat response"""
    response: str = Field(..., description="Assistant response")
    guardrails_triggered: bool = Field(..., description="Whether any guardrails blocked request")
    regex_guardrail_triggered: bool = Field(default=False, description="Whether regex guardrails blocked request")
    nemo_guardrail_triggered: bool = Field(default=False, description="Whether NeMo guardrails blocked request")
    injection_detected: bool = Field(..., description="Whether injection was detected")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    guardrails_available: bool
