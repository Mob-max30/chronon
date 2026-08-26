from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Chronon Timetable System"

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://chronon_user:chronon_password@localhost:5432/chronon_db"
    DATABASE_URL_SYNC: str = "postgresql://chronon_user:chronon_password@localhost:5432/chronon_db"

    # Solver
    CP_SAT_MAX_TIME_IN_SECONDS: int = 120
    CP_SAT_NUM_SEARCH_WORKERS: int = 8
    CP_SAT_LOG_SEARCH_PROGRESS: bool = False

    # Ingestion
    TESSERACT_CMD: str = "tesseract"
    UPLOAD_DIR: str = "./uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
