import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
from src.enums import Environment

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    ENVIRONMENT: str = os.getenv("APP_ENV") or Environment.DEVELOPMENT.value
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: str = os.getenv("REDIS_PORT")
    REDIS_USERNAME: str = os.getenv("REDIS_USERNAME")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = os.getenv("ORIGINS")
    GENERATION_JOB_PREFIX_KEY: str = "GJOB"
    DELETE_GENERATION_AFTER_DAYS: int = os.getenv("DELETE_GENERATION_AFTER_DAYS")
    CALLER_TOKEN: str = os.getenv("CALLER_TOKEN")

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> Union[list[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True


settings = Settings()
