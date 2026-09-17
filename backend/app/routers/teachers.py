from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_roles
from app.models.teacher import Teacher
from app.models.user import UserRole
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
