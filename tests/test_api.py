from fastapi.testclient import TestClient

from ai_workspace.api import app


client = TestClient(app)


def test_get_health_returns_ok_status_and_body():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}