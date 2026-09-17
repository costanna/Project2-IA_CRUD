from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user, require_roles
from app.models.grade import Grade
from app.models.user import UserRole
from app.schemas.common import Page
from app.schemas.grade import GradeCreate, GradeRead, GradeUpdate
from app.services.grade_service import GradeService

router = APIRouter(prefix="/grades", tags=["grades"])

staff_only = require_roles(UserRole.ADMIN, UserRole.TEACHER)


@router.get("", response_model=Page[GradeRead], dependencies=[Depends(get_current_user)])
def list_grades(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    enrollment_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Page:
    items, total = GradeService(db).list(skip, limit, enrollment_id=enrollment_id)
    return Page(items=items, total=total, skip=skip, limit=limit)


@router.post("", response_model=GradeRead, status_code=201, dependencies=[Depends(staff_only)])
async def create_grade(data: GradeCreate, db: Session = Depends(get_db)) -> Grade:
    return await GradeService(db).create(data)


@router.put("/{grade_id}", response_model=GradeRead, dependencies=[Depends(staff_only)])
def update_grade(grade_id: int, data: GradeUpdate, db: Session = Depends(get_db)) -> Grade:
    return GradeService(db).update(grade_id, data)


@router.delete("/{grade_id}", status_code=204, dependencies=[Depends(staff_only)])
def delete_grade(grade_id: int, db: Session = Depends(get_db)) -> None:
    GradeService(db).delete(grade_id)
