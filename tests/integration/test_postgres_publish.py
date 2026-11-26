import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import Engine


pytestmark = pytest.mark.integration


def test_publish_commits_and_rejects_repeat_in_postgresql(
    postgres_client: TestClient,
    postgres_engine: Engine,
) -> None:
    created = postgres_client.post(
        "/documents",
        json={
            "title": "Integration test",
            "content": "First draft",
            "author_name": "Ada Lovelace",
        },
    )
    assert created.status_code == 201
    draft = created.json()
    assert draft["is_published"] is False
    document_url = created.headers["location"]
    publish_url = f"{document_url}/publish"

    published = postgres_client.post(publish_url)
    assert published.status_code == 200
    assert published.json() == {**draft, "is_published": True}
    assert postgres_client.post(publish_url).status_code == 409
    assert postgres_client.patch(
        document_url, json={"content": "Unexpected edit"}
    ).status_code == 409

    with postgres_engine.connect() as connection:
        stored = connection.execute(
            text("SELECT is_published, content FROM documents WHERE id = :id"),
            {"id": draft["id"]},
        ).one()

    assert stored == (True, draft["content"])
