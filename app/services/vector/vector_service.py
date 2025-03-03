import os
import io
import json
from typing import List, Dict, Any, Optional, Tuple, BinaryIO
from datetime import datetime

from fastapi import UploadFile, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import PyPDF2
import mammoth
import pandas as pd
import numpy as np
from openai import AsyncOpenAI

from app.core.database import get_session
from app.core.config import settings
from app.core.id_generator.id_generator import generate_document_embedding_id
from app.models.vector import (
    DocumentStore,
    DocumentChunk,
    DocumentEmbedding,
    EmbeddingSearch,
    DocumentProcessingStatus,
    DocumentType
)
from app.repositories.vector.vector_store import VectorRepository
from app.services.vector.vector_helpers import convert_to_dict, get_document_type, extract_text, split_text


class VectorDBService:
    def __init__(
            self,
            db: AsyncSession,
            repository: VectorRepository,
            openai_client: AsyncOpenAI
    ):
        self.db = db
        self.repository = repository
        self.openai_client = openai_client
        self.chunk_size = 1000  # Characters per chunk
        self.chunk_overlap = 200  # Character overlap between chunks

    async def process_document(
            self,
            file: UploadFile,
            workspace_id: str,
            user_id: Optional[str] = None,
            custom_metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentStore:
        """
        Process an uploaded document:
        1. Store metadata
        2. Extract text
        3. Split into chunks
        4. Generate embeddings
        """
        try:
            # Check if document exists already
            document = await self.repository.get_document_by_name(file.filename, workspace_id)
            if document:
                raise ValueError(
                    f"Document '{file.filename}' already exists in this workspace. Please use a different file name or "
                    f"delete the existing document first.")

            # 1. Create document record
            document_type = get_document_type(
                file.filename
            )
            content_type = file.content_type or "application/octet-stream"

            # Read file content into memory
            file_content = await file.read()
            file_size = len(file_content)

            # Create document record
            user_id = "usr_j66lytm7yed8bt7esd2kh"
            document = DocumentStore(
                workspace_id=workspace_id,
                filename=file.filename,
                document_type=document_type,
                content_type=content_type,
                file_size=file_size,
                uploaded_by_user_id=user_id,
                processing_status=DocumentProcessingStatus.PROCESSING.value,
                document_metadata=custom_metadata or {}
            )

            document = await self.repository.create_document(document)

            try:
                text_content, metadata = await extract_text(
                    file_content=file_content,
                    document_type=document_type,
                    filename=file.filename
                )

                metadata = convert_to_dict(metadata)

                document = await self.repository.update_document_metadata(
                    document_id=document.id,
                    metadata={**(document.document_metadata or {}), **metadata}
                )

                chunks = split_text(
                    text=text_content,
                    document_id=document.id,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
                saved_chunks = await self.repository.create_chunks_batch(chunks)

                await self._process_embeddings(saved_chunks)

                document = await self.repository.update_document_status(
                    document_id=document.id,
                    status=DocumentProcessingStatus.COMPLETED.value
                )

            except Exception as e:
                _ = await self.repository.update_document_status(
                    document_id=document.id,
                    status=DocumentProcessingStatus.ERROR.value,
                    error_message=str(e)
                )
                raise

            return document

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing document: {str(e)}"
            )

    async def _process_embeddings(self, chunks: List[DocumentChunk]) -> List[DocumentEmbedding]:
        """
        Generate embeddings for chunks and save them to the database.
        """
        embeddings = []
        chunk_batches = [chunks[i:i + 100] for i in range(0, len(chunks), 100)]

        for batch in chunk_batches:
            texts = [chunk.content for chunk in batch]

            response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )

            embedding_vectors = [item.embedding for item in response.data]

            batch_embeddings = []
            for i, chunk in enumerate(batch):
                # Create the embedding object with the vector data
                embedding = DocumentEmbedding(
                    id=generate_document_embedding_id(),
                    chunk_id=chunk.id,
                    embedding=embedding_vectors[i]  # Pass the raw list directly
                )

                # Add to session and flush to get the ID
                self.db.add(embedding)
                await self.db.flush()

                batch_embeddings.append(embedding)

            embeddings.extend(batch_embeddings)

            # Commit after each batch
            await self.db.commit()

        return embeddings

    async def search_documents(
            self,
            query: str,
            workspace_id: str,
            user_id: Optional[str] = None,
            limit: int = 10,
            similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query.
        """
        try:
            # 1. Generate embedding for the query
            response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=[query]
            )

            query_embedding = response.data[0].embedding

            # 2. Find similar document chunks
            results = await self.repository.search_similar_embeddings(
                query_embedding=query_embedding,
                workspace_id=workspace_id,
                limit=limit,
                threshold=similarity_threshold
            )

            # 3. Log the search
            search_record = EmbeddingSearch(
                workspace_id=workspace_id,
                user_id=user_id,
                query=query,
                metadata={
                    "result_count": len(results),
                    "top_similarity": results[0]["similarity"] if results else None
                }
            )

            await self.repository.create_search(search_record)

            return results

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Search failed: {str(e)}"
            )

    async def get_document_by_id(self, document_id: str) -> Optional[DocumentStore]:
        """Get document by ID."""
        return await self.repository.get_document(document_id)

    async def get_documents_by_workspace(
            self,
            workspace_id: str,
            status: Optional[str] = None,
            document_type: Optional[str] = None,
            limit: int = 100,
            offset: int = 0
    ) -> Tuple[List[DocumentStore], int]:
        """Get documents for a workspace with optional filters."""
        return await self.repository.get_documents_by_workspace(
            workspace_id=workspace_id,
            status=status,
            document_type=document_type,
            limit=limit,
            offset=offset
        )

    async def get_document_content(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get full content of a document by retrieving all its chunks.
        """
        # Get document to confirm it exists
        document = await self.repository.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Get all chunks
        chunks = await self.repository.get_chunks_by_document(document_id)

        # Format results
        result = {
            "document_id": document.id,
            "filename": document.filename,
            "document_type": document.document_type,
            "metadata": document.metadata,
            "chunks": [
                {
                    "chunk_id": chunk.id,
                    "index": chunk.chunk_index,
                    "content": chunk.content,
                    "metadata": chunk.metadata
                }
                for chunk in chunks
            ]
        }

        return result

    async def get_recent_searches(self, workspace_id: str, limit: int = 20) -> List[EmbeddingSearch]:
        """Get recent searches for a workspace."""
        return await self.repository.get_searches_by_workspace(
            workspace_id=workspace_id,
            limit=limit
        )


# Factory for dependency injection
def get_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def get_vector_db_repository(db: AsyncSession = Depends(get_session)) -> VectorRepository:
    return VectorRepository(db)


def get_vector_db_service(
        db: AsyncSession = Depends(get_session),
        repository: VectorRepository = Depends(get_vector_db_repository),
        openai_client: AsyncOpenAI = Depends(get_openai_client)
) -> VectorDBService:
    return VectorDBService(db=db, repository=repository, openai_client=openai_client)
