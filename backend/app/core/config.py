from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql://rag_user:rag_password@db:5432/private_rag"
    storage_dir: str = "storage"
    ollama_base_url: str = "http://ollama:11434"
    embedding_model: str = "nomic-embed-text"
    generation_model: str = "llama3.2:1b"
    retrieval_max_distance: float = 0.32

    jwt_secret_key: str | None = None
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()