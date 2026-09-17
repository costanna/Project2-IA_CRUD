from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.schedule import Schedule
from app.repositories.course_repository import CourseRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.schedule import ScheduleCreate


class ScheduleService:
    def __init__(self, db: Session):
        self.db = db
        self.schedules = ScheduleRepository(db)
        self.courses = CourseRepository(db)

    def list(self, skip: int, limit: int, course_id: int | None = None) -> tuple[list[Schedule], int]:
        return self.schedules.list(skip=skip, limit=limit, course_id=course_id)

    def get(self, schedule_id: int) -> Schedule:
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            raise NotFoundError(f"Horario {schedule_id} no encontrado.")
        return schedule

    def create(self, data: ScheduleCreate) -> Schedule:
        if not self.courses.get(data.course_id):
            raise NotFoundError(f"Curso {data.course_id} no encontrado.")
        return self.schedules.create(Schedule(**data.model_dump()))

    def delete(self, schedule_id: int) -> None:
        schedule = self.get(schedule_id)
        self.schedules.delete(schedule)
