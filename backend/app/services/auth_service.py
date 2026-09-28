from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions import ConflictError, ForbiddenError, UnauthorizedError
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(self, data: UserCreate, requested_by: User | None = None) -> User:
        if self.users.get_by_email(data.email):
            raise ConflictError(f"Ya existe una cuenta con el email {data.email}.")

        privileged = data.role not in (None, UserRole.STUDENT)
        is_admin = requested_by is not None and requested_by.role == UserRole.ADMIN
        if privileged and not is_admin and self.users.count() > 0:
            raise ForbiddenError("Solo un administrador puede crear cuentas de admin o profesor.")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            role=data.role or UserRole.STUDENT,
        )
        return self.users.create(user)

    def authenticate(self, email: str, password: str) -> str:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Email o contrasena incorrectos.")
        if not user.is_active:
            raise UnauthorizedError("La cuenta esta desactivada.")

        return create_access_token(subject=user.email, extra_claims={"role": user.role.value})
