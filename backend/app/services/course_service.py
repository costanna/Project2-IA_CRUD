import csv
import io

from sqlalchemy.orm import Session

from app.core.cache import cache_key, get_cached, invalidate_prefix, set_cached
from app.exceptions import NotFoundError
from app.models.course import Course
from app.models.teacher import Teacher
from app.repositories.course_repository import CourseRepository
from app.schemas.course import CourseCreate, CourseUpdate

CACHE_PREFIX = "courses"


class CourseService:
    def __init__(self, db: Session):
        self.db = db
        self.courses = CourseRepository(db)

    def list(self, skip: int, limit: int, teacher_id: int | None = None) -> tuple[list[Course], int]:
        # Cache de lectura: las listas de cursos cambian poco y se piden mucho.
        key = cache_key(CACHE_PREFIX, skip, limit, teacher_id)
        cached = get_cached(key)
        if cached is not None:
            return cached

        result = self.courses.list(skip=skip, limit=limit, teacher_id=teacher_id)
        set_cached(key, result)
        return result

    def get(self, course_id: int) -> Course:
        course = self.courses.get(course_id)
        if not course:
            raise NotFoundError(f"Curso {course_id} no encontrado.")
        return course

    def _check_teacher(self, teacher_id: int | None) -> None:
        if teacher_id is not None and not self.db.get(Teacher, teacher_id):
            raise NotFoundError(f"Profesor {teacher_id} no encontrado.")

    def create(self, data: CourseCreate) -> Course:
        self._check_teacher(data.teacher_id)
        course = self.courses.create(Course(**data.model_dump()))
        invalidate_prefix(CACHE_PREFIX)
        return course

    def update(self, course_id: int, data: CourseUpdate) -> Course:
        course = self.get(course_id)
        changes = data.model_dump(exclude_unset=True)
        self._check_teacher(changes.get("teacher_id"))
        # El update generico ignora los None; quitar el profesor es explicito.
        if "teacher_id" in changes and changes["teacher_id"] is None:
            course.teacher_id = None
        updated = self.courses.update(course, changes)
        invalidate_prefix(CACHE_PREFIX)
        return updated

    def delete(self, course_id: int) -> None:
        course = self.get(course_id)
        self.courses.delete(course)
        invalidate_prefix(CACHE_PREFIX)

    def export_csv(self) -> str:
        """Genera un CSV en memoria con todos los cursos (Nivel Medio: exportacion a CSV)."""
        courses, _ = self.courses.list(skip=0, limit=10_000)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "name", "description", "credits", "teacher_id"])
        for c in courses:
            writer.writerow([c.id, c.name, c.description or "", c.credits, c.teacher_id or ""])
        return buffer.getvalue()
