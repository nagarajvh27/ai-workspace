from ai_workspace.models.document import Author, Document
from ai_workspace.repositories import InMemoryDocumentRepository


def make_document(title: str) -> Document:
    return Document(
        title=title,
        content="Repository test content.",
        author=Author("Ada Lovelace"),
    )


def test_add_assigns_sequential_ids_and_stores_documents() -> None:
    repository = InMemoryDocumentRepository()
    first_document = make_document("First")
    second_document = make_document("Second")

    first_id = repository.add(first_document)
    second_id = repository.add(second_document)

    assert first_id == 1
    assert second_id == 2
    assert repository.get(first_id) is first_document
    assert repository.get(second_id) is second_document


def test_get_returns_none_for_missing_document() -> None:
    repository = InMemoryDocumentRepository()

    assert repository.get(1) is None


def test_list_all_returns_stored_documents_with_ids() -> None:
    repository = InMemoryDocumentRepository()
    first_document = make_document("First")
    second_document = make_document("Second")

    first_id = repository.add(first_document)
    second_id = repository.add(second_document)

    assert repository.list_all() == [
        (first_id, first_document),
        (second_id, second_document),
    ]


def test_list_all_does_not_expose_repository_collection() -> None:
    repository = InMemoryDocumentRepository()
    document = make_document("Structural isolation")
    document_id = repository.add(document)

    returned_documents = repository.list_all()
    returned_documents.clear()

    assert repository.list_all() == [(document_id, document)]


def test_clear_removes_documents_and_resets_next_id() -> None:
    repository = InMemoryDocumentRepository()
    repository.add(make_document("Before reset"))

    repository.clear()

    assert repository.list_all() == []

    new_document = make_document("After reset")
    assert repository.add(new_document) == 1
