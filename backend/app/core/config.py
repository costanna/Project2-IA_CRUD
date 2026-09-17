"""Configuracion de la aplicacion a partir de variables de entorno.

Usamos pydantic-settings para que todo dato sensible (credenciales de BD,
clave secreta de JWT, etc.) llegue via variables de entorno y nunca quede
hardcodeado en el codigo fuente (requisito de Nivel Esencial: "Variables de
entorno para datos sensibles").
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "Academia F5 API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    # Base de datos
    database_url: str = "sqlite:///./academia.db"

    # Seguridad / JWT
    secret_key: str = "change-me-in-.env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS (frontend)
    cors_origins: list[str] = ["http://localhost:5173"]

    # Cache
    cache_ttl_seconds: int = 30

    # Logging
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
