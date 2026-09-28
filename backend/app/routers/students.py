from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user, require_roles
from app.exceptions import NotFoundError
from app.models.student import Student
from app.models.user import User, UserRole
from app.schemas.common import Page
from app.schemas.student import StudentCreate, StudentRead, StudentUpdate
from app.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["students"])

staff_only = require_roles(UserRole.ADMIN, UserRole.TEACHER)
admin_only = require_roles(UserRole.ADMIN)


@router.get("/me", response_model=StudentRead)
def get_my_student_profile(current_user: User = Depends(get_current_user)) -> Student:
    """Permite a un estudiante autenticado conocer su propio student_id,
    necesario para matricularse en cursos desde el frontend."""
    if not current_user.student_profile:
        raise NotFoundError("El usuario autenticado no tiene un perfil de estudiante asociado.")
    return current_user.student_profile


@router.get("", response_model=Page[StudentRead], dependencies=[Depends(staff_only)])
def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> Page:
    items, total = StudentService(db).list(skip, limit)
    return Page(items=items, total=total, skip=skip, limit=limit)


@router.get("/export", dependencies=[Depends(staff_only)])
def export_students(db: Session = Depends(get_db)) -> StreamingResponse:
    csv_data = StudentService(db).export_csv()
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=students.csv"},
    )


@router.get("/{student_id}", response_model=StudentRead, dependencies=[Depends(staff_only)])
def get_student(student_id: int, db: Session = Depends(get_db)) -> Student:
    return StudentService(db).get(student_id)


@router.post("", response_model=StudentRead, status_code=201, dependencies=[Depends(admin_only)])
def create_student(data: StudentCreate, db: Session = Depends(get_db)) -> Student:
    return StudentService(db).create(data)


@router.put("/{student_id}", response_model=StudentRead, dependencies=[Depends(admin_only)])
def update_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)) -> Student:
    return StudentService(db).update(student_id, data)


@router.delete("/{student_id}", status_code=204, dependencies=[Depends(admin_only)])
def delete_student(student_id: int, db: Session = Depends(get_db)) -> None:
    StudentService(db).delete(student_id)
