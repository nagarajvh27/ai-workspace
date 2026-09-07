from ai_workspace.models.document import Document


def test_document_word_count() -> None:
    document = Document(
        title="Test",
        content="AI Workspace is starting today",
    )

    assert document.word_count() == 5