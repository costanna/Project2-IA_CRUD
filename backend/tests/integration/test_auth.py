def test_register_creates_user_with_student_role_by_default(client):
    response = client.post(
        "/api/v1/auth/register", json={"email": "nuevo@academiaf5.dev", "password": "clave12345"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "nuevo@academiaf5.dev"
    assert body["role"] == "student"


def test_register_con_email_duplicado_devuelve_409(client):
    payload = {"email": "dup@academiaf5.dev", "password": "clave12345"}
    client.post("/api/v1/auth/register", json=payload)

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409


def test_login_con_credenciales_correctas_devuelve_token(client):
    client.post("/api/v1/auth/register", json={"email": "login@academiaf5.dev", "password": "clave12345"})

    response = client.post(
        "/api/v1/auth/login", data={"username": "login@academiaf5.dev", "password": "clave12345"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_con_password_incorrecta_devuelve_401(client):
    client.post("/api/v1/auth/register", json={"email": "login2@academiaf5.dev", "password": "clave12345"})

    response = client.post(
        "/api/v1/auth/login", data={"username": "login2@academiaf5.dev", "password": "incorrecta"}
    )

    assert response.status_code == 401


def test_me_sin_token_devuelve_401(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_con_token_devuelve_el_usuario_autenticado(client):
    client.post("/api/v1/auth/register", json={"email": "me@academiaf5.dev", "password": "clave12345"})
    login = client.post(
        "/api/v1/auth/login", data={"username": "me@academiaf5.dev", "password": "clave12345"}
    )
    token = login.json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "me@academiaf5.dev"
