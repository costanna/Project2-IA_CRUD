def test_estudiante_puede_ver_su_propio_perfil(client, student):
    response = client.get("/api/v1/students/me", headers=student.headers)

    assert response.status_code == 200
    assert response.json()["id"] == student.profile.id


def test_admin_sin_perfil_de_estudiante_recibe_404_en_me(client, admin):
    response = client.get("/api/v1/students/me", headers=admin.headers)
    assert response.status_code == 404
