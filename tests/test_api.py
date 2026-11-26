import logging

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import ai_workspace.api as api
from ai_workspace.api import DocumentCreate, create_app
from ai_workspace.repositories import InMemoryDocumentRepository
from ai_workspace.services import DocumentService


@pytest.fixture
def document_repository() -> InMemoryDocumentRepository:
    return InMemoryDocumentRepository()


@pytest.fixture
def document_service(
    document_repository: InMemoryDocumentRepository,
) -> DocumentService:
    return DocumentService(document_repository)


@pytest.fixture
def client(
    document_service: DocumentService,
) -> TestClient:
    return TestClient(create_app(document_service))


def document_payload() -> dict[str, str]:
    return {
        "title": "Design notes",
        "content": "First draft",
        "author_name": "Ada Lovelace",
    }


def test_get_health_returns_ok_status_and_body(
    client: TestClient,
) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_documents_returns_empty_collection(
    client: TestClient,
) -> None:
    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == []


def test_document_create_deserializes_valid_payload() -> None:
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
    server_owned_field,
    value,
) -> None:
    payload = document_payload()
    payload[server_owned_field] = value

    with pytest.raises(ValidationError):
        DocumentCreate.model_validate(payload)


def test_create_document_returns_created_response_and_location(
    client: TestClient,
) -> None:
    response = client.post(
        "/documents",
        json=document_payload(),
    )

    assert response.status_code == 201
    assert response.headers["location"] == "/documents/1"
    assert response.json() == {
        "id": 1,
        "title": "Design notes",
        "content": "First draft",
        "author_name": "Ada Lovelace",
        "is_published": False,
    }


def test_get_document_returns_created_document(
    client: TestClient,
) -> None:
    created_response = client.post(
        "/documents",
        json=document_payload(),
    )

    response = client.get(
        created_response.headers["location"]
    )

    assert response.status_code == 200
    assert response.json() == created_response.json()


def test_list_documents_returns_created_document(
    client: TestClient,
) -> None:
    created_response = client.post(
        "/documents",
        json=document_payload(),
    )

    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == [created_response.json()]


@pytest.mark.parametrize(
    ("params", "expected_titles"),
    [
        ({}, ["Draft", "Published"]),
        ({"published": "false"}, ["Draft"]),
        ({"published": "true"}, ["Published"]),
    ],
)
def test_list_documents_filters_by_published_status(
    client: TestClient,
    params: dict[str, str],
    expected_titles: list[str],
) -> None:
    draft = client.post("/documents", json={**document_payload(), "title": "Draft"})
    to_publish = client.post(
        "/documents", json={**document_payload(), "title": "Published"}
    )
    assert draft.status_code == 201
    assert to_publish.status_code == 201
    assert client.post(f"{to_publish.headers['location']}/publish").status_code == 200

    response = client.get("/documents", params=params)

    assert response.status_code == 200
    assert [document["title"] for document in response.json()] == expected_titles


def test_list_documents_rejects_invalid_published_filter(client: TestClient) -> None:
    response = client.get("/documents", params={"published": "maybe"})

    assert response.status_code == 422


def test_edit_draft_document_content(client: TestClient) -> None:
    created_response = client.post("/documents", json=document_payload())
    assert created_response.status_code == 201
    document_url = created_response.headers["location"]

    edit_response = client.patch(
        document_url,
        json={"content": "Updated draft"},
    )

    assert edit_response.status_code == 200
    retrieved_response = client.get(document_url)
    assert retrieved_response.status_code == 200
    assert retrieved_response.json()["content"] == "Updated draft"


def test_publish_draft_document(client: TestClient) -> None:
    created = client.post("/documents", json=document_payload())
    assert created.status_code == 201
    document_url = created.headers["location"]

    published = client.post(f"{document_url}/publish")
    assert published.status_code == 200

    retrieved = client.get(document_url)
    assert retrieved.status_code == 200
    assert retrieved.json()["is_published"] is True


def test_publish_already_published_document_returns_conflict(
    client: TestClient,
) -> None:
    created = client.post("/documents", json=document_payload())
    assert created.status_code == 201
    document_url = created.headers["location"]
    publish_url = f"{document_url}/publish"
    published = client.post(publish_url)
    assert published.status_code == 200

    repeated = client.post(publish_url)

    assert repeated.status_code == 409
    assert repeated.json() == {"detail": "Document is already published"}
    retrieved = client.get(document_url)
    assert retrieved.status_code == 200
    assert retrieved.json() == published.json()


def test_publish_missing_document_returns_not_found(client: TestClient) -> None:
    response = client.post("/documents/999/publish")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_edit_published_document_keeps_original_content(
    client: TestClient,
    document_repository: InMemoryDocumentRepository,
) -> None:
    created_response = client.post("/documents", json=document_payload())
    assert created_response.status_code == 201
    original = created_response.json()
    document = document_repository.get(original["id"])
    assert document is not None
    document.publish()
    document_url = created_response.headers["location"]

    edit_response = client.patch(document_url, json={"content": "Updated draft"})

    assert edit_response.status_code == 409
    assert edit_response.json() == {"detail": "Cannot modify a published document"}
    retrieved_response = client.get(document_url)
    assert retrieved_response.status_code == 200
    assert retrieved_response.json() == {**original, "is_published": True}


def test_edit_missing_document_returns_not_found(client: TestClient) -> None:
    response = client.patch("/documents/999", json={"content": "Updated draft"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_edit_document_rejects_fields_other_than_content(client: TestClient) -> None:
    created_response = client.post("/documents", json=document_payload())
    assert created_response.status_code == 201
    document_url = created_response.headers["location"]

    response = client.patch(
        document_url, json={"content": "Updated draft", "is_published": True}
    )

    assert response.status_code == 422
    assert client.get(document_url).json() == created_response.json()


def test_get_missing_document_returns_not_found(
    client: TestClient,
) -> None:
    response = client.get("/documents/1")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found"
    }


def test_create_document_returns_unprocessable_for_domain_error(
    client: TestClient,
    document_repository: InMemoryDocumentRepository,
    caplog,
) -> None:
    caplog.set_level(logging.INFO, logger=api.__name__)
    payload = document_payload()
    payload["author_name"] = "   "

    response = client.post("/documents", json=payload)

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Author name cannot be blank"
    }
    assert document_repository.list_all() == []

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


def test_create_document_rejects_client_supplied_id(
    client: TestClient,
) -> None:
    response = client.post(
        "/documents",
        json={**document_payload(), "id": 1},
    )

    assert response.status_code == 422


def test_create_document_rejects_missing_required_field(
    client: TestClient,
) -> None:
    payload = document_payload()
    del payload["author_name"]

    response = client.post("/documents", json=payload)

    assert response.status_code == 422


def test_create_document_does_not_translate_unexpected_value_error(
    document_service: DocumentService,
    monkeypatch,
    caplog,
) -> None:
    caplog.set_level(logging.INFO, logger=api.__name__)
    internal_detail = "sensitive-internal-detail"

    def fail_create_document(**_kwargs):
        raise ValueError(internal_detail)

    monkeypatch.setattr(
        document_service,
        "create_document",
        fail_create_document,
    )
    error_client = TestClient(
        create_app(document_service),
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
