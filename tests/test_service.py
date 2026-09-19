from ai_workspace.repositories import InMemoryDocumentRepository
from ai_workspace.services import DocumentService


def make_service() -> tuple[
    DocumentService,
    InMemoryDocumentRepository,
]:
    repository = InMemoryDocumentRepository()
    return DocumentService(repository), repository


def test_create_document_constructs_and_stores_domain_document() -> None:
    service, repository = make_service()

    document_id, document = service.create_document(
        title="Design notes",
        content="First draft",
        author_name="Ada Lovelace",
    )

    assert document_id == 1
    assert document.title == "Design notes"
    assert document.content == "First draft"
    assert document.author.name == "Ada Lovelace"
    assert document.is_published is False
    assert repository.get(document_id) is document


def test_get_document_returns_stored_document_or_none() -> None:
    service, _ = make_service()
    document_id, document = service.create_document(
        title="Design notes",
        content="First draft",
        author_name="Ada Lovelace",
    )

    assert service.get_document(document_id) is document
    assert service.get_document(999) is None


def test_list_documents_returns_stored_documents_with_ids() -> None:
    service, _ = make_service()
    first_id, first_document = service.create_document(
        title="First",
        content="First draft",
        author_name="Ada Lovelace",
    )
    second_id, second_document = service.create_document(
        title="Second",
        content="Second draft",
        author_name="Grace Hopper",
    )

    assert service.list_documents() == [
        (first_id, first_document),
        (second_id, second_document),
    ]
