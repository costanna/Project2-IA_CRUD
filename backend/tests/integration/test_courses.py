def test_admin_puede_crear_curso_y_estudiante_puede_listarlo(client, admin, student):
    creation = client.post(
        "/api/v1/courses", headers=admin.headers, json={"name": "Algoritmia", "credits": 4}
    )
    assert creation.status_code == 201

    listing = client.get("/api/v1/courses", headers=student.headers)
    assert listing.status_code == 200
    assert listing.json()["total"] == 1


def test_estudiante_no_puede_crear_curso(client, student):
    response = client.post("/api/v1/courses", headers=student.headers, json={"name": "Redes", "credits": 2})
    assert response.status_code == 403


def test_paginacion_de_cursos(client, admin):
    for i in range(5):
        client.post("/api/v1/courses", headers=admin.headers, json={"name": f"Curso {i}", "credits": 1})

    page = client.get("/api/v1/courses?skip=2&limit=2", headers=admin.headers)

    assert page.status_code == 200
    body = page.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2
    assert body["skip"] == 2 and body["limit"] == 2


def test_filtro_por_profesor(client, admin, teacher):
    client.post(
        "/api/v1/courses",
        headers=admin.headers,
        json={"name": "Con profesor", "credits": 3, "teacher_id": teacher.profile.id},
    )
    client.post("/api/v1/courses", headers=admin.headers, json={"name": "Sin profesor", "credits": 1})

    filtered = client.get(f"/api/v1/courses?teacher_id={teacher.profile.id}", headers=admin.headers)

    assert filtered.status_code == 200
    body = filtered.json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Con profesor"


def test_actualizar_curso_invalida_la_cache(client, admin):
    created = client.post("/api/v1/courses", headers=admin.headers, json={"name": "Original", "credits": 1})
    course_id = created.json()["id"]

    # Forzamos que la primera lista quede cacheada.
    client.get("/api/v1/courses", headers=admin.headers)

    client.put(f"/api/v1/courses/{course_id}", headers=admin.headers, json={"name": "Actualizado"})

    listing = client.get("/api/v1/courses", headers=admin.headers)
    assert listing.json()["items"][0]["name"] == "Actualizado"


def test_borrar_curso_inexistente_devuelve_404(client, admin):
    response = client.delete("/api/v1/courses/999", headers=admin.headers)
    assert response.status_code == 404


def test_export_courses_devuelve_csv(client, admin):
    client.post("/api/v1/courses", headers=admin.headers, json={"name": "Exportable", "credits": 2})

    response = client.get("/api/v1/courses/export", headers=admin.headers)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "Exportable" in response.text
