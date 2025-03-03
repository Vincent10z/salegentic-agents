# app/services/agent/tool_registry.py
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod


class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the tool"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does"""
        pass

    @abstractmethod
    async def execute(
            self,
            workspace_id: str,
            user_id: str,
            query: str,
            conversation_id: str
    ) -> Dict[str, Any]:
        """Execute the tool"""
        pass


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool with the registry"""
        self.tools[tool.name] = tool

    def get_tool_by_name(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)

    def get_tools_with_descriptions(self) -> List[Dict[str, str]]:
        """Get a list of all tools with their descriptions"""
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self.tools.values()
        ]
