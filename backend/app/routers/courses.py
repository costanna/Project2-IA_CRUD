from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user, require_roles
from app.models.course import Course
from app.models.user import UserRole
from app.schemas.common import Page
from app.schemas.course import CourseCreate, CourseRead, CourseUpdate
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["courses"])

admin_only = require_roles(UserRole.ADMIN)


@router.get("", response_model=Page[CourseRead], dependencies=[Depends(get_current_user)])
def list_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    teacher_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Page:
    """Lista cursos con paginacion y filtrado opcional por profesor.

    La respuesta se sirve desde cache en memoria (ver app.core.cache) para
    reducir la carga sobre la base de datos en listados muy solicitados.
    """
    items, total = CourseService(db).list(skip, limit, teacher_id=teacher_id)
    return Page(items=items, total=total, skip=skip, limit=limit)


@router.get("/export", dependencies=[Depends(admin_only)])
def export_courses(db: Session = Depends(get_db)) -> StreamingResponse:
    csv_data = CourseService(db).export_csv()
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=courses.csv"},
    )


@router.get("/{course_id}", response_model=CourseRead, dependencies=[Depends(get_current_user)])
def get_course(course_id: int, db: Session = Depends(get_db)) -> Course:
    return CourseService(db).get(course_id)


@router.post("", response_model=CourseRead, status_code=201, dependencies=[Depends(admin_only)])
def create_course(data: CourseCreate, db: Session = Depends(get_db)) -> Course:
    return CourseService(db).create(data)


@router.put("/{course_id}", response_model=CourseRead, dependencies=[Depends(admin_only)])
def update_course(course_id: int, data: CourseUpdate, db: Session = Depends(get_db)) -> Course:
    return CourseService(db).update(course_id, data)


@router.delete("/{course_id}", status_code=204, dependencies=[Depends(admin_only)])
def delete_course(course_id: int, db: Session = Depends(get_db)) -> None:
    CourseService(db).delete(course_id)
