from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict

from ai_workspace.models.document import Author, Document


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


documents_by_id: dict[int, Document] = {}
next_document_id = 1


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
        for document_id, document in documents_by_id.items()
    ]


@app.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    request: DocumentCreate, response: Response
) -> DocumentResponse:
    global next_document_id

    try:
        author = Author(name=request.author_name)
        document = Document(
            title=request.title,
            content=request.content,
            author=author,
        )
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    document_id = next_document_id
    documents_by_id[document_id] = document
    next_document_id += 1

    response.headers["Location"] = f"/documents/{document_id}"

    return _to_document_response(document_id, document)


@app.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
)
def get_document(document_id: int) -> DocumentResponse:
    document = documents_by_id.get(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return _to_document_response(document_id, document)