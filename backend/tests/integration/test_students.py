def test_admin_puede_crear_y_listar_estudiantes(client, admin):
    response = client.post(
        "/api/v1/students",
        headers=admin.headers,
        json={
            "email": "ana@academiaf5.dev",
            "password": "clave12345",
            "first_name": "Ana",
            "last_name": "Perez",
        },
    )
    assert response.status_code == 201

    listing = client.get("/api/v1/students", headers=admin.headers)
    assert listing.status_code == 200
    body = listing.json()
    assert body["total"] == 1
    assert body["items"][0]["first_name"] == "Ana"


def test_estudiante_no_puede_listar_estudiantes(client, student):
    response = client.get("/api/v1/students", headers=student.headers)
    assert response.status_code == 403


def test_sin_token_devuelve_401(client):
    response = client.get("/api/v1/students")
    assert response.status_code == 401


def test_profesor_puede_ver_pero_no_crear_estudiantes(client, teacher):
    listing = client.get("/api/v1/students", headers=teacher.headers)
    assert listing.status_code == 200

    creation = client.post(
        "/api/v1/students",
        headers=teacher.headers,
        json={
            "email": "otro@academiaf5.dev",
            "password": "clave12345",
            "first_name": "Luis",
            "last_name": "Diaz",
        },
    )
    assert creation.status_code == 403


def test_get_estudiante_inexistente_devuelve_404(client, admin):
    response = client.get("/api/v1/students/999", headers=admin.headers)
    assert response.status_code == 404


def test_actualizar_y_borrar_estudiante(client, admin, student):
    update = client.put(
        f"/api/v1/students/{student.profile.id}",
        headers=admin.headers,
        json={"phone": "600111222"},
    )
    assert update.status_code == 200
    assert update.json()["phone"] == "600111222"

    delete = client.delete(f"/api/v1/students/{student.profile.id}", headers=admin.headers)
    assert delete.status_code == 204

    get_after_delete = client.get(f"/api/v1/students/{student.profile.id}", headers=admin.headers)
    assert get_after_delete.status_code == 404


def test_export_students_devuelve_csv(client, admin, student):
    response = client.get("/api/v1/students/export", headers=admin.headers)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "Grace" in response.text
