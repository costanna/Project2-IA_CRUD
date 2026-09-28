from datetime import time

from pydantic import BaseModel, ConfigDict

from app.models.schedule import DayOfWeek


class ScheduleCreate(BaseModel):
    course_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    classroom: str | None = None


class ScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    classroom: str | None
