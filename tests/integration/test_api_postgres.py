import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import Engine


pytestmark = pytest.mark.integration


def document_payload() -> dict[str, str]:
    return {
        "title": "Integration test",
        "content": "Stored in PostgreSQL.",
        "author_name": "Ada Lovelace",
    }


def test_create_document_persists_to_postgresql(
    postgres_client: TestClient,
    postgres_engine: Engine,
) -> None:
    payload = document_payload()

    response = postgres_client.post(
        "/documents",
        json=payload,
    )

    assert response.status_code == 201

    created_document = response.json()
    document_id = created_document["id"]

    assert response.headers["location"] == (
        f"/documents/{document_id}"
    )

    with postgres_engine.connect() as connection:
        row = connection.execute(
            text(
                """
                SELECT
                    id,
                    title,
                    content,
                    author_name,
                    is_published
                FROM documents
                WHERE id = :document_id
                """
            ),
            {"document_id": document_id},
        ).mappings().one()

    assert dict(row) == {
        "id": document_id,
        "title": "Integration test",
        "content": "Stored in PostgreSQL.",
        "author_name": "Ada Lovelace",
        "is_published": False,
    }


def test_created_document_can_be_retrieved_and_listed(
    postgres_client: TestClient,
) -> None:
    created_response = postgres_client.post(
        "/documents",
        json=document_payload(),
    )
    assert created_response.status_code == 201

    created_document = created_response.json()

    retrieved_response = postgres_client.get(
        created_response.headers["location"]
    )
    listed_response = postgres_client.get("/documents")

    assert retrieved_response.status_code == 200
    assert retrieved_response.json() == created_document
    assert listed_response.status_code == 200
    assert listed_response.json() == [created_document]


@pytest.mark.parametrize(("is_published", "expected_status"), [(False, 200), (True, 409)])
def test_edit_document_content_in_postgresql(
    postgres_client: TestClient,
    postgres_engine: Engine,
    is_published: bool,
    expected_status: int,
) -> None:
    payload = document_payload()
    created_response = postgres_client.post("/documents", json=payload)
    assert created_response.status_code == 201
    document_url = created_response.headers["location"]
    document_id = created_response.json()["id"]

    with postgres_engine.begin() as connection:
        connection.execute(
            text("UPDATE documents SET is_published = :published WHERE id = :id"),
            {"published": is_published, "id": document_id},
        )

    response = postgres_client.patch(document_url, json={"content": "Updated draft"})

    assert response.status_code == expected_status
    expected_content = payload["content"] if is_published else "Updated draft"
    with postgres_engine.connect() as connection:
        row = connection.execute(
            text("SELECT content, is_published FROM documents WHERE id = :id"),
            {"id": document_id},
        ).one()

    assert row == (expected_content, is_published)


def test_list_documents_filters_by_published_status_in_postgresql(
    postgres_client: TestClient,
) -> None:
    draft = postgres_client.post("/documents", json=document_payload())
    to_publish = postgres_client.post("/documents", json=document_payload())
    assert draft.status_code == 201
    assert to_publish.status_code == 201
    published = postgres_client.post(f"{to_publish.headers['location']}/publish")
    assert published.status_code == 200

    drafts = postgres_client.get("/documents", params={"published": "false"})
    published_documents = postgres_client.get(
        "/documents", params={"published": "true"}
    )

    assert drafts.status_code == 200
    assert drafts.json() == [draft.json()]
    assert published_documents.status_code == 200
    assert published_documents.json() == [published.json()]
