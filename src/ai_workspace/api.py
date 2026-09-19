from fastapi import FastAPI


app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/documents")
def list_documents():
    return []