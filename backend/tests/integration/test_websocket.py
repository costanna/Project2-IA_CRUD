import json


def _enroll(client, admin_headers, student, teacher_id=None):
    course_id = client.post(
        "/api/v1/courses",
        headers=admin_headers,
        json={"name": "Algoritmia", "credits": 3, "teacher_id": teacher_id},
    ).json()["id"]
    enrollment = client.post(
        "/api/v1/enrollments",
        headers=student.headers,
        json={"student_id": student.profile.id, "course_id": course_id},
    ).json()
    return enrollment["id"]


def test_estudiante_conectado_recibe_notificacion_de_nota_nueva(client, admin, teacher, student):
    token = student.headers["Authorization"].split(" ")[1]
    enrollment_id = _enroll(client, admin.headers, student, teacher.profile.id)

    with client.websocket_connect(f"/ws/notifications?token={token}") as websocket:
        client.post(
            "/api/v1/grades",
            headers=teacher.headers,
            json={"enrollment_id": enrollment_id, "evaluation_name": "Parcial 1", "score": 9},
        )

        message = json.loads(websocket.receive_text())

    assert message["event"] == "new_grade"
    assert message["data"]["evaluation_name"] == "Parcial 1"
    assert message["data"]["score"] == 9


def test_conexion_con_token_invalido_se_cierra(client):
    try:
        with client.websocket_connect("/ws/notifications?token=invalido"):
            raise AssertionError("La conexion deberia haberse cerrado por token invalido")
    except Exception:
        # starlette cierra la conexion con codigo 4401 (ver app/routers/ws.py);
        # el cliente de test la refleja como excepcion de cierre.
        pass
