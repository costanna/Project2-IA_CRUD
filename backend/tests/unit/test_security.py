from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_hash_password_no_guarda_texto_plano():
    hashed = hash_password("mi-clave-segura")
    assert hashed != "mi-clave-segura"


def test_verify_password_acepta_la_contrasena_correcta():
    hashed = hash_password("mi-clave-segura")
    assert verify_password("mi-clave-segura", hashed) is True


def test_verify_password_rechaza_contrasena_incorrecta():
    hashed = hash_password("mi-clave-segura")
    assert verify_password("otra-clave", hashed) is False


def test_create_and_decode_access_token_roundtrip():
    token = create_access_token(subject="user@example.com", extra_claims={"role": "admin"})
    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "user@example.com"
    assert payload["role"] == "admin"


def test_decode_access_token_con_token_invalido_devuelve_none():
    assert decode_access_token("token-que-no-existe") is None
