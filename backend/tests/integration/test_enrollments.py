def _create_course(client, admin_headers, name="Algoritmia", teacher_id=None):
    response = client.post(
        "/api/v1/courses", headers=admin_headers, json={"name": name, "credits": 3, "teacher_id": teacher_id}
    )
    return response.json()["id"]


def test_matricular_estudiante_en_curso(client, admin, student):
    course_id = _create_course(client, admin.headers)

    response = client.post(
        "/api/v1/enrollments",
        headers=student.headers,
        json={"student_id": student.profile.id, "course_id": course_id},
    )

    assert response.status_code == 201
    assert response.json()["status"] == "active"


def test_matricula_duplicada_devuelve_409(client, admin, student):
    course_id = _create_course(client, admin.headers)
    payload = {"student_id": student.profile.id, "course_id": course_id}
    client.post("/api/v1/enrollments", headers=student.headers, json=payload)

    response = client.post("/api/v1/enrollments", headers=student.headers, json=payload)

    assert response.status_code == 409


def test_matricula_con_curso_inexistente_devuelve_404(client, student):
    response = client.post(
        "/api/v1/enrollments",
        headers=student.headers,
        json={"student_id": student.profile.id, "course_id": 999},
    )
    assert response.status_code == 404


def test_profesor_puede_cambiar_estado_de_matricula(client, admin, teacher, student):
    course_id = _create_course(client, admin.headers, teacher_id=teacher.profile.id)
    enrollment = client.post(
        "/api/v1/enrollments",
        headers=student.headers,
        json={"student_id": student.profile.id, "course_id": course_id},
    ).json()

    response = client.put(
        f"/api/v1/enrollments/{enrollment['id']}", headers=teacher.headers, json={"status": "completed"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_estudiante_no_puede_cambiar_estado_de_matricula(client, admin, student):
    course_id = _create_course(client, admin.headers)
    enrollment = client.post(
        "/api/v1/enrollments",
        headers=student.headers,
        json={"student_id": student.profile.id, "course_id": course_id},
    ).json()

    response = client.put(
        f"/api/v1/enrollments/{enrollment['id']}", headers=student.headers, json={"status": "dropped"}
    )

    assert response.status_code == 403


def test_filtrar_matriculas_por_curso(client, admin, student):
    course_id = _create_course(client, admin.headers)
    client.post(
        "/api/v1/enrollments",
        headers=student.headers,
        json={"student_id": student.profile.id, "course_id": course_id},
    )

    response = client.get(f"/api/v1/enrollments?course_id={course_id}", headers=admin.headers)

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_profesor_no_puede_gestionar_matriculas_de_cursos_ajenos(client, admin, teacher, student):
    course_id = _create_course(client, admin.headers)  # sin profesor asignado
    enrollment = client.post(
        "/api/v1/enrollments",
        headers=admin.headers,
        json={"student_id": student.profile.id, "course_id": course_id},
    ).json()

    update = client.put(
        f"/api/v1/enrollments/{enrollment['id']}", headers=teacher.headers, json={"status": "dropped"}
    )
    delete = client.delete(f"/api/v1/enrollments/{enrollment['id']}", headers=teacher.headers)
    create = client.post(
        "/api/v1/enrollments",
        headers=teacher.headers,
        json={"student_id": student.profile.id, "course_id": _create_course(client, admin.headers, "Otro")},
    )

    assert (update.status_code, delete.status_code, create.status_code) == (403, 403, 403)


def test_profesor_solo_ve_matriculas_de_sus_cursos(client, admin, teacher, student):
    own = _create_course(client, admin.headers, "Mio", teacher_id=teacher.profile.id)
    other = _create_course(client, admin.headers, "Ajeno")
    for course_id in (own, other):
        client.post(
            "/api/v1/enrollments",
            headers=admin.headers,
            json={"student_id": student.profile.id, "course_id": course_id},
        )

    listing = client.get("/api/v1/enrollments", headers=teacher.headers).json()

    assert listing["total"] == 1
    assert listing["items"][0]["course_name"] == "Mio"
