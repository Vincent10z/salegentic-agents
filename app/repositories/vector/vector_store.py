from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import or_

from app.models.vector import (
    DocumentStore,
    DocumentChunk,
    DocumentEmbedding,
    EmbeddingSearch,
    DocumentProcessingStatus
)


class VectorDBRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Document store methods
    async def create_document(self, document: DocumentStore) -> DocumentStore:
        """Create a new document entry."""
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def get_document(
            self,
            document_id: str
    ) -> Optional[DocumentStore]:
        """Get document by ID."""
        stmt = select(DocumentStore).where(DocumentStore.id == document_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_document_by_name(
            self,
            file_name: str,
            workspace_id: str
    ) -> Optional[DocumentStore]:
        """Get document by ID."""
        stmt = select(DocumentStore).where(
            (DocumentStore.filename == file_name) & (DocumentStore.workspace_id == workspace_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_documents_by_workspace(
            self,
            workspace_id: str,
            status: Optional[str] = None,
            document_type: Optional[str] = None,
            limit: int = 100,
            offset: int = 0
    ) -> Tuple[List[DocumentStore], int]:
        """Get documents for a workspace with optional filters."""
        # Build base query
        query = select(DocumentStore).where(DocumentStore.workspace_id == workspace_id)

        # Add filters if provided
        if status:
            query = query.where(DocumentStore.processing_status == status)
        if document_type:
            query = query.where(DocumentStore.document_type == document_type)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)

        # Add pagination
        query = query.order_by(DocumentStore.upload_date.desc()).offset(offset).limit(limit)

        # Execute query
        result = await self.db.execute(query)
        documents = list(result.scalars().all())

        return documents, total

    async def update_document_status(self, document_id: str, status: str, error_message: Optional[str] = None) -> Optional[DocumentStore]:
        """Update document processing status."""
        document = await self.get_document(document_id)
        if not document:
            return None

        document.processing_status = status
        if error_message:
            document.error_message = error_message

        await self.db.commit()
        return document

    async def update_document_metadata(
            self,
            document_id: str,
            metadata: Dict[str, Any]
    ) -> Optional[DocumentStore]:
        """Update document metadata."""
        document = await self.get_document(document_id)
        if not document:
            return None

        if document.document_metadata:
            document.document_metadata.update(metadata)
        else:
            document.document_metadata = metadata

        await self.db.commit()
        return document

    # Chunk methods
    async def create_chunk(self, chunk: DocumentChunk) -> DocumentChunk:
        """Create a new document chunk."""
        self.db.add(chunk)
        await self.db.commit()
        await self.db.refresh(chunk)
        return chunk

    async def create_chunks_batch(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Create multiple document chunks in a batch."""
        self.db.add_all(chunks)
        await self.db.commit()
        return chunks

    async def get_chunks_by_document(self, document_id: str) -> List[DocumentChunk]:
        """Get all chunks for a document."""
        stmt = select(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # Embedding methods
    async def create_embedding(self, embedding: DocumentEmbedding) -> DocumentEmbedding:
        """Create a new embedding."""
        self.db.add(embedding)
        await self.db.commit()
        await self.db.refresh(embedding)
        return embedding

    async def create_embeddings_batch(self, embeddings: List[DocumentEmbedding]) -> List[DocumentEmbedding]:
        """Create multiple embeddings in a batch."""
        self.db.add_all(embeddings)
        await self.db.commit()
        return embeddings

    async def search_similar_embeddings(
            self,
            query_embedding: List[float],
            workspace_id: str,
            limit: int = 10,
            threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings using cosine similarity.

        Note: This requires the pgvector extension to be installed in PostgreSQL.
        """
        # Convert Python list to PostgreSQL vector literal
        vector_str = f"'[{','.join(map(str, query_embedding))}]'"

        # SQL query using pgvector's <=> operator (cosine distance)
        query = text(f"""
            SELECT 
                dc.id as chunk_id,
                dc.content,
                dc.metadata as chunk_metadata,
                ds.id as document_id,
                ds.filename,
                ds.document_type,
                ds.metadata as document_metadata,
                1 - (de.embedding <=> {vector_str}::vector) as similarity
            FROM 
                document_embeddings de
            JOIN 
                document_chunks dc ON de.chunk_id = dc.id
            JOIN 
                document_store ds ON dc.document_id = ds.id
            WHERE 
                ds.workspace_id = :workspace_id
                AND ds.processing_status = :completed_status
                AND 1 - (de.embedding <=> {vector_str}::vector) > :threshold
            ORDER BY 
                similarity DESC
            LIMIT :limit
        """)

        # Execute the query
        result = await self.db.execute(
            query,
            {
                "workspace_id": workspace_id,
                "completed_status": DocumentProcessingStatus.COMPLETED.value,
                "threshold": threshold,
                "limit": limit
            }
        )

        # Process results
        rows = result.fetchall()
        results = []

        for row in rows:
            # Convert row to dict
            result_dict = {
                "chunk_id": row.chunk_id,
                "content": row.content,
                "chunk_metadata": row.chunk_metadata,
                "document_id": row.document_id,
                "filename": row.filename,
                "document_type": row.document_type,
                "document_metadata": row.document_metadata,
                "similarity": row.similarity
            }
            results.append(result_dict)

        return results

    # Search history methods
    async def create_search(self, search: EmbeddingSearch) -> EmbeddingSearch:
        """Create a new search entry."""
        self.db.add(search)
        await self.db.commit()
        await self.db.refresh(search)
        return search

    async def get_searches_by_workspace(
            self,
            workspace_id: str,
            limit: int = 20
    ) -> List[EmbeddingSearch]:
        """Get recent searches for a workspace."""
        stmt = select(EmbeddingSearch).where(
            EmbeddingSearch.workspace_id == workspace_id
        ).order_by(
            EmbeddingSearch.created_at.desc()
        ).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())