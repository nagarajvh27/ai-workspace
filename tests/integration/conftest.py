import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.orm import sessionmaker

from ai_workspace.api import create_app
from ai_workspace.persistence import PostgresDocumentRepository
from ai_workspace.services import DocumentService


TEST_DATABASE_ENV = "TEST_DATABASE_URL"
EXPECTED_TEST_DATABASE = "ai_workspace_test"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = PROJECT_ROOT / "sql" / "documents_schema.sql"


def _load_test_database_url() -> URL:
    database_url = os.environ.get(TEST_DATABASE_ENV)

    if database_url is None:
        pytest.skip(f"{TEST_DATABASE_ENV} is not configured")

    parsed_url = make_url(database_url)

    if parsed_url.get_backend_name() != "postgresql":
        pytest.fail(
            f"{TEST_DATABASE_ENV} must use PostgreSQL",
            pytrace=False,
        )

    if parsed_url.database != EXPECTED_TEST_DATABASE:
        pytest.fail(
            "Refusing database cleanup because the database name "
            f"is not {EXPECTED_TEST_DATABASE!r}",
            pytrace=False,
        )

    return parsed_url


@pytest.fixture(scope="session")
def postgres_test_database_url() -> URL:
    return _load_test_database_url()


@pytest.fixture(scope="session")
def postgres_engine(
    postgres_test_database_url: URL,
) -> Iterator[Engine]:
    engine = create_engine(postgres_test_database_url)
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    try:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "DROP TABLE IF EXISTS documents"
            )
            connection.exec_driver_sql(schema_sql)

        yield engine
    finally:
        engine.dispose()


def _truncate_documents(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "TRUNCATE TABLE documents RESTART IDENTITY"
        )


@pytest.fixture(autouse=True)
def clean_documents_table(
    postgres_engine: Engine,
) -> Iterator[None]:
    _truncate_documents(postgres_engine)

    try:
        yield
    finally:
        _truncate_documents(postgres_engine)


@pytest.fixture
def postgres_client(
    postgres_engine: Engine,
) -> Iterator[TestClient]:
    session_factory = sessionmaker(bind=postgres_engine)
    repository = PostgresDocumentRepository(session_factory)
    service = DocumentService(repository)

    with TestClient(create_app(service)) as client:
        yield client
