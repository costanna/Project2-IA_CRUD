from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.models.enrollment import Enrollment
from app.repositories.course_repository import CourseRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.student_repository import StudentRepository
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate


class EnrollmentService:
    def __init__(self, db: Session):
        self.db = db
        self.enrollments = EnrollmentRepository(db)
        self.students = StudentRepository(db)
        self.courses = CourseRepository(db)

    def list(
        self,
        skip: int,
        limit: int,
        student_id: int | None = None,
        course_id: int | None = None,
        teacher_id: int | None = None,
    ) -> tuple[list[Enrollment], int]:
        return self.enrollments.list_scoped(
            skip=skip, limit=limit, student_id=student_id, course_id=course_id, teacher_id=teacher_id
        )

    def get(self, enrollment_id: int) -> Enrollment:
        enrollment = self.enrollments.get(enrollment_id)
        if not enrollment:
            raise NotFoundError(f"Matricula {enrollment_id} no encontrada.")
        return enrollment

    def create(self, data: EnrollmentCreate) -> Enrollment:
        if not self.students.get(data.student_id):
            raise NotFoundError(f"Estudiante {data.student_id} no encontrado.")
        if not self.courses.get(data.course_id):
            raise NotFoundError(f"Curso {data.course_id} no encontrado.")
        if self.enrollments.get_by_student_and_course(data.student_id, data.course_id):
            raise ConflictError("El estudiante ya esta matriculado en este curso.")

        return self.enrollments.create(Enrollment(student_id=data.student_id, course_id=data.course_id))

    def update_status(self, enrollment_id: int, data: EnrollmentUpdate) -> Enrollment:
        enrollment = self.get(enrollment_id)
        return self.enrollments.update(enrollment, {"status": data.status})

    def delete(self, enrollment_id: int) -> None:
        enrollment = self.get(enrollment_id)
        self.enrollments.delete(enrollment)
