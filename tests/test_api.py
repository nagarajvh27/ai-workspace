from fastapi.testclient import TestClient
import pytest
from pydantic import ValidationError
from ai_workspace.api import DocumentCreate, app


client = TestClient(app)


def test_get_health_returns_ok_status_and_body():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_documents_returns_empty_collection():
    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == []

def test_document_create_deserializes_valid_payload():
    payload = {
        "title": "Design notes",
        "content": "First draft",
        "author_name": "Ada Lovelace",
    }

    creation_request = DocumentCreate.model_validate(payload)

    assert creation_request.model_dump() == payload


@pytest.mark.parametrize(
    ("server_owned_field", "value"),
    [
        ("id", "client-chosen-id"),
        ("is_published", True),
    ],
)
def test_document_create_rejects_server_owned_fields(
    server_owned_field, value
):
    payload = {
        "title": "Design notes",
        "content": "First draft",
        "author_name": "Ada Lovelace",
        server_owned_field: value,
    }

    with pytest.raises(ValidationError):
        DocumentCreate.model_validate(payload)