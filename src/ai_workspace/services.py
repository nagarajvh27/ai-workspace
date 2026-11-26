from ai_workspace.models.document import Author, Document
from ai_workspace.repositories import DocumentRepository


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
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

    def edit_document_content(
        self, document_id: int, content: str
    ) -> Document | None:
        return self._repository.update_content(document_id, content)

    def publish_document(self, document_id: int) -> Document | None:
        return self._repository.publish(document_id)

    def list_documents(
        self, *, published: bool | None = None
    ) -> list[tuple[int, Document]]:
        return self._repository.list_all(published=published)
