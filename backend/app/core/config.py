from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql://rag_user:rag_password@db:5432/private_rag"


settings = Settings()