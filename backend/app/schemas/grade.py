from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GradeCreate(BaseModel):
    enrollment_id: int
    evaluation_name: str
    score: float = Field(ge=0, le=10)


class GradeUpdate(BaseModel):
    evaluation_name: str | None = None
    score: float | None = Field(default=None, ge=0, le=10)


class GradeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    enrollment_id: int
    evaluation_name: str
    score: float
    date: datetime
