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
