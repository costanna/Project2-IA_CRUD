from sqlalchemy import func, select

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.repositories.base import BaseRepository


class GradeRepository(BaseRepository[Grade]):
    model = Grade

    def list_scoped(
        self,
        skip: int = 0,
        limit: int = 20,
        enrollment_id: int | None = None,
        student_id: int | None = None,
        teacher_id: int | None = None,
    ) -> tuple[list[Grade], int]:
        """Notas filtradas por matricula, por estudiante o por cursos de un profesor."""
        stmt = select(Grade).join(Enrollment)
        if teacher_id is not None:
            stmt = stmt.join(Course, Enrollment.course_id == Course.id).where(Course.teacher_id == teacher_id)
        if student_id is not None:
            stmt = stmt.where(Enrollment.student_id == student_id)
        if enrollment_id is not None:
            stmt = stmt.where(Grade.enrollment_id == enrollment_id)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = self.db.scalars(stmt.order_by(Grade.id).offset(skip).limit(limit)).all()
        return list(items), total
