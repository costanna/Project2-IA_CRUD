import csv
import io

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.exceptions import ConflictError, NotFoundError
from app.models.student import Student
from app.models.user import User, UserRole
from app.repositories.student_repository import StudentRepository
from app.repositories.user_repository import UserRepository
from app.schemas.student import StudentCreate, StudentUpdate


class StudentService:
    def __init__(self, db: Session):
        self.db = db
        self.students = StudentRepository(db)
        self.users = UserRepository(db)

    def list(self, skip: int, limit: int) -> tuple[list[Student], int]:
        return self.students.list(skip=skip, limit=limit)

    def get(self, student_id: int) -> Student:
        student = self.students.get(student_id)
        if not student:
            raise NotFoundError(f"Estudiante {student_id} no encontrado.")
        return student

    def create(self, data: StudentCreate) -> Student:
        if self.users.get_by_email(data.email):
            raise ConflictError(f"Ya existe una cuenta con el email {data.email}.")

        user = self.users.create(
            User(email=data.email, hashed_password=hash_password(data.password), role=UserRole.STUDENT)
        )
        student = Student(
            user_id=user.id,
            first_name=data.first_name,
            last_name=data.last_name,
            birth_date=data.birth_date,
            phone=data.phone,
        )
        return self.students.create(student)

    def update(self, student_id: int, data: StudentUpdate) -> Student:
        student = self.get(student_id)
        return self.students.update(student, data.model_dump(exclude_unset=True))

    def delete(self, student_id: int) -> None:
        student = self.get(student_id)
        # Borrar la cuenta arrastra el perfil (ON DELETE CASCADE) y evita
        # que quede un usuario huerfano que aun pueda iniciar sesion.
        self.users.delete(student.user)

    def export_csv(self) -> str:
        """CSV con todos los estudiantes (Nivel Medio: exportacion a CSV)."""
        students, _ = self.students.list(skip=0, limit=10_000)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "first_name", "last_name", "birth_date", "phone", "enrollment_date"])
        for s in students:
            writer.writerow(
                [s.id, s.first_name, s.last_name, s.birth_date or "", s.phone or "", s.enrollment_date]
            )
        return buffer.getvalue()
