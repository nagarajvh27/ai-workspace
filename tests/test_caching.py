from fastapi.testclient import TestClient

from ai_workspace.api import create_app
from ai_workspace.caching import CachingDocumentRepository
from ai_workspace.models.document import Document
from ai_workspace.repositories import InMemoryDocumentRepository
from ai_workspace.services import DocumentService


class CountingDocumentRepository:
    def __init__(self) -> None:
        self._repository = InMemoryDocumentRepository()
        self.list_all_call_count = 0

    def add(self, document: Document) -> int:
        return self._repository.add(document)

    def get(self, document_id: int) -> Document | None:
        return self._repository.get(document_id)

    def list_all(self) -> list[tuple[int, Document]]:
        self.list_all_call_count += 1
        return self._repository.list_all()


def make_client() -> tuple[TestClient, CountingDocumentRepository]:
    repository = CountingDocumentRepository()
    cached_repository = CachingDocumentRepository(repository)
    service = DocumentService(cached_repository)

    return TestClient(create_app(service)), repository


def document_payload() -> dict[str, str]:
    return {
        "title": "Caching notes",
        "content": "Temporary collection copy.",
        "author_name": "Ada Lovelace",
    }


def test_list_documents_cache_miss_reads_repository() -> None:
    client, repository = make_client()

    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == []
    assert repository.list_all_call_count == 1


def test_list_documents_cache_hit_avoids_repository_read() -> None:
    client, repository = make_client()

    first_response = client.get("/documents")
    second_response = client.get("/documents")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json() == []
    assert second_response.json() == []
    assert repository.list_all_call_count == 1


def test_create_document_invalidates_cached_collection() -> None:
    client, repository = make_client()
    initial_response = client.get("/documents")

    created_response = client.post(
        "/documents",
        json=document_payload(),
    )
    refreshed_response = client.get("/documents")

    assert initial_response.status_code == 200
    assert initial_response.json() == []
    assert created_response.status_code == 201
    assert refreshed_response.status_code == 200
    assert refreshed_response.json() == [created_response.json()]
    assert repository.list_all_call_count == 2
