import os
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from app.core.config import settings
from app.core.logging import system_logger
from app.rag.embeddings import embedding_engine

class VectorStoreManager:
    _db: Chroma = None

    @classmethod
    def get_db(cls) -> Chroma:
        """Singleton getter for Chroma database connection."""
        if cls._db is None:
            try:
                os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
                cls._db = Chroma(
                    persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                    embedding_function=embedding_engine.get_embeddings(),
                    collection_name="buildwise_kb"
                )
                system_logger.info("ChromaDB connection initialized successfully.")
            except Exception as e:
                system_logger.error(f"Failed to connect to ChromaDB: {str(e)}")
                raise e
        return cls._db

    @classmethod
    def add_documents(cls, documents: List[Document]) -> None:
        """Add langchain documents to ChromaDB."""
        db = cls.get_db()
        db.add_documents(documents)
        system_logger.info(f"Successfully added {len(documents)} chunks to ChromaDB.")

    @classmethod
    def delete_collection(cls) -> None:
        """Delete ChromaDB collection (useful for rebuilds)."""
        db = cls.get_db()
        db.delete_collection()
        cls._db = None
        system_logger.info("ChromaDB collection cleared.")
