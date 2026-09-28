import asyncio
import json

import httpx

from app.services.email_service import RESEND_URL, EmailService


def _service(handler):
    return EmailService(
        api_key="re_test", sender="Academia <test@resend.dev>", transport=httpx.MockTransport(handler)
    )


def test_sin_api_key_no_envia_nada():
    calls = []
    service = EmailService(api_key="", transport=httpx.MockTransport(lambda r: calls.append(r)))

    assert asyncio.run(service.send("ana@academiaf5.dev", "Hola", "<p>Hola</p>")) is False
    assert calls == []


def test_envia_la_peticion_esperada_a_resend():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers["Authorization"]
        captured["body"] = json.loads(request.content)
        return httpx.Response(200, json={"id": "email_123"})

    sent = asyncio.run(
        _service(handler).send_new_grade("ana@academiaf5.dev", "Ana", "React", "Parcial 1", 8.5)
    )

    assert sent is True
    assert captured["url"] == RESEND_URL
    assert captured["auth"] == "Bearer re_test"
    assert captured["body"]["to"] == ["ana@academiaf5.dev"]
    assert captured["body"]["subject"] == "Nueva nota en React"
    assert "8.5" in captured["body"]["html"]


def test_un_error_del_proveedor_no_lanza_excepcion():
    sent = asyncio.run(
        _service(lambda r: httpx.Response(500)).send("ana@academiaf5.dev", "Hola", "<p>Hola</p>")
    )

    assert sent is False


def test_escapa_el_html_de_los_datos():
    captured = {}

    def handler(request):
        captured["html"] = json.loads(request.content)["html"]
        return httpx.Response(200, json={})

    asyncio.run(_service(handler).send_new_grade("a@b.dev", "<script>", "Curso", "Examen", 5))

    assert "<script>" not in captured["html"]
    assert "&lt;script&gt;" in captured["html"]
