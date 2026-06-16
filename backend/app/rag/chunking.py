from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class ChunkingEngine:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def split_text(self, text: str, metadata: Dict[str, Any]) -> List[Document]:
        """Split a raw text block into Documents with metadata."""
        return self.splitter.create_documents([text], metadatas=[metadata])

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split a list of LangChain Document objects."""
        return self.splitter.split_documents(documents)

chunker = ChunkingEngine()
