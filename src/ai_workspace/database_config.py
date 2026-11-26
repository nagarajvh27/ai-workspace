from collections.abc import Mapping

from sqlalchemy.engine import URL


def database_url_from_env(environment: Mapping[str, str]) -> str | URL:
    """Load a complete URL or build one from separate PostgreSQL settings."""
    if "DATABASE_URL" in environment:
        return environment["DATABASE_URL"]

    return URL.create(
        "postgresql+psycopg",
        username=environment["POSTGRES_USER"],
        password=environment["POSTGRES_PASSWORD"],
        host=environment["POSTGRES_HOST"],
        port=int(environment.get("POSTGRES_PORT", "5432")),
        database=environment["POSTGRES_DB"],
    )
