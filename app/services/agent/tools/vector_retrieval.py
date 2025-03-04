# app/services/agent/tools/vector_retrieval_tool.py
from typing import Dict, Any
from app.services.vector.vector_service import VectorDBService
from app.services.agent.tools.tool_registry import BaseTool


class VectorRetrievalTool(BaseTool):
    def __init__(self, vector_service: VectorDBService):
        self.vector_service = vector_service

    @property
    def name(self) -> str:
        return "document_search"

    @property
    def description(self) -> str:
        return ("Search through documents to find information. Input should be a specific question about document "
                "content.")

    async def execute(
            self,
            workspace_id: str,
            user_id: str,
            query: str,
            conversation_id: str
    ) -> Dict[str, Any]:
        search_results = await self.vector_service.search_documents(
            query=query,
            workspace_id=workspace_id,
            user_id=user_id,
            limit=5,
            similarity_threshold=0.7
        )

        sources = []
        for result in search_results:
            sources.append({
                "document_id": result.get("document_id"),
                "filename": result.get("filename"),
                "content": result.get("content"),
                "similarity": result.get("similarity", 0)
            })

        return {
            "sources": sources,
            "count": len(sources)
        }
