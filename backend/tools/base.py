"""
Base tool interface
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """Abstract base class for chatbot tools"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        pass

    def to_langchain_tool(self):
        """Convert to LangChain tool format"""
        from langchain.tools import Tool

        return Tool(
            name=self.name,
            description=self.description,
            func=self.execute
        )
