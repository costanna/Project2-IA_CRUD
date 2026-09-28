from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user, require_roles
from app.models.schedule import Schedule
from app.models.user import UserRole
from app.schemas.common import Page
from app.schemas.schedule import ScheduleCreate, ScheduleRead
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/schedules", tags=["schedules"])

admin_only = require_roles(UserRole.ADMIN)


@router.get("", response_model=Page[ScheduleRead], dependencies=[Depends(get_current_user)])
def list_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    course_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Page:
    items, total = ScheduleService(db).list(skip, limit, course_id=course_id)
    return Page(items=items, total=total, skip=skip, limit=limit)


@router.post("", response_model=ScheduleRead, status_code=201, dependencies=[Depends(admin_only)])
def create_schedule(data: ScheduleCreate, db: Session = Depends(get_db)) -> Schedule:
    return ScheduleService(db).create(data)


@router.delete("/{schedule_id}", status_code=204, dependencies=[Depends(admin_only)])
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)) -> None:
    ScheduleService(db).delete(schedule_id)
