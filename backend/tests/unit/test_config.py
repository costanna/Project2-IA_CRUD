from app.core.config import Settings


def test_normaliza_esquema_postgres_a_postgresql_psycopg2():
    settings = Settings(database_url="postgres://user:pass@host:5432/db")
    assert settings.database_url == "postgresql+psycopg2://user:pass@host:5432/db"


def test_normaliza_esquema_postgresql_a_postgresql_psycopg2():
    settings = Settings(database_url="postgresql://user:pass@host:5432/db")
    assert settings.database_url == "postgresql+psycopg2://user:pass@host:5432/db"


def test_conserva_query_params_como_sslmode_de_neon():
    settings = Settings(database_url="postgres://user:pass@ep-xxx.neon.tech/db?sslmode=require")
    assert settings.database_url == "postgresql+psycopg2://user:pass@ep-xxx.neon.tech/db?sslmode=require"


def test_no_toca_sqlite():
    settings = Settings(database_url="sqlite:///./academia.db")
    assert settings.database_url == "sqlite:///./academia.db"
