import pytest

from ai_workspace.exceptions import DomainValidationError
from ai_workspace.models.document import Author, Document


def test_document_word_count() -> None:
    document = Document(
        title="Test",
        content="AI Workspace is starting today",
        author=Author("Ada Lovelace"),
    )

    assert document.word_count() == 5


def test_document_normalizes_title() -> None:
    document = Document(
        title="  Backend foundations  ",
        content="AI Workspace is starting today",
        author=Author("Ada Lovelace"),
    )

    assert document.title == "Backend foundations"


def test_document_rejects_blank_title() -> None:
    with pytest.raises(
        DomainValidationError,
        match="Title cannot be blank",
    ):
        Document(
            title="   ",
            content="This document should not be created.",
            author=Author("Ada Lovelace"),
        )


def test_document_non_string_title() -> None:
    with pytest.raises(TypeError, match="Title must be a string"):
        Document(
            title=1234,
            content="This document should not be created.",
            author=Author("Ada Lovelace"),
        )


def test_document_rename_normalizes_title() -> None:
    document = Document(
        title="Initial title",
        content="Learning domain-model behavior.",
        author=Author("Ada Lovelace"),
    )

    document.rename("  Updated title  ")

    assert document.title == "Updated title"


def test_document_rename_rejects_blank_title() -> None:
    document = Document(
        title="Original title",
        content="Learning domain-model behavior.",
        author=Author("Ada Lovelace"),
    )

    with pytest.raises(
        DomainValidationError,
        match="Title cannot be blank",
    ):
        document.rename("   ")

    assert document.title == "Original title"


def test_document_publish_marks_document_as_published() -> None:
    document = Document(
        title="Release notes",
        content="Ready for publication.",
        author=Author("Ada Lovelace"),
    )

    document.publish()

    assert document.is_published is True


def test_document_publish_rejects_already_published_document() -> None:
    document = Document(
        title="Release notes",
        content="Ready for publication.",
        author=Author("Ada Lovelace"),
    )
    document.publish()

    with pytest.raises(
        DomainValidationError,
        match="Document is already published",
    ):
        document.publish()

    assert document.is_published is True


def test_document_update_content_changes_draft_document() -> None:
    document = Document(
        title="Initial title",
        content="Original content.",
        author=Author("Ada Lovelace"),
    )

    document.update_content("Updated content.")

    assert document.content == "Updated content."


def test_document_rename_rejects_published_document() -> None:
    document = Document(
        title="Original title",
        content="Original content.",
        author=Author("Ada Lovelace"),
    )
    document.publish()

    with pytest.raises(
        DomainValidationError,
        match="Cannot modify a published document",
    ):
        document.rename("Changed title")

    assert document.title == "Original title"


def test_document_update_content_rejects_published_document() -> None:
    document = Document(
        title="Original title",
        content="Original content.",
        author=Author("Ada Lovelace"),
    )
    document.publish()

    with pytest.raises(
        DomainValidationError,
        match="Cannot modify a published document",
    ):
        document.update_content("Changed content.")

    assert document.content == "Original content."

def test_excerpt_returns_requested_prefix() -> None:
    document = Document(title="Note", content="Hello world", author=Author("Ada Lovelace"),)

    assert document.excerpt(5) == "Hello"


def test_excerpt_returns_all_content_when_shorter_than_limit() -> None:
    document = Document(title="Note", content="Hi", author=Author("Ada Lovelace"),)

    assert document.excerpt(5) == "Hi"


def test_excerpt_rejects_negative_limit() -> None:
    document = Document(title="Note", content="Hello", author=Author("Ada Lovelace"),)

    with pytest.raises(
        DomainValidationError,
        match="max_chars cannot be negative",
    ):
        document.excerpt(-1)


def test_excerpt_does_not_change_document_state() -> None:
    document = Document(title=" Note ", content="Hello world", author=Author("Ada Lovelace"),)
    document.publish()

    assert document.excerpt(5) == "Hello"
    assert document.title == "Note"
    assert document.content == "Hello world"
    assert document.is_published is True

def test_excerpt_rejects_non_int() -> None:
    document = Document(title="Note", content="Hello", author=Author("Ada Lovelace"),)

    with pytest.raises(TypeError):
        document.excerpt("5")

def test_new_document_is_not_published():
    document = Document(title="Draft", content="Body", author=Author("Ada Lovelace"))

    assert document.is_published is False

def test_document_cannot_be_created_as_published():
    with pytest.raises(TypeError):
        Document(title="Draft", content="Body", author=Author("Ada Lovelace"), published=True)

def test_published_status_is_read_only():
    document = Document(title="Draft", content="Body", author=Author("Ada Lovelace"))

    with pytest.raises(AttributeError):
        document.is_published = True

    assert document.is_published is False


def test_document_exposes_the_supplied_author() -> None:
    author = Author("Ada Lovelace")

    document = Document(
        title="Analytical Engine notes",
        content="A draft document.",
        author=author,
    )

    assert document.author is author


@pytest.mark.parametrize("invalid_author", ["Ada Lovelace", None])
def test_document_rejects_non_author_values(invalid_author) -> None:
    with pytest.raises(TypeError):
        Document(
            title="Analytical Engine notes",
            content="A draft document.",
            author=invalid_author,
        )



class TestAuthor:
    def test_exposes_a_valid_name(self) -> None:
        author = Author("Ada Lovelace")

        assert author.name == "Ada Lovelace"

    def test_normalizes_surrounding_whitespace(self) -> None:
        author = Author("  Ada Lovelace  ")

        assert author.name == "Ada Lovelace"

    @pytest.mark.parametrize("name", ["", "   ", "\n\t"])
    def test_rejects_blank_names(self, name: str) -> None:
        with pytest.raises(DomainValidationError, match="name"):
            Author(name)

    @pytest.mark.parametrize("name", [None, 42, []])
    def test_rejects_non_text_names(self, name: object) -> None:
        with pytest.raises(TypeError, match="name"):
            Author(name)  # type: ignore[arg-type]

    def test_cannot_be_mutated_after_creation(self) -> None:
        author = Author("Ada Lovelace")

        with pytest.raises(AttributeError):
            author.name = "Grace Hopper"  # type: ignore[misc]

        assert author.name == "Ada Lovelace"
