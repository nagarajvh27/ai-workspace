# AI Workspace v0

A Python backend foundation for safe document workflows.

## Current scope

AI Workspace v0 currently provides a small FastAPI API for creating and reading documents:

- `GET /health` reports service health.
- `GET /documents` returns the current document collection.
- `POST /documents` creates a document with a server-assigned ID.
- `GET /documents/{document_id}` returns one document or `404 Not Found`.

The API keeps request schemas, domain models, application orchestration, PostgreSQL-backed production storage, and public response schemas separate. FastAPI routes call `DocumentService`, which constructs `Author` and `Document` domain models and delegates server-owned identity and storage through a narrow repository contract. Production composition uses `PostgresDocumentRepository`; deterministic unit and API tests explicitly use `InMemoryDocumentRepository`.

Handled domain validation failures are translated at the HTTP boundary and logged once with privacy-safe structured context. Unexpected built-in failures remain server errors rather than being presented as client validation failures.

## Requirements

- Python 3.12 or later
- A reachable PostgreSQL database

## Setup

From the repository root:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --editable ".[dev]"
```

## Database setup

Create an empty PostgreSQL database, then apply the explicit schema:

If you use Postgres.app on macOS, expose its command-line tools in the current shell:

```bash
export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"
```

```bash
psql --dbname=DATABASE --file=sql/documents_schema.sql
```

`sql/documents_schema.sql` is standalone bootstrap DDL, not an Alembic migration.

Provide the application's SQLAlchemy connection URL through the environment:

```bash
export DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE"
```

Replace every uppercase placeholder locally. Do not commit real credentials.

## Run locally

```bash
./.venv/bin/uvicorn ai_workspace.main:app --reload
```

The API is then available at `http://127.0.0.1:8000`.

## Run tests

```bash
./.venv/bin/python -m pytest
```

Latest local verification: 63 tests passed with 2 known upstream test-client deprecation warnings. Manual PostgreSQL 18.6 verification confirmed schema creation, database-generated identity, create/read/list behavior, direct row storage, and persistence across an application restart.

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

The production composition persists documents in PostgreSQL, but schema setup is currently an explicit manual step. The repository does not yet include Alembic migration configuration, automated PostgreSQL integration-test infrastructure, authentication, Docker, CI, or a production deployment.

The ordinary test suite intentionally composes `InMemoryDocumentRepository`; passing it does not prove PostgreSQL connectivity or behavior. PostgreSQL verification must be run separately against a real database.

## Development status

This is a learning-focused backend foundation. It demonstrates explicit domain validation, HTTP request validation, server-owned identity, document retrieval, public response serialization, and deterministic API tests without making production-readiness claims.
