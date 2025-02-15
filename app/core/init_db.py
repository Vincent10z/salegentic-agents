from app.repository.vector_store import VectorStore


async def init_vector_store(articles_path: str) -> VectorStore:
    store = VectorStore()
    await store.add_documents(articles_path)
    return store
