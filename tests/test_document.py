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
