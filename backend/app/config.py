from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mesh_api_key: str = ""
    mesh_embedding_model: str = "vertex/text-embedding-005"
    frontend_origin: str = "http://localhost:3000"
    request_timeout_seconds: float = 20
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
