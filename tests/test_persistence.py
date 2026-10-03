from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from ai_workspace.models.document import Author, Document
from ai_workspace.persistence import (
    DocumentRecord,
    PostgresDocumentRepository,
    _document_from_record,
    _record_from_document,
)


def make_document() -> Document:
    return Document(
        title="Design notes",
        content="First draft",
        author=Author("Ada Lovelace"),
    )


def make_record(
    document_id: int = 1,
    *,
    is_published: bool = False,
) -> DocumentRecord:
    return DocumentRecord(
        id=document_id,
        title="Design notes",
        content="First draft",
        author_name="Ada Lovelace",
        is_published=is_published,
    )


def test_document_record_metadata_matches_proposed_table() -> None:
    table = DocumentRecord.__table__

    assert table.name == "documents"
    assert list(table.c.keys()) == [
        "id",
        "title",
        "content",
        "author_name",
        "is_published",
    ]
    assert table.c.id.primary_key is True
    assert table.c.id.identity is not None
    assert table.c.id.identity.always is True
    assert table.c.title.nullable is False
    assert table.c.content.nullable is False
    assert table.c.author_name.nullable is False
    assert table.c.is_published.nullable is False

    constraint_names = {
        constraint.name
        for constraint in table.constraints
    }
    assert "documents_title_not_blank" in constraint_names
    assert (
        "documents_author_name_not_blank"
        in constraint_names
    )


def test_record_from_document_maps_domain_fields() -> None:
    document = make_document()
    document.publish()

    record = _record_from_document(document)

    assert record.title == "Design notes"
    assert record.content == "First draft"
    assert record.author_name == "Ada Lovelace"
    assert record.is_published is True


def test_document_from_record_reconstructs_draft() -> None:
    document = _document_from_record(make_record())

    assert document.title == "Design notes"
    assert document.content == "First draft"
    assert document.author == Author("Ada Lovelace")
    assert document.is_published is False


def test_document_from_record_reconstructs_published_state() -> None:
    document = _document_from_record(
        make_record(is_published=True)
    )

    assert document.is_published is True


def test_add_returns_database_generated_id_after_commit() -> None:
    session = MagicMock(spec=Session)

    def assign_generated_id() -> None:
        record = session.add.call_args.args[0]
        record.id = 41

    session.flush.side_effect = assign_generated_id
    repository = PostgresDocumentRepository(lambda: session)

    document_id = repository.add(make_document())

    assert document_id == 41
    session.add.assert_called_once()
    session.flush.assert_called_once_with()
    session.commit.assert_called_once_with()
    session.rollback.assert_not_called()
    session.close.assert_called_once_with()


def test_add_rolls_back_and_closes_after_flush_failure() -> None:
    session = MagicMock(spec=Session)
    session.flush.side_effect = RuntimeError("write failed")
    repository = PostgresDocumentRepository(lambda: session)

    with pytest.raises(RuntimeError, match="write failed"):
        repository.add(make_document())

    session.commit.assert_not_called()
    session.rollback.assert_called_once_with()
    session.close.assert_called_once_with()


def test_add_rolls_back_and_closes_after_commit_failure() -> None:
    session = MagicMock(spec=Session)

    def assign_generated_id() -> None:
        record = session.add.call_args.args[0]
        record.id = 41

    session.flush.side_effect = assign_generated_id
    session.commit.side_effect = RuntimeError("commit failed")
    repository = PostgresDocumentRepository(lambda: session)

    with pytest.raises(RuntimeError, match="commit failed"):
        repository.add(make_document())

    session.rollback.assert_called_once_with()
    session.close.assert_called_once_with()


def test_get_returns_none_for_missing_record() -> None:
    session = MagicMock(spec=Session)
    session.get.return_value = None
    repository = PostgresDocumentRepository(lambda: session)

    result = repository.get(999)

    assert result is None
    session.get.assert_called_once_with(DocumentRecord, 999)
    session.commit.assert_not_called()
    session.rollback.assert_not_called()
    session.close.assert_called_once_with()


def test_get_reconstructs_domain_document() -> None:
    session = MagicMock(spec=Session)
    session.get.return_value = make_record(
        document_id=7,
        is_published=True,
    )
    repository = PostgresDocumentRepository(lambda: session)

    document = repository.get(7)

    assert document is not None
    assert document.title == "Design notes"
    assert document.author == Author("Ada Lovelace")
    assert document.is_published is True
    session.close.assert_called_once_with()


def test_list_all_returns_ordered_domain_documents() -> None:
    session = MagicMock(spec=Session)
    session.scalars.return_value.all.return_value = [
        make_record(document_id=1),
        make_record(document_id=2, is_published=True),
    ]
    repository = PostgresDocumentRepository(lambda: session)

    results = repository.list_all()

    assert [document_id for document_id, _ in results] == [
        1,
        2,
    ]
    assert results[0][1].is_published is False
    assert results[1][1].is_published is True

    statement = session.scalars.call_args.args[0]
    assert "ORDER BY documents.id" in str(statement)
    session.commit.assert_not_called()
    session.rollback.assert_not_called()
    session.close.assert_called_once_with()
