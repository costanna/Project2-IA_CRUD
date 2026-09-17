def _create_course(client, admin_headers, name="Algoritmia"):
    response = client.post("/api/v1/courses", headers=admin_headers, json={"name": name, "credits": 3})
    return response.json()["id"]


def test_admin_puede_crear_horario(client, admin):
    course_id = _create_course(client, admin.headers)

    response = client.post(
        "/api/v1/schedules",
        headers=admin.headers,
        json={
            "course_id": course_id,
            "day_of_week": "monday",
            "start_time": "09:00:00",
            "end_time": "11:00:00",
            "classroom": "A-101",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["day_of_week"] == "monday"
    assert body["classroom"] == "A-101"


def test_estudiante_no_puede_crear_horario(client, student):
    response = client.post(
        "/api/v1/schedules",
        headers=student.headers,
        json={
            "course_id": 1,
            "day_of_week": "monday",
            "start_time": "09:00:00",
            "end_time": "11:00:00",
        },
    )
    assert response.status_code == 403


def test_crear_horario_con_curso_inexistente_devuelve_404(client, admin):
    response = client.post(
        "/api/v1/schedules",
        headers=admin.headers,
        json={
            "course_id": 999,
            "day_of_week": "friday",
            "start_time": "10:00:00",
            "end_time": "12:00:00",
        },
    )
    assert response.status_code == 404


def test_listar_y_filtrar_horarios_por_curso(client, admin):
    course_id = _create_course(client, admin.headers)
    other_course_id = _create_course(client, admin.headers, name="Redes")
    client.post(
        "/api/v1/schedules",
        headers=admin.headers,
        json={
            "course_id": course_id,
            "day_of_week": "tuesday",
            "start_time": "08:00:00",
            "end_time": "10:00:00",
        },
    )
    client.post(
        "/api/v1/schedules",
        headers=admin.headers,
        json={
            "course_id": other_course_id,
            "day_of_week": "wednesday",
            "start_time": "08:00:00",
            "end_time": "10:00:00",
        },
    )

    response = client.get(f"/api/v1/schedules?course_id={course_id}", headers=admin.headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["course_id"] == course_id


def test_borrar_horario(client, admin):
    course_id = _create_course(client, admin.headers)
    schedule = client.post(
        "/api/v1/schedules",
        headers=admin.headers,
        json={
            "course_id": course_id,
            "day_of_week": "thursday",
            "start_time": "09:00:00",
            "end_time": "11:00:00",
        },
    ).json()

    response = client.delete(f"/api/v1/schedules/{schedule['id']}", headers=admin.headers)
    assert response.status_code == 204
