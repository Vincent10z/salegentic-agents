from chromadb import Client
from chromadb.utils import embedding_functions
import json
from typing import List, Dict


class VectorStore:
    def __init__(self):
        self.client = Client()
        self.embedding_fn = embedding_functions.HuggingFaceEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.collection = self.client.create_collection(
            "help_center",
            embedding_function=self.embedding_fn
        )

    async def add_documents(self, file_path: str):
        with open(file_path, 'r') as f:
            articles = json.load(f)

        docs = []
        metadatas = []
        ids = []

        for i, article in enumerate(articles):
            docs.append(article['content'])
            metadatas.append({
                'title': article['title'],
                'url': article.get('url', '')
            })
            ids.append(f"doc_{i}")

        self.collection.add(
            documents=docs,
            metadatas=metadatas,
            ids=ids
        )

    async def search(self, query: str, n_results: int = 3) -> List[Dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        return [
            {
                'content': doc,
                'metadata': meta
            } for doc, meta in zip(results['documents'][0], results['metadatas'][0])
        ]
