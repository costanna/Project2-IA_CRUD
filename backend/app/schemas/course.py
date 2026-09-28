from pydantic import BaseModel, ConfigDict


class CourseCreate(BaseModel):
    name: str
    description: str | None = None
    credits: int = 1
    teacher_id: int | None = None


class CourseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    credits: int | None = None
    teacher_id: int | None = None


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    credits: int
    teacher_id: int | None
