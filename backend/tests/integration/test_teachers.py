def test_cualquier_autenticado_puede_listar_profesores(client, admin, teacher):
    response = client.get("/api/v1/teachers", headers=admin.headers)

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_sin_token_no_puede_listar_profesores(client):
    response = client.get("/api/v1/teachers")
    assert response.status_code == 401


def test_admin_puede_crear_profesor(client, admin):
    response = client.post(
        "/api/v1/teachers",
        headers=admin.headers,
        json={
            "email": "nuevo.profe@academiaf5.dev",
            "password": "clave12345",
            "first_name": "Marie",
            "last_name": "Curie",
            "specialty": "Fisica",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["first_name"] == "Marie"
    assert body["specialty"] == "Fisica"


def test_estudiante_no_puede_crear_profesor(client, student):
    response = client.post(
        "/api/v1/teachers",
        headers=student.headers,
        json={
            "email": "otro.profe@academiaf5.dev",
            "password": "clave12345",
            "first_name": "Isaac",
            "last_name": "Newton",
        },
    )
    assert response.status_code == 403


def test_crear_profesor_con_email_duplicado_devuelve_409(client, admin, teacher):
    response = client.post(
        "/api/v1/teachers",
        headers=admin.headers,
        json={
            "email": teacher.user.email,
            "password": "clave12345",
            "first_name": "Duplicado",
            "last_name": "Duplicado",
        },
    )
    assert response.status_code == 409


def test_get_profesor_inexistente_devuelve_404(client, admin):
    response = client.get("/api/v1/teachers/999", headers=admin.headers)
    assert response.status_code == 404


def test_actualizar_y_borrar_profesor(client, admin, teacher):
    update = client.put(
        f"/api/v1/teachers/{teacher.profile.id}",
        headers=admin.headers,
        json={"specialty": "Quimica"},
    )
    assert update.status_code == 200
    assert update.json()["specialty"] == "Quimica"

    delete = client.delete(f"/api/v1/teachers/{teacher.profile.id}", headers=admin.headers)
    assert delete.status_code == 204

    get_after_delete = client.get(f"/api/v1/teachers/{teacher.profile.id}", headers=admin.headers)
    assert get_after_delete.status_code == 404
