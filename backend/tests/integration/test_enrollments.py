def _create_course(client, admin_headers, name="Algoritmia"):
    response = client.post("/api/v1/courses", headers=admin_headers, json={"name": name, "credits": 3})
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
    course_id = _create_course(client, admin.headers)
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
