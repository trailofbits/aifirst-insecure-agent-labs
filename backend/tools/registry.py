"""
Tool registry for managing available tools
"""
from typing import Dict, List
import logging

from tools.web_fetch import fetch_url
from tools.health_benefits import calculate_benefits, lookup_benefit_details
from tools.employee_data import get_employee_info

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for managing chatbot tools"""

    _tools: Dict = {}

    @classmethod
    def register(cls, name: str, tool):
        """Register a tool"""
        cls._tools[name] = tool
        logger.info(f"Registered tool: {name}")

    @classmethod
    def get(cls, name: str):
        """Get a tool by name"""
        return cls._tools.get(name)

    @classmethod
    def get_tools(cls, tool_names: List[str]) -> List:
        """Get multiple tools by names"""
        tools = []
        for name in tool_names:
            tool = cls.get(name)
            if tool:
                tools.append(tool)
            else:
                logger.warning(f"Tool not found: {name}")
        return tools

    @classmethod
    def list_tools(cls) -> List[str]:
        """List all registered tool names"""
        return list(cls._tools.keys())


# Register default tools
ToolRegistry.register('web_fetch', fetch_url)
ToolRegistry.register('calculate_benefits', calculate_benefits)
ToolRegistry.register('lookup_benefit_details', lookup_benefit_details)
ToolRegistry.register('get_employee_info', get_employee_info)
