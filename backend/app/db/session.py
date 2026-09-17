"""Motor y sesion de SQLAlchemy.

Los modelos usan tipos estandar (no especificos de Postgres) para que la
misma base de codigo funcione tanto contra PostgreSQL (produccion, via
DATABASE_URL) como contra SQLite en memoria (tests rapidos), maximizando
la fiabilidad de la suite de tests sin necesitar un Postgres corriendo en
cada ejecucion local.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
