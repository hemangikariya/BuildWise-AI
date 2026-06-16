from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from app.core.logging import system_logger
from app.rag.vector_store import VectorStoreManager

class RetrievalEngine:
    @classmethod
    def retrieve_context(cls, query: str, k: int = 5) -> Tuple[str, List[Dict[str, Any]]]:
        """Performs search in ChromaDB, re-ranks, and returns context and source citations."""
        db = VectorStoreManager.get_db()
        
        # similarity_search_with_relevance_scores returns (Document, score)
        try:
            results = db.similarity_search_with_relevance_scores(query, k=k)
        except Exception as e:
            system_logger.error(f"Error performing similarity search: {str(e)}")
            return "", []

        # Filter out low relevance results (score threshold, e.g., > 0.3)
        # Re-rank: Sort descending by score
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        
        context_parts = []
        citations = []
        seen_sources = set()

        for doc, score in sorted_results:
            # Format text block
            content = doc.page_content.strip()
            source = doc.metadata.get("title", "Unknown Source")
            
            # Context compression: simple extraction of text
            context_parts.append(f"Source: {source}\nContent: {content}")
            
            # Format citation
            citation_key = (source, doc.metadata.get("source", ""))
            if citation_key not in seen_sources:
                seen_sources.add(citation_key)
                citations.append({
                    "title": source,
                    "url_or_path": doc.metadata.get("source", "")
                })

        context_string = "\n\n---\n\n".join(context_parts)
        return context_string, citations

retriever = RetrievalEngine()
