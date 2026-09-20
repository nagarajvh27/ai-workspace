import logging

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import ai_workspace.api as api
from ai_workspace.api import DocumentCreate, app


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_document_store():
    api.document_repository.clear()

    yield

    api.document_repository.clear()


def document_payload() -> dict[str, str]:
    return {
        "title": "Design notes",
        "content": "First draft",
        "author_name": "Ada Lovelace",
    }


def test_get_health_returns_ok_status_and_body():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_documents_returns_empty_collection():
    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == []


def test_document_create_deserializes_valid_payload():
    payload = document_payload()

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
    payload = document_payload()
    payload[server_owned_field] = value

    with pytest.raises(ValidationError):
        DocumentCreate.model_validate(payload)


def test_create_document_returns_created_response_and_location():
    response = client.post("/documents", json=document_payload())

    assert response.status_code == 201
    assert response.headers["location"] == "/documents/1"
    assert response.json() == {
        "id": 1,
        "title": "Design notes",
        "content": "First draft",
        "author_name": "Ada Lovelace",
        "is_published": False,
    }


def test_get_document_returns_created_document():
    created_response = client.post("/documents", json=document_payload())

    response = client.get(created_response.headers["location"])

    assert response.status_code == 200
    assert response.json() == created_response.json()


def test_list_documents_returns_created_document():
    created_response = client.post("/documents", json=document_payload())

    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == [created_response.json()]


def test_get_missing_document_returns_not_found():
    response = client.get("/documents/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_create_document_returns_unprocessable_for_domain_error(
    caplog,
):
    caplog.set_level(logging.INFO, logger=api.__name__)
    payload = document_payload()
    payload["author_name"] = "   "

    response = client.post("/documents", json=payload)

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Author name cannot be blank"
    }
    assert api.document_repository.list_all() == []

    records = [
        record
        for record in caplog.records
        if getattr(record, "event", None)
        == "document_creation_rejected"
    ]

    assert len(records) == 1
    record = records[0]
    assert record.operation == "create_document"
    assert record.failure_category == "domain_validation"
    assert record.http_status == 422
    assert record.exception_type == "DomainValidationError"


def test_create_document_rejects_client_supplied_id():
    response = client.post(
        "/documents",
        json={**document_payload(), "id": 1},
    )

    assert response.status_code == 422


def test_create_document_rejects_missing_required_field():
    payload = document_payload()
    del payload["author_name"]

    response = client.post("/documents", json=payload)

    assert response.status_code == 422


def test_create_document_does_not_translate_unexpected_value_error(
    monkeypatch,
    caplog,
):
    caplog.set_level(logging.INFO, logger=api.__name__)
    internal_detail = "sensitive-internal-detail"

    def fail_create_document(**_kwargs):
        raise ValueError(internal_detail)

    monkeypatch.setattr(
        api.document_service,
        "create_document",
        fail_create_document,
    )
    error_client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    response = error_client.post(
        "/documents",
        json=document_payload(),
    )

    assert response.status_code == 500
    assert internal_detail not in response.text
    assert all(
        getattr(record, "event", None)
        != "document_creation_rejected"
        for record in caplog.records
    )
