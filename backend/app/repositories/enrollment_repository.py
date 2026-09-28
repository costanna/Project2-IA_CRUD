from sqlalchemy import func, select

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.repositories.base import BaseRepository


class EnrollmentRepository(BaseRepository[Enrollment]):
    model = Enrollment

    def get_by_student_and_course(self, student_id: int, course_id: int) -> Enrollment | None:
        return (
            self.db.query(Enrollment)
            .filter(Enrollment.student_id == student_id, Enrollment.course_id == course_id)
            .first()
        )

    def list_scoped(
        self,
        skip: int = 0,
        limit: int = 20,
        student_id: int | None = None,
        course_id: int | None = None,
        teacher_id: int | None = None,
    ) -> tuple[list[Enrollment], int]:
        """Matriculas filtradas; `teacher_id` limita a los cursos de ese profesor."""
        stmt = select(Enrollment)
        if teacher_id is not None:
            stmt = stmt.join(Course).where(Course.teacher_id == teacher_id)
        if student_id is not None:
            stmt = stmt.where(Enrollment.student_id == student_id)
        if course_id is not None:
            stmt = stmt.where(Enrollment.course_id == course_id)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = self.db.scalars(stmt.order_by(Enrollment.id).offset(skip).limit(limit)).all()
        return list(items), total
