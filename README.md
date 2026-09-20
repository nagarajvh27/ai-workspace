# AI Workspace v0

A Python backend foundation for safe document workflows.

## Current scope

AI Workspace v0 currently provides a small FastAPI API for creating and reading documents:

- `GET /health` reports service health.
- `GET /documents` returns the current document collection.
- `POST /documents` creates a document with a server-assigned ID.
- `GET /documents/{document_id}` returns one document or `404 Not Found`.

The API keeps request schemas, domain models, application orchestration, in-memory storage, and public response schemas separate. FastAPI routes call `DocumentService`, which constructs `Author` and `Document` domain models and delegates server-owned identity and storage to `InMemoryDocumentRepository`.

Handled domain validation failures are translated at the HTTP boundary and logged once with privacy-safe structured context. Unexpected built-in failures remain server errors rather than being presented as client validation failures.

## Requirements

- Python 3.12 or later

## Setup

From the repository root:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --editable ".[dev]"
```

## Run locally

```bash
./.venv/bin/uvicorn ai_workspace.api:app --reload
```

The API is then available at `http://127.0.0.1:8000`.

## Run tests

```bash
./.venv/bin/python -m pytest
```

Latest local verification: 53 tests passed with 2 known upstream test-client deprecation warnings.

## API overview

### Health check

```text
GET /health
```

Returns:

```json
{"status": "ok"}
```

### Create a document

```text
POST /documents
Content-Type: application/json
```

Request body:

```json
{
  "title": "Design notes",
  "content": "First draft",
  "author_name": "Ada Lovelace"
}
```

A successful request returns `201 Created`, a `Location` header such as `/documents/1`, and a response like:

```json
{
  "id": 1,
  "title": "Design notes",
  "content": "First draft",
  "author_name": "Ada Lovelace",
  "is_published": false
}
```

The server owns `id` and `is_published`; client-supplied values for those fields are rejected.

### Read documents

```text
GET /documents
GET /documents/{document_id}
```

A document that does not exist returns `404 Not Found`.

Invalid request shapes and domain validation failures return `422 Unprocessable Content`.

## Current limitations

Document data is stored only in process memory. It is lost when the application restarts and is not durable, concurrent-safe, multi-process-safe, or backed by a database.

This repository does not yet include PostgreSQL, SQLAlchemy, migrations, authentication, Docker, CI, or a production deployment.

## Development status

This is a learning-focused backend foundation. It demonstrates explicit domain validation, HTTP request validation, server-owned identity, document retrieval, public response serialization, and deterministic API tests without making production-readiness claims.
