from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import configure_logging, logger
from app.db.session import Base, engine
from app.exceptions import AppError, app_error_handler, unhandled_exception_handler
from app.routers import auth, courses, enrollments, grades, schedules, students, teachers, ws

configure_logging()

app = FastAPI(
    title=settings.app_name,
    description=(
        "API REST para la gestion academica de un centro educativo: "
        "estudiantes, profesores, cursos, horarios, matriculas y notas."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(students.router, prefix=settings.api_v1_prefix)
app.include_router(teachers.router, prefix=settings.api_v1_prefix)
app.include_router(courses.router, prefix=settings.api_v1_prefix)
app.include_router(schedules.router, prefix=settings.api_v1_prefix)
app.include_router(enrollments.router, prefix=settings.api_v1_prefix)
app.include_router(grades.router, prefix=settings.api_v1_prefix)
app.include_router(ws.router)


@app.on_event("startup")
def on_startup() -> None:
    # En un proyecto con Alembic configurado, las migraciones se aplican con
    # `alembic upgrade head` antes de arrancar. `create_all` queda como red
    # de seguridad para entornos de desarrollo/tests sin migraciones.
    Base.metadata.create_all(bind=engine)
    logger.info("%s iniciada en entorno '%s'", settings.app_name, settings.environment)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
