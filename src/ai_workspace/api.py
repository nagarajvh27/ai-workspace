import logging

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict

from ai_workspace.exceptions import DomainValidationError
from ai_workspace.models.document import Document
from ai_workspace.repositories import InMemoryDocumentRepository
from ai_workspace.services import DocumentService

logger = logging.getLogger(__name__)


class DocumentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    content: str
    author_name: str


class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    author_name: str
    is_published: bool


document_repository = InMemoryDocumentRepository()
document_service = DocumentService(document_repository)


def _to_document_response(
    document_id: int, document: Document
) -> DocumentResponse:
    return DocumentResponse(
        id=document_id,
        title=document.title,
        content=document.content,
        author_name=document.author.name,
        is_published=document.is_published,
    )


app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/documents", response_model=list[DocumentResponse])
def list_documents() -> list[DocumentResponse]:
    return [
        _to_document_response(document_id, document)
        for document_id, document in document_service.list_documents()
    ]


@app.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    request: DocumentCreate, response: Response
) -> DocumentResponse:
    try:
        document_id, document = document_service.create_document(
            title=request.title,
            content=request.content,
            author_name=request.author_name,
        )
    except DomainValidationError as error:
        logger.info(
            "document_creation_rejected",
            extra={
                "event": "document_creation_rejected",
                "operation": "create_document",
                "failure_category": "domain_validation",
                "http_status": status.HTTP_422_UNPROCESSABLE_CONTENT,
                "exception_type": type(error).__name__,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    response.headers["Location"] = f"/documents/{document_id}"

    return _to_document_response(document_id, document)


@app.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
)
def get_document(document_id: int) -> DocumentResponse:
    document = document_service.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return _to_document_response(document_id, document)
