from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Template Solventa Math Service"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "dev"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    API_PREFIX: str = "/api/v1/math-service"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()