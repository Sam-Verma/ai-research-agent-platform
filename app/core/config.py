from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Research Agent"

    # LLM
    LLM_BASE_URL: str
    LLM_API_KEY: str
    LLM_MODEL: str

    # Infrastructure
    POSTGRES_URL: str
    REDIS_URL: str
    QDRANT_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()