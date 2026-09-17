from app.models.student import Student
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    model = Student

    def get_by_user_id(self, user_id: int) -> Student | None:
        return self.db.query(Student).filter(Student.user_id == user_id).first()
