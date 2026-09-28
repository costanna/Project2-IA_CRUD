"""Configuracion de la aplicacion a partir de variables de entorno.

Usamos pydantic-settings para que todo dato sensible (credenciales de BD,
clave secreta de JWT, etc.) llegue via variables de entorno y nunca quede
hardcodeado en el codigo fuente (requisito de Nivel Esencial: "Variables de
entorno para datos sensibles").
"""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "Academia F5 API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    # Base de datos
    database_url: str = "sqlite:///./academia.db"

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        """Proveedores como Neon, Render o Heroku entregan cadenas de
        conexion con el esquema `postgres://`, que SQLAlchemy 1.4+ ya no
        reconoce (espera `postgresql://` o, con el driver explicito,
        `postgresql+psycopg2://`). Normalizamos aqui para poder pegar la
        cadena de Neon tal cual en la variable de entorno sin editarla.
        """
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg2://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg2://", 1)
        return value

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
