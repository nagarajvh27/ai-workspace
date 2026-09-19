from ai_workspace.models.document import Author, Document
from ai_workspace.repositories import InMemoryDocumentRepository


class DocumentService:
    def __init__(
        self,
        repository: InMemoryDocumentRepository,
    ) -> None:
        self._repository = repository

    def create_document(
        self,
        title: str,
        content: str,
        author_name: str,
    ) -> tuple[int, Document]:
        author = Author(name=author_name)
        document = Document(
            title=title,
            content=content,
            author=author,
        )
        document_id = self._repository.add(document)

        return document_id, document

    def get_document(self, document_id: int) -> Document | None:
        return self._repository.get(document_id)

    def list_documents(self) -> list[tuple[int, Document]]:
        return self._repository.list_all()
