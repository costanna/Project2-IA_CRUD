from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user, require_roles
from app.exceptions import NotFoundError
from app.models.teacher import Teacher
from app.models.user import User, UserRole
from app.schemas.common import Page
from app.schemas.teacher import TeacherCreate, TeacherRead, TeacherUpdate
from app.services.teacher_service import TeacherService

router = APIRouter(prefix="/teachers", tags=["teachers"])

staff_only = require_roles(UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT)
admin_only = require_roles(UserRole.ADMIN)


@router.get("", response_model=Page[TeacherRead], dependencies=[Depends(staff_only)])
def list_teachers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> Page:
    items, total = TeacherService(db).list(skip, limit)
    return Page(items=items, total=total, skip=skip, limit=limit)


@router.get("/me", response_model=TeacherRead)
def get_my_teacher_profile(current_user: User = Depends(get_current_user)) -> Teacher:
    """Perfil de profesor del usuario autenticado (para filtrar sus cursos en la web)."""
    if not current_user.teacher_profile:
        raise NotFoundError("El usuario autenticado no tiene un perfil de profesor asociado.")
    return current_user.teacher_profile


@router.get("/{teacher_id}", response_model=TeacherRead, dependencies=[Depends(staff_only)])
def get_teacher(teacher_id: int, db: Session = Depends(get_db)) -> Teacher:
    return TeacherService(db).get(teacher_id)


@router.post("", response_model=TeacherRead, status_code=201, dependencies=[Depends(admin_only)])
def create_teacher(data: TeacherCreate, db: Session = Depends(get_db)) -> Teacher:
    return TeacherService(db).create(data)


@router.put("/{teacher_id}", response_model=TeacherRead, dependencies=[Depends(admin_only)])
def update_teacher(teacher_id: int, data: TeacherUpdate, db: Session = Depends(get_db)) -> Teacher:
    return TeacherService(db).update(teacher_id, data)


@router.delete("/{teacher_id}", status_code=204, dependencies=[Depends(admin_only)])
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)) -> None:
    TeacherService(db).delete(teacher_id)
