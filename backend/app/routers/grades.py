from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import ensure_can_manage_course, get_current_user, own_student_id, own_teacher_id, require_roles
from app.models.grade import Grade
from app.models.user import User, UserRole
from app.schemas.common import Page
from app.schemas.grade import GradeCreate, GradeRead, GradeUpdate
from app.services.email_service import EmailService
from app.services.enrollment_service import EnrollmentService
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
    # Un estudiante solo ve sus notas; un profesor, las de sus cursos.
    items, total = GradeService(db).list(
        skip,
        limit,
        enrollment_id=enrollment_id,
        student_id=own_student_id(current_user),
        teacher_id=own_teacher_id(current_user),
    )
    return Page(items=items, total=total, skip=skip, limit=limit)


@router.post("", response_model=GradeRead, status_code=201)
async def create_grade(
    data: GradeCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(staff_only),
) -> Grade:
    ensure_can_manage_course(current_user, EnrollmentService(db).get(data.enrollment_id).course)
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


@router.put("/{grade_id}", response_model=GradeRead)
def update_grade(
    grade_id: int,
    data: GradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(staff_only),
) -> Grade:
    service = GradeService(db)
    ensure_can_manage_course(current_user, service.get(grade_id).enrollment.course)
    return service.update(grade_id, data)


@router.delete("/{grade_id}", status_code=204)
def delete_grade(
    grade_id: int, db: Session = Depends(get_db), current_user: User = Depends(staff_only)
) -> None:
    service = GradeService(db)
    ensure_can_manage_course(current_user, service.get(grade_id).enrollment.course)
    service.delete(grade_id)
