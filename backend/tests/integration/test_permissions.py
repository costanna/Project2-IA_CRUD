"""Reglas de acceso por rol: registro, matriculas y notas de estudiantes."""

from app.core.security import create_access_token, hash_password
from app.models.student import Student
from app.models.user import User, UserRole


def _other_student(db_session):
    user = User(
        email="otro@academiaf5.dev", hashed_password=hash_password("otropass123"), role=UserRole.STUDENT
    )
    db_session.add(user)
    db_session.commit()
    profile = Student(user_id=user.id, first_name="Alan", last_name="Turing")
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    token = create_access_token(subject=user.email, extra_claims={"role": "student"})
    return profile, {"Authorization": f"Bearer {token}"}


def _course(client, admin_headers, name="Algoritmia"):
    return client.post("/api/v1/courses", headers=admin_headers, json={"name": name}).json()["id"]


# --- Registro -----------------------------------------------------------------


def test_primera_cuenta_puede_registrarse_como_admin(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "root@academiaf5.dev", "password": "clave12345", "role": "admin"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "admin"


def test_registro_publico_no_permite_crear_admin_si_ya_hay_usuarios(client, admin):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "intruso@academiaf5.dev", "password": "clave12345", "role": "admin"},
    )
    assert response.status_code == 403


def test_estudiante_no_puede_crear_cuentas_de_profesor(client, student):
    response = client.post(
        "/api/v1/auth/register",
        headers=student.headers,
        json={"email": "falso@academiaf5.dev", "password": "clave12345", "role": "teacher"},
    )
    assert response.status_code == 403


def test_admin_puede_crear_otro_admin(client, admin):
    response = client.post(
        "/api/v1/auth/register",
        headers=admin.headers,
        json={"email": "admin2@academiaf5.dev", "password": "clave12345", "role": "admin"},
    )
    assert response.status_code == 201


# --- Matriculas ---------------------------------------------------------------


def test_estudiante_no_puede_matricular_a_otro(client, admin, student, db_session):
    other, _ = _other_student(db_session)
    course_id = _course(client, admin.headers)

    response = client.post(
        "/api/v1/enrollments", headers=student.headers, json={"student_id": other.id, "course_id": course_id}
    )

    assert response.status_code == 403


def test_admin_puede_matricular_a_cualquier_estudiante(client, admin, student):
    course_id = _course(client, admin.headers)

    response = client.post(
        "/api/v1/enrollments",
        headers=admin.headers,
        json={"student_id": student.profile.id, "course_id": course_id},
    )

    assert response.status_code == 201
    assert response.json()["student_name"] == "Grace Hopper"
    assert response.json()["course_name"] == "Algoritmia"


def test_estudiante_solo_ve_sus_matriculas(client, admin, student, db_session):
    other, _ = _other_student(db_session)
    course_id = _course(client, admin.headers)
    for sid in (student.profile.id, other.id):
        client.post(
            "/api/v1/enrollments", headers=admin.headers, json={"student_id": sid, "course_id": course_id}
        )

    # Aunque pida las del otro estudiante, solo recibe las suyas.
    response = client.get(f"/api/v1/enrollments?student_id={other.id}", headers=student.headers)

    assert response.json()["total"] == 1
    assert response.json()["items"][0]["student_id"] == student.profile.id


# --- Notas --------------------------------------------------------------------


def test_estudiante_solo_ve_sus_notas(client, admin, student, db_session):
    other, other_headers = _other_student(db_session)
    course_id = _course(client, admin.headers)
    enrollment_ids = []
    for sid in (student.profile.id, other.id):
        enrollment = client.post(
            "/api/v1/enrollments", headers=admin.headers, json={"student_id": sid, "course_id": course_id}
        ).json()
        enrollment_ids.append(enrollment["id"])
        client.post(
            "/api/v1/grades",
            headers=admin.headers,
            json={"enrollment_id": enrollment["id"], "evaluation_name": "Parcial", "score": 7},
        )

    mine = client.get("/api/v1/grades", headers=student.headers).json()
    theirs = client.get(f"/api/v1/grades?enrollment_id={enrollment_ids[1]}", headers=student.headers).json()
    staff_view = client.get("/api/v1/grades", headers=admin.headers).json()

    assert mine["total"] == 1
    assert mine["items"][0]["enrollment_id"] == enrollment_ids[0]
    assert theirs["total"] == 0
    assert staff_view["total"] == 2


# --- Bajas y cursos -----------------------------------------------------------


def test_borrar_estudiante_elimina_tambien_su_cuenta(client, admin, student):
    client.delete(f"/api/v1/students/{student.profile.id}", headers=admin.headers)

    response = client.post(
        "/api/v1/auth/login", data={"username": "student@academiaf5.dev", "password": "studentpass123"}
    )

    assert response.status_code == 401


def test_asignar_y_quitar_profesor_de_un_curso(client, admin, teacher):
    course_id = _course(client, admin.headers)

    assigned = client.put(
        f"/api/v1/courses/{course_id}", headers=admin.headers, json={"teacher_id": teacher.profile.id}
    )
    removed = client.put(f"/api/v1/courses/{course_id}", headers=admin.headers, json={"teacher_id": None})

    assert assigned.json()["teacher_id"] == teacher.profile.id
    assert removed.json()["teacher_id"] is None


def test_asignar_profesor_inexistente_devuelve_404(client, admin):
    course_id = _course(client, admin.headers)

    response = client.put(f"/api/v1/courses/{course_id}", headers=admin.headers, json={"teacher_id": 999})

    assert response.status_code == 404
