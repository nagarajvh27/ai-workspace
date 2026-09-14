import pytest

from ai_workspace.models.document import Document


def test_document_word_count() -> None:
    document = Document(
        title="Test",
        content="AI Workspace is starting today",
    )

    assert document.word_count() == 5


def test_document_normalizes_title() -> None:
    document = Document(
        title="  Backend foundations  ",
        content="AI Workspace is starting today",
    )

    assert document.title == "Backend foundations"


def test_document_rejects_blank_title() -> None:
    with pytest.raises(ValueError, match="Title cannot be blank"):
        Document(
            title="   ",
            content="This document should not be created.",
        )


def test_document_non_string_title() -> None:
    with pytest.raises(TypeError, match="Title must be a string"):
        Document(
            title=1234,
            content="This document should not be created.",
        )


def test_document_rename_normalizes_title() -> None:
    document = Document(
        title="Initial title",
        content="Learning domain-model behavior.",
    )

    document.rename("  Updated title  ")

    assert document.title == "Updated title"


def test_document_rename_rejects_blank_title() -> None:
    document = Document(
        title="Original title",
        content="Learning domain-model behavior.",
    )

    with pytest.raises(ValueError, match="Title cannot be blank"):
        document.rename("   ")

    assert document.title == "Original title"


def test_document_publish_marks_document_as_published() -> None:
    document = Document(
        title="Release notes",
        content="Ready for publication.",
    )

    document.publish()

    assert document.published is True


def test_document_publish_rejects_already_published_document() -> None:
    document = Document(
        title="Release notes",
        content="Ready for publication.",
    )
    document.publish()

    with pytest.raises(ValueError, match="Document is already published"):
        document.publish()

    assert document.published is True


def test_document_update_content_changes_draft_document() -> None:
    document = Document(
        title="Initial title",
        content="Original content.",
    )

    document.update_content("Updated content.")

    assert document.content == "Updated content."


def test_document_rename_rejects_published_document() -> None:
    document = Document(
        title="Original title",
        content="Original content.",
    )
    document.publish()

    with pytest.raises(ValueError, match="Cannot modify a published document"):
        document.rename("Changed title")

    assert document.title == "Original title"


def test_document_update_content_rejects_published_document() -> None:
    document = Document(
        title="Original title",
        content="Original content.",
    )
    document.publish()

    with pytest.raises(ValueError, match="Cannot modify a published document"):
        document.update_content("Changed content.")

    assert document.content == "Original content."

def test_excerpt_returns_requested_prefix() -> None:
    document = Document(title="Note", content="Hello world")

    assert document.excerpt(5) == "Hello"


def test_excerpt_returns_all_content_when_shorter_than_limit() -> None:
    document = Document(title="Note", content="Hi")

    assert document.excerpt(5) == "Hi"


def test_excerpt_rejects_negative_limit() -> None:
    document = Document(title="Note", content="Hello")

    with pytest.raises(ValueError):
        document.excerpt(-1)


def test_excerpt_does_not_change_document_state() -> None:
    document = Document(title=" Note ", content="Hello world")
    document.publish()

    assert document.excerpt(5) == "Hello"
    assert document.title == "Note"
    assert document.content == "Hello world"
    assert document.published is True

def test_excerpt_rejects_non_int() -> None:
    document = Document(title="Note", content="Hello")

    with pytest.raises(TypeError):
        document.excerpt("5")
