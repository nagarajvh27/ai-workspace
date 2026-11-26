# AI Workspace v0

A Python backend foundation for safe document workflows.

## Current scope

AI Workspace v0 provides a small FastAPI API for creating, reading, editing, and publishing
documents:

- `GET /health` reports service health.
- `GET /documents` returns the current document collection.
- `POST /documents` creates a document with a server-assigned ID.
- `GET /documents/{document_id}` returns one document or `404 Not Found`.
- `PATCH /documents/{document_id}` replaces a draft's content.
- `POST /documents/{document_id}/publish` publishes a draft.

The API keeps request schemas, domain models, application orchestration, PostgreSQL-backed production storage, and public response schemas separate. FastAPI routes call `DocumentService`, which constructs `Author` and `Document` domain models and delegates server-owned identity and storage through a narrow repository contract. Production composition uses `PostgresDocumentRepository`; deterministic unit and API tests explicitly use `InMemoryDocumentRepository`.

The API translates expected validation failures and state conflicts at the HTTP
boundary. The create route logs domain validation failures with privacy-safe
structured context. Unexpected failures remain server errors.

## Architecture

```mermaid
flowchart TD
    Client["Client or Swagger UI"] -->|HTTP request| API

    subgraph App["AI Workspace v0"]
        API["FastAPI + Pydantic<br/>Routes and request validation"]
        Service["DocumentService<br/>Coordinates document operations"]
        Repo["PostgresDocumentRepository<br/>SQLAlchemy sessions and transactions"]
        Domain["Author and Document<br/>Domain rules and publication state"]

        API --> Service
        Service -->|DocumentRepository interface| Repo
        Service -. creates .-> Domain
        Repo -. applies document rules .-> Domain
    end

    Repo -->|SQL| DB[("PostgreSQL<br/>documents table")]
```

## Requirements

Choose one local setup:

- Host-based setup: Python 3.12 or later and a reachable PostgreSQL database.
- Container-based setup: Docker with the Compose plugin.

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

## Run with Docker Compose

The Compose setup runs FastAPI and PostgreSQL 18 as separate services. It uses
the existing `pyproject.toml` dependency metadata and
`sql/documents_schema.sql` bootstrap DDL.

Set a local-only PostgreSQL password in the current shell. Use the original
password if the Compose database already has a volume:

```bash
export POSTGRES_PASSWORD="choose-a-local-development-password"
```

Compose passes the original password to the app as a separate setting.
SQLAlchemy builds the connection URL, so characters such as `@` do not require
manual percent-encoding here.

Then build and start the services:

```bash
docker compose up --build
```

The API is available at `http://127.0.0.1:8000`. PostgreSQL is intentionally
not published to the host; the FastAPI container reaches it through the
Compose service name `db`.

Stop and remove the containers with:

```bash
docker compose down
```

The named `postgres_data` volume remains after the containers are removed, so
development data survives container replacement. Explicitly deleting that
volume deletes the stored PostgreSQL data.

`sql/documents_schema.sql` runs automatically only when PostgreSQL initializes
an empty data directory. Changing that file does not update an existing
database volume, and the file is not a migration system.

The Compose database is the development database `ai_workspace`. Integration
tests remain separate and still require `TEST_DATABASE_URL` to name exactly
`ai_workspace_test`. Never point the destructive integration-test setup at the
Compose development database.

Do not commit real credentials or local environment files.

## Run tests

The ordinary unit and API tests do not require PostgreSQL:

```bash
./.venv/bin/python -m pytest
```

PostgreSQL integration tests require a dedicated database named exactly
`ai_workspace_test`. For a local Postgres.app installation using its Unix
socket:

```bash
createdb ai_workspace_test
export TEST_DATABASE_URL="postgresql+psycopg:///ai_workspace_test?host=/tmp"
./.venv/bin/python -m pytest -m integration
```

For another PostgreSQL installation, use the same database name and provide
the appropriate local connection details through `TEST_DATABASE_URL`. Never
commit credentials.

The integration-test safety guard refuses non-PostgreSQL URLs and any database
whose name is not exactly `ai_workspace_test`. After that guard succeeds, the
test fixtures recreate the `documents` table from `sql/documents_schema.sql`
and run `TRUNCATE TABLE documents RESTART IDENTITY` before and after each test.
Never point `TEST_DATABASE_URL` at a database containing non-test data.

With `TEST_DATABASE_URL` configured, the complete suite includes the real
PostgreSQL tests:

```bash
./.venv/bin/python -m pytest
```

Before draft editing and publishing, ordinary-suite verification recorded 68
passing tests. The 3 PostgreSQL integration
tests were skipped because `TEST_DATABASE_URL` was not configured, and 2 known
upstream test-client deprecation warnings remained. A separate configured
PostgreSQL integration run proved API create, retrieve, and list behavior,
direct committed row storage, and rollback of a flushed insert after an
injected pre-commit failure. Earlier manual PostgreSQL 18.6 verification also
confirmed persistence across an application restart.

## Continuous integration

[GitHub Actions](.github/workflows/ci.yml) runs on pushes to `main` and on
pull requests targeting `main`. It runs three independent jobs:

- Ordinary tests and dependency checks on Python 3.12.
- Integration tests against a temporary PostgreSQL 18 service using
  `ai_workspace_test`.
- A Docker image build.

The Docker job verifies that the image builds. The local Docker Compose
procedure above exercises the running app and database. Deployment remains
outside the workflow.

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

`GET /documents` returns all documents by default. Use
`GET /documents?published=false` for drafts only or
`GET /documents?published=true` for published documents only.

A document that does not exist returns `404 Not Found`.

Invalid request shapes return `422 Unprocessable Content`. The create endpoint
also returns `422` for domain validation failures.

### Edit a draft's content

Send `PATCH /documents/{document_id}` with a JSON body such as
`{"content": "Updated draft"}`. The response is `200 OK` with the updated
document. A missing ID returns `404 Not Found`. A published document returns
`409 Conflict` and its content stays unchanged.

### Publish a draft

Send `POST /documents/{document_id}/publish`. The response is `200 OK` with
the document and `is_published: true`. A missing document returns
`404 Not Found`. A repeat publish returns `409 Conflict` and leaves the
document unchanged.

## Current limitations

The database uses explicit bootstrap SQL. Versioned schema migrations remain
future work. Document endpoints currently accept anonymous requests, and the
document access policy is still open. The application has been verified
locally with Docker Compose. Production deployment remains future work.

Most unit and API tests intentionally compose `InMemoryDocumentRepository`.
The marked integration tests separately compose `PostgresDocumentRepository`
and require the explicitly configured real PostgreSQL test database.

## Development status

This is a learning-focused backend foundation. It demonstrates explicit domain validation, HTTP request validation, server-owned identity, document retrieval, public response serialization, and deterministic API tests without making production-readiness claims.
