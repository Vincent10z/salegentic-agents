from typing import Dict, Any, List
from app.services.vector.vector_service import VectorDBService
from app.services.agent.tools.tool_registry import BaseTool


class VectorRetrievalTool(BaseTool):
    def __init__(self, vector_service: VectorDBService):
        self.vector_service = vector_service

    async def execute(
            self,
            workspace_id: str,
            user_id: str,
            query: str,
            conversation_id: str
    ) -> Dict[str, Any]:
        # Search for relevant documents
        search_results = await self.vector_service.search_documents(
            query=query,
            workspace_id=workspace_id,
            user_id=user_id,
            limit=5,
            similarity_threshold=0.7
        )

        # Process search results
        sources = []
        for result in search_results:
            sources.append({
                "document_id": result.get("document_id"),
                "filename": result.get("filename"),
                "content": result.get("content"),
                "similarity": result.get("similarity", 0)
            })

        # Generate simple response for now
        if sources:
            context_content = "\n\n".join([s["content"] for s in sources])
            answer = f"Based on your documents, I found the following information:\n\n{context_content}"
        else:
            answer = "I couldn't find relevant information in your documents to answer this question."

        return {
            "answer": answer,
            "sources": sources
        }
