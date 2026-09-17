from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user, require_roles
from app.models.enrollment import Enrollment
from app.models.user import UserRole
from app.schemas.common import Page
from app.schemas.enrollment import EnrollmentCreate, EnrollmentRead, EnrollmentUpdate
from app.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["enrollments"])

staff_only = require_roles(UserRole.ADMIN, UserRole.TEACHER)


@router.get("", response_model=Page[EnrollmentRead], dependencies=[Depends(get_current_user)])
def list_enrollments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    student_id: int | None = Query(default=None),
    course_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Page:
    items, total = EnrollmentService(db).list(skip, limit, student_id=student_id, course_id=course_id)
    return Page(items=items, total=total, skip=skip, limit=limit)


@router.post("", response_model=EnrollmentRead, status_code=201, dependencies=[Depends(get_current_user)])
def create_enrollment(data: EnrollmentCreate, db: Session = Depends(get_db)) -> Enrollment:
    return EnrollmentService(db).create(data)


@router.put("/{enrollment_id}", response_model=EnrollmentRead, dependencies=[Depends(staff_only)])
def update_enrollment(
    enrollment_id: int, data: EnrollmentUpdate, db: Session = Depends(get_db)
) -> Enrollment:
    return EnrollmentService(db).update_status(enrollment_id, data)


@router.delete("/{enrollment_id}", status_code=204, dependencies=[Depends(staff_only)])
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)) -> None:
    EnrollmentService(db).delete(enrollment_id)
