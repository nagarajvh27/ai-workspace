"""Process-local cache lab that is not wired into production."""

from ai_workspace.models.document import Document
from ai_workspace.repositories import DocumentRepository


class CachingDocumentRepository:
    def __init__(
        self,
        repository: DocumentRepository,
    ) -> None:
        self._repository = repository
        self._cached_documents: list[tuple[int, Document]] | None = None

    def add(self, document: Document) -> int:
        document_id = self._repository.add(document)
        self._cached_documents = None
        return document_id

    def get(self, document_id: int) -> Document | None:
        return self._repository.get(document_id)

    def list_all(self) -> list[tuple[int, Document]]:
        if self._cached_documents is None:
            self._cached_documents = self._repository.list_all()

        return list(self._cached_documents)
