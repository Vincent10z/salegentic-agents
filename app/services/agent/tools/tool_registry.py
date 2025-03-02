from typing import List, Dict, Any
from abc import ABC, abstractmethod


class BaseTool(ABC):
    @abstractmethod
    async def execute(self, workspace_id: str, user_id: str, query: str, conversation_id: str) -> Dict[str, Any]:
        """Execute the tool on the given query and return a result"""
        pass


class ToolRegistry:
    def __init__(self):
        self.tools: List[BaseTool] = []

    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool with the registry"""
        self.tools.append(tool)

    def get_tool_for_query(self, query: str) -> BaseTool:
        """Get the appropriate tool for the query"""
        # Simple implementation for now - just return the first tool
        # Later we can implement tool selection logic
        if not self.tools:
            raise ValueError("No tools registered")
        return self.tools[0]
