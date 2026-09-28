from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user, own_student_id, require_roles
from app.models.grade import Grade
from app.models.user import User, UserRole
from app.schemas.common import Page
from app.schemas.grade import GradeCreate, GradeRead, GradeUpdate
from app.services.email_service import EmailService
from app.services.grade_service import GradeService

router = APIRouter(prefix="/grades", tags=["grades"])

staff_only = require_roles(UserRole.ADMIN, UserRole.TEACHER)


@router.get("", response_model=Page[GradeRead])
def list_grades(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    enrollment_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page:
    # Un estudiante solo ve las notas de sus propias matriculas.
    items, total = GradeService(db).list(
        skip, limit, enrollment_id=enrollment_id, student_id=own_student_id(current_user)
    )
    return Page(items=items, total=total, skip=skip, limit=limit)


@router.post("", response_model=GradeRead, status_code=201, dependencies=[Depends(staff_only)])
async def create_grade(
    data: GradeCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> Grade:
    grade = await GradeService(db).create(data)
    # El email se envia tras responder, para no hacer esperar al profesor.
    enrollment = grade.enrollment
    background_tasks.add_task(
        EmailService().send_new_grade,
        to=enrollment.student.user.email,
        student_name=enrollment.student.first_name,
        course=enrollment.course.name,
        evaluation=grade.evaluation_name,
        score=grade.score,
    )
    return grade


@router.put("/{grade_id}", response_model=GradeRead, dependencies=[Depends(staff_only)])
def update_grade(grade_id: int, data: GradeUpdate, db: Session = Depends(get_db)) -> Grade:
    return GradeService(db).update(grade_id, data)


@router.delete("/{grade_id}", status_code=204, dependencies=[Depends(staff_only)])
def delete_grade(grade_id: int, db: Session = Depends(get_db)) -> None:
    GradeService(db).delete(grade_id)
