from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings
from app.core.logging import system_logger

class EmbeddingEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingEngine, cls).__new__(cls)
            try:
                system_logger.info(f"Loading local embedding model: {settings.EMBEDDING_MODEL_NAME}")
                cls._instance.model = HuggingFaceEmbeddings(
                    model_name=settings.EMBEDDING_MODEL_NAME,
                    encode_kwargs={'normalize_embeddings': True}
                )
                system_logger.info("Local embedding model loaded successfully.")
            except Exception as e:
                system_logger.error(f"Failed to load embedding model: {str(e)}")
                raise e
        return cls._instance

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        return self.model

embedding_engine = EmbeddingEngine()
