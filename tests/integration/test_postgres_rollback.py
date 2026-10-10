import pytest
from sqlalchemy import event, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ai_workspace.models.document import Author, Document
from ai_workspace.persistence import (
    DocumentRecord,
    PostgresDocumentRepository,
)


pytestmark = pytest.mark.integration


def test_add_rolls_back_flushed_insert_after_precommit_failure(
    postgres_engine: Engine,
) -> None:
    session_factory = sessionmaker(bind=postgres_engine)
    repository_session = session_factory()
    flushed_row_was_visible = False

    def fail_before_commit(session: Session) -> None:
        nonlocal flushed_row_was_visible

        row_count = session.scalar(
            select(func.count()).select_from(DocumentRecord)
        )
        flushed_row_was_visible = row_count == 1
        raise RuntimeError("injected failure before commit")

    event.listen(
        repository_session,
        "before_commit",
        fail_before_commit,
        once=True,
    )

    repository = PostgresDocumentRepository(
        lambda: repository_session
    )
    document = Document(
        title="Rolled back document",
        content="This row must not be committed.",
        author=Author("Ada Lovelace"),
    )

    with pytest.raises(
        RuntimeError,
        match="injected failure before commit",
    ):
        repository.add(document)

    assert flushed_row_was_visible is True

    with Session(postgres_engine) as verification_session:
        persisted_row_count = verification_session.scalar(
            select(func.count()).select_from(DocumentRecord)
        )

    assert persisted_row_count == 0
