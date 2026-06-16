import os
import uuid
from typing import List
from sqlalchemy.orm import Session
from langchain_core.documents import Document
from app.core.config import settings
from app.core.logging import system_logger
from app.models.rag import KnowledgeBase
from app.rag.chunking import chunker
from app.rag.vector_store import VectorStoreManager

class IngestionManager:
    @classmethod
    def ingest_file(cls, db: Session, file_path: str, title: str, source_url: str = None) -> KnowledgeBase:
        """Reads a local file, saves metadata to PostgreSQL, chunks and stores in ChromaDB."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read text content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Save to database
        db_kb = KnowledgeBase(
            title=title,
            content=content,
            source_url=source_url,
            file_path=file_path,
            metadata_={"file_size": len(content)}
        )
        db.add(db_kb)
        db.commit()
        db.refresh(db_kb)

        # Chunk text
        metadata = {
            "kb_id": str(db_kb.id),
            "title": title,
            "source": source_url or file_path
        }
        chunks = chunker.split_text(content, metadata)

        # Add to ChromaDB
        VectorStoreManager.add_documents(chunks)
        system_logger.info(f"Ingested file '{title}' successfully and chunked into {len(chunks)} fragments.")
        return db_kb

    @classmethod
    def ingest_directory(cls, db: Session, directory_path: str) -> List[KnowledgeBase]:
        """Scans a directory for .md and .txt files, and ingests them all."""
        ingested = []
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
            system_logger.warning(f"Directory {directory_path} did not exist, created empty.")
            return ingested

        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith((".md", ".txt")):
                    file_path = os.path.join(root, file)
                    title = os.path.splitext(file)[0].replace("_", " ").title()
                    try:
                        kb_entry = cls.ingest_file(db, file_path, title)
                        ingested.append(kb_entry)
                    except Exception as e:
                        system_logger.error(f"Failed to ingest file '{file_path}': {str(e)}")
        return ingested
