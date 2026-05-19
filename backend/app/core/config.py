from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql://rag_user:rag_password@db:5432/private_rag"
    storage_dir: str = "storage"
    ollama_base_url: str = "http://ollama:11434"
    embedding_model: str = "nomic-embed-text"
    generation_model: str = "llama3.2:1b"

settings = Settings()