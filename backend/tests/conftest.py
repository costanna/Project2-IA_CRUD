"""Fixtures compartidas por toda la suite de tests.

Usamos una base de datos SQLite en un fichero temporal (no en memoria, para
que la misma base sea visible desde cualquier conexion/hilo que abra la
app) que se recrea antes de cada test, de forma que los tests son
independientes entre si y no requieren un PostgreSQL real para ejecutarse.
Los mismos modelos corren sin cambios contra PostgreSQL en produccion.
"""

import os
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

_TEST_DB_PATH = Path(tempfile.gettempdir()) / "academia_test.db"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TEST_DB_PATH.as_posix()}")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.core.cache import clear_cache  # noqa: E402
from app.core.security import create_access_token, hash_password  # noqa: E402
from app.db.session import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.student import Student  # noqa: E402
from app.models.teacher import Teacher  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_state():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    clear_cache()
    yield
    Base.metadata.drop_all(bind=engine)
    clear_cache()


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def _create_user(db, email: str, password: str, role: UserRole) -> User:
    user = User(email=email, hashed_password=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _auth_headers(user: User) -> dict:
    token = create_access_token(subject=user.email, extra_claims={"role": user.role.value})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin(db_session):
    user = _create_user(db_session, "admin@academiaf5.dev", "adminpass123", UserRole.ADMIN)
    return SimpleNamespace(user=user, headers=_auth_headers(user))


@pytest.fixture
def teacher(db_session):
    user = _create_user(db_session, "teacher@academiaf5.dev", "teacherpass123", UserRole.TEACHER)
    profile = Teacher(user_id=user.id, first_name="Ada", last_name="Lovelace", specialty="Matematicas")
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return SimpleNamespace(user=user, profile=profile, headers=_auth_headers(user))


@pytest.fixture
def student(db_session):
    user = _create_user(db_session, "student@academiaf5.dev", "studentpass123", UserRole.STUDENT)
    profile = Student(user_id=user.id, first_name="Grace", last_name="Hopper")
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return SimpleNamespace(user=user, profile=profile, headers=_auth_headers(user))
