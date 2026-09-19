from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

class DocumentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    content: str
    author_name: str

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/documents")
def list_documents():
    return []