from collections.abc import Callable

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Identity,
    Text,
    select,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
)

from ai_workspace.models.document import Author, Document


class Base(DeclarativeBase):
    pass


class DocumentRecord(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(
            "btrim(title) <> ''",
            name="documents_title_not_blank",
        ),
        CheckConstraint(
            "btrim(author_name) <> ''",
            name="documents_author_name_not_blank",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )


def _record_from_document(document: Document) -> DocumentRecord:
    return DocumentRecord(
        title=document.title,
        content=document.content,
        author_name=document.author.name,
        is_published=document.is_published,
    )


def _document_from_record(record: DocumentRecord) -> Document:
    document = Document(
        title=record.title,
        content=record.content,
        author=Author(record.author_name),
    )

    if record.is_published:
        document.publish()

    return document


SessionFactory = Callable[[], Session]


class PostgresDocumentRepository:
    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def add(self, document: Document) -> int:
        session = self._session_factory()

        try:
            record = _record_from_document(document)
            session.add(record)
            session.flush()

            document_id = record.id

            session.commit()
            return document_id
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get(self, document_id: int) -> Document | None:
        session = self._session_factory()

        try:
            record = session.get(DocumentRecord, document_id)

            if record is None:
                return None

            return _document_from_record(record)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list_all(self) -> list[tuple[int, Document]]:
        session = self._session_factory()

        try:
            statement = select(DocumentRecord).order_by(
                DocumentRecord.id
            )
            records = session.scalars(statement).all()

            return [
                (record.id, _document_from_record(record))
                for record in records
            ]
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
