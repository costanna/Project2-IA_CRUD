from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.exceptions import ConflictError, NotFoundError
from app.models.teacher import Teacher
from app.models.user import User, UserRole
from app.repositories.teacher_repository import TeacherRepository
from app.repositories.user_repository import UserRepository
from app.schemas.teacher import TeacherCreate, TeacherUpdate


class TeacherService:
    def __init__(self, db: Session):
        self.db = db
        self.teachers = TeacherRepository(db)
        self.users = UserRepository(db)

    def list(self, skip: int, limit: int) -> tuple[list[Teacher], int]:
        return self.teachers.list(skip=skip, limit=limit)

    def get(self, teacher_id: int) -> Teacher:
        teacher = self.teachers.get(teacher_id)
        if not teacher:
            raise NotFoundError(f"Profesor {teacher_id} no encontrado.")
        return teacher

    def create(self, data: TeacherCreate) -> Teacher:
        if self.users.get_by_email(data.email):
            raise ConflictError(f"Ya existe una cuenta con el email {data.email}.")

        user = self.users.create(
            User(email=data.email, hashed_password=hash_password(data.password), role=UserRole.TEACHER)
        )
        teacher = Teacher(
            user_id=user.id,
            first_name=data.first_name,
            last_name=data.last_name,
            specialty=data.specialty,
        )
        return self.teachers.create(teacher)

    def update(self, teacher_id: int, data: TeacherUpdate) -> Teacher:
        teacher = self.get(teacher_id)
        return self.teachers.update(teacher, data.model_dump(exclude_unset=True))

    def delete(self, teacher_id: int) -> None:
        teacher = self.get(teacher_id)
        # Borrar la cuenta arrastra el perfil (ON DELETE CASCADE) y evita
        # que quede un usuario huerfano que aun pueda iniciar sesion.
        self.users.delete(teacher.user)
