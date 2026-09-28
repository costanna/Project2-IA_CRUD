from sqlalchemy import func, select

from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.repositories.base import BaseRepository


class GradeRepository(BaseRepository[Grade]):
    model = Grade

    def list_for_student(
        self, student_id: int, skip: int = 0, limit: int = 20, enrollment_id: int | None = None
    ) -> tuple[list[Grade], int]:
        """Notas de las matriculas de un estudiante concreto."""
        stmt = select(Grade).join(Enrollment).where(Enrollment.student_id == student_id)
        if enrollment_id is not None:
            stmt = stmt.where(Grade.enrollment_id == enrollment_id)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = self.db.scalars(stmt.offset(skip).limit(limit)).all()
        return list(items), total
