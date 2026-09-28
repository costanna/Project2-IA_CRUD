from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.grade import Grade
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.grade_repository import GradeRepository
from app.schemas.grade import GradeCreate, GradeUpdate
from app.services.notification_service import manager


class GradeService:
    def __init__(self, db: Session):
        self.db = db
        self.grades = GradeRepository(db)
        self.enrollments = EnrollmentRepository(db)

    def list(
        self, skip: int, limit: int, enrollment_id: int | None = None, student_id: int | None = None
    ) -> tuple[list[Grade], int]:
        if student_id is not None:
            return self.grades.list_for_student(
                student_id, skip=skip, limit=limit, enrollment_id=enrollment_id
            )
        return self.grades.list(skip=skip, limit=limit, enrollment_id=enrollment_id)

    def get(self, grade_id: int) -> Grade:
        grade = self.grades.get(grade_id)
        if not grade:
            raise NotFoundError(f"Nota {grade_id} no encontrada.")
        return grade

    async def create(self, data: GradeCreate) -> Grade:
        enrollment = self.enrollments.get(data.enrollment_id)
        if not enrollment:
            raise NotFoundError(f"Matricula {data.enrollment_id} no encontrada.")

        grade = self.grades.create(
            Grade(
                enrollment_id=data.enrollment_id,
                evaluation_name=data.evaluation_name,
                score=data.score,
            )
        )

        student_email = enrollment.student.user.email
        await manager.notify_user(
            student_email,
            event="new_grade",
            payload={
                "course": enrollment.course.name,
                "evaluation_name": grade.evaluation_name,
                "score": grade.score,
            },
        )
        return grade

    def update(self, grade_id: int, data: GradeUpdate) -> Grade:
        grade = self.get(grade_id)
        return self.grades.update(grade, data.model_dump(exclude_unset=True))

    def delete(self, grade_id: int) -> None:
        grade = self.get(grade_id)
        self.grades.delete(grade)
