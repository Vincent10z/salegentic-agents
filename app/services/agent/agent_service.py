from app.models.request import ChatRequest
from app.models.response import ChatResponse
from app.repository.vector_store import VectorStore


class AgentService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    async def process_query(self, request: ChatRequest) -> ChatResponse:
        if self._needs_context(request) and not self._has_required_context(request):
            return ChatResponse(
                response="Before troubleshooting, I need some information.",
                sources=[],
                requires_context=True,
                required_info=["country", "device"]
            )

        # RAG
        relevant_docs = await self.vector_store.search(request.query)


    def _needs_context(self, request):
        pass

    def _has_required_context(self, request):
        pass
