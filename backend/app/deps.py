"""Dependencias reutilizables de FastAPI: sesion de BD, usuario autenticado
y control de acceso basado en roles (RBAC)."""

from collections.abc import Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.exceptions import ForbiddenError, UnauthorizedError
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise UnauthorizedError("Credenciales invalidas o token expirado.")

    user = db.query(User).filter(User.email == payload["sub"]).first()
    if user is None or not user.is_active:
        raise UnauthorizedError("Usuario no encontrado o inactivo.")
    return user


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    """Dependencia parametrizable: `Depends(require_roles(UserRole.ADMIN))`."""

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenError("No tienes permisos para realizar esta accion.")
        return current_user

    return dependency


def get_optional_user(
    token: str | None = Depends(optional_oauth2_scheme), db: Session = Depends(get_db)
) -> User | None:
    """Como `get_current_user`, pero devuelve None si la peticion no trae token."""
    if not token:
        return None
    return get_current_user(token, db)


def own_student_id(user: User) -> int | None:
    """student_id al que queda limitado un usuario con rol estudiante.

    Devuelve None para admin/teacher (sin limite). Un estudiante sin perfil
    recibe -1, que no coincide con ningun registro.
    """
    if user.role != UserRole.STUDENT:
        return None
    return user.student_profile.id if user.student_profile else -1
