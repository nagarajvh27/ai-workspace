from typing import Protocol

from ai_workspace.models.document import Document


class DocumentRepository(Protocol):
    def add(self, document: Document) -> int:
        ...

    def get(self, document_id: int) -> Document | None:
        ...

    def list_all(self) -> list[tuple[int, Document]]:
        ...


class InMemoryDocumentRepository:
    def __init__(self) -> None:
        self._documents_by_id: dict[int, Document] = {}
        self._next_document_id = 1

    def add(self, document: Document) -> int:
        document_id = self._next_document_id
        self._documents_by_id[document_id] = document
        self._next_document_id += 1
        return document_id

    def get(self, document_id: int) -> Document | None:
        return self._documents_by_id.get(document_id)

    def list_all(self) -> list[tuple[int, Document]]:
        return list(self._documents_by_id.items())

    def clear(self) -> None:
        self._documents_by_id.clear()
        self._next_document_id = 1
