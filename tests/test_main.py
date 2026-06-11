import os

from fastapi.testclient import TestClient

# Establecer variable de entorno dummy antes de importar la app
os.environ["GEMINI_API_KEY"] = "DUMMY_KEY_FOR_TESTING"

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_endpoint(mocker):
    # Mockear la llamada a httpx para no hacer peticiones reales
    mock_httpx = mocker.patch("httpx.AsyncClient.get")
    mock_httpx_response = mocker.AsyncMock()
    mock_httpx_response.text = "<html><body><h1>Python is great</h1></body></html>"
    mock_httpx_response.raise_for_status.return_value = None
    mock_httpx.return_value = mock_httpx_response

    # Mockear la respuesta asíncrona de client.aio.models.generate_content
    mock_response = mocker.MagicMock()
    mock_response.text = "This is a mocked concise response about python."

    mock_generate = mocker.patch(
        'app.main.client.aio.models.generate_content',
        new_callable=mocker.AsyncMock,
        return_value=mock_response
    )

    response = client.post(
        "/ask",
        json={"url": "https://example.com/python", "question": "What is this about?"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "response": "This is a mocked concise response about python."
    }

    # Verificar que los mocks se llamaron
    mock_generate.assert_called_once()
    mock_httpx.assert_called_once_with("https://example.com/python")


def test_ask_endpoint_empty_question():
    response = client.post(
        "/ask",
        json={"url": "https://example.com", "question": "   "}
    )
    assert response.status_code == 400
    assert "Question cannot be empty" in response.json()["detail"]


def test_ask_endpoint_invalid_url():
    response = client.post(
        "/ask",
        json={"url": "not-a-url", "question": "What?"}
    )
    assert response.status_code == 422
