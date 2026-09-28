def _enroll(client, admin_headers, student):
    course_id = client.post(
        "/api/v1/courses", headers=admin_headers, json={"name": "Algoritmia", "credits": 3}
    ).json()["id"]
    enrollment = client.post(
        "/api/v1/enrollments",
        headers=student.headers,
        json={"student_id": student.profile.id, "course_id": course_id},
    ).json()
    return enrollment["id"]


def test_profesor_puede_registrar_nota(client, admin, teacher, student):
    enrollment_id = _enroll(client, admin.headers, student)

    response = client.post(
        "/api/v1/grades",
        headers=teacher.headers,
        json={"enrollment_id": enrollment_id, "evaluation_name": "Parcial 1", "score": 8.5},
    )

    assert response.status_code == 201
    assert response.json()["score"] == 8.5


def test_estudiante_no_puede_registrar_nota(client, admin, student):
    enrollment_id = _enroll(client, admin.headers, student)

    response = client.post(
        "/api/v1/grades",
        headers=student.headers,
        json={"enrollment_id": enrollment_id, "evaluation_name": "Parcial 1", "score": 9},
    )

    assert response.status_code == 403


def test_nota_fuera_de_rango_devuelve_422(client, admin, teacher, student):
    enrollment_id = _enroll(client, admin.headers, student)

    response = client.post(
        "/api/v1/grades",
        headers=teacher.headers,
        json={"enrollment_id": enrollment_id, "evaluation_name": "Parcial 1", "score": 15},
    )

    assert response.status_code == 422


def test_nota_con_matricula_inexistente_devuelve_404(client, teacher):
    response = client.post(
        "/api/v1/grades",
        headers=teacher.headers,
        json={"enrollment_id": 999, "evaluation_name": "Parcial 1", "score": 5},
    )
    assert response.status_code == 404


def test_actualizar_y_listar_notas_por_matricula(client, admin, teacher, student):
    enrollment_id = _enroll(client, admin.headers, student)
    grade = client.post(
        "/api/v1/grades",
        headers=teacher.headers,
        json={"enrollment_id": enrollment_id, "evaluation_name": "Parcial 1", "score": 6},
    ).json()

    update = client.put(f"/api/v1/grades/{grade['id']}", headers=teacher.headers, json={"score": 7.5})
    assert update.status_code == 200
    assert update.json()["score"] == 7.5

    listing = client.get(f"/api/v1/grades?enrollment_id={enrollment_id}", headers=student.headers)
    assert listing.status_code == 200
    assert listing.json()["total"] == 1


def test_registrar_nota_envia_email_al_estudiante(client, admin, teacher, student, monkeypatch):
    sent = []

    async def fake_send_new_grade(self, **kwargs):
        sent.append(kwargs)
        return True

    monkeypatch.setattr("app.services.email_service.EmailService.send_new_grade", fake_send_new_grade)
    course_id = client.post("/api/v1/courses", headers=admin.headers, json={"name": "React"}).json()["id"]
    enrollment_id = client.post(
        "/api/v1/enrollments",
        headers=admin.headers,
        json={"student_id": student.profile.id, "course_id": course_id},
    ).json()["id"]

    response = client.post(
        "/api/v1/grades",
        headers=teacher.headers,
        json={"enrollment_id": enrollment_id, "evaluation_name": "Parcial 1", "score": 9},
    )

    assert response.status_code == 201
    assert sent == [
        {
            "to": "student@academiaf5.dev",
            "student_name": "Grace",
            "course": "React",
            "evaluation": "Parcial 1",
            "score": 9.0,
        }
    ]
