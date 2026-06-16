from app.rag.chunking import chunker

def test_chunking_engine_splits():
    sample_text = (
        "BuildWise AI is an enterprise-grade AI CTO platform that translates software ideas into comprehensive plans. "
        "It uses a LangGraph orchestrator to run multiple agents in loops. "
        "Each agent covers a specific domain such as Product Requirements, API Contracts, or Database Schema."
    )
    
    metadata = {"title": "Test Document", "source": "test_src"}
    
    # We set a small chunk size to verify it splits
    chunker.splitter._chunk_size = 50
    chunks = chunker.split_text(sample_text, metadata)
    
    assert len(chunks) > 1
    assert chunks[0].metadata["title"] == "Test Document"
    assert chunks[0].metadata["source"] == "test_src"
    assert len(chunks[0].page_content) <= 50
