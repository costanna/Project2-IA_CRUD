from app.models.teacher import Teacher
from app.repositories.base import BaseRepository


class TeacherRepository(BaseRepository[Teacher]):
    model = Teacher

    def get_by_user_id(self, user_id: int) -> Teacher | None:
        return self.db.query(Teacher).filter(Teacher.user_id == user_id).first()
