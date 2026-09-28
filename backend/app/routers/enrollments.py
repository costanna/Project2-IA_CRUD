from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user, own_student_id, require_roles
from app.exceptions import ForbiddenError
from app.models.enrollment import Enrollment
from app.models.user import User, UserRole
from app.schemas.common import Page
from app.schemas.enrollment import EnrollmentCreate, EnrollmentRead, EnrollmentUpdate
from app.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["enrollments"])

staff_only = require_roles(UserRole.ADMIN, UserRole.TEACHER)


@router.get("", response_model=Page[EnrollmentRead])
def list_enrollments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    student_id: int | None = Query(default=None),
    course_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page:
    # Un estudiante solo ve sus propias matriculas, pida lo que pida.
    own_id = own_student_id(current_user)
    if own_id is not None:
        student_id = own_id
    items, total = EnrollmentService(db).list(skip, limit, student_id=student_id, course_id=course_id)
    return Page(items=items, total=total, skip=skip, limit=limit)


@router.post("", response_model=EnrollmentRead, status_code=201)
def create_enrollment(
    data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Enrollment:
    own_id = own_student_id(current_user)
    if own_id is not None and data.student_id != own_id:
        raise ForbiddenError("Un estudiante solo puede matricularse a si mismo.")
    return EnrollmentService(db).create(data)


@router.put("/{enrollment_id}", response_model=EnrollmentRead, dependencies=[Depends(staff_only)])
def update_enrollment(
    enrollment_id: int, data: EnrollmentUpdate, db: Session = Depends(get_db)
) -> Enrollment:
    return EnrollmentService(db).update_status(enrollment_id, data)


@router.delete("/{enrollment_id}", status_code=204, dependencies=[Depends(staff_only)])
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)) -> None:
    EnrollmentService(db).delete(enrollment_id)
