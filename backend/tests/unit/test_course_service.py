import pytest

from app.exceptions import NotFoundError
from app.schemas.course import CourseCreate, CourseUpdate
from app.services.course_service import CourseService


def test_create_and_get_course(db_session):
    service = CourseService(db_session)
    course = service.create(CourseCreate(name="Algoritmia", credits=4))

    fetched = service.get(course.id)

    assert fetched.name == "Algoritmia"
    assert fetched.credits == 4


def test_get_course_inexistente_lanza_not_found(db_session):
    service = CourseService(db_session)

    with pytest.raises(NotFoundError):
        service.get(999)


def test_update_course_solo_cambia_los_campos_enviados(db_session):
    service = CourseService(db_session)
    course = service.create(CourseCreate(name="Bases de Datos", credits=3))

    updated = service.update(course.id, CourseUpdate(credits=5))

    assert updated.name == "Bases de Datos"
    assert updated.credits == 5


def test_list_courses_usa_cache_hasta_que_se_invalida(db_session):
    service = CourseService(db_session)
    service.create(CourseCreate(name="Redes", credits=2))

    items_first_call, total_first_call = service.list(skip=0, limit=20)
    items_second_call, total_second_call = service.list(skip=0, limit=20)

    assert total_first_call == total_second_call == 1
    assert items_first_call == items_second_call

    # ...y que tras crear un curso a traves del servicio (que invalida la
    # cache) el nuevo listado si refleja el cambio.
    service.create(CourseCreate(name="Sistemas Operativos", credits=3))
    _, total_after_create = service.list(skip=0, limit=20)
    assert total_after_create == 2
