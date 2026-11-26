from sqlalchemy.engine import URL

from ai_workspace.database_config import database_url_from_env


def test_database_url_from_env_preserves_explicit_database_url() -> None:
    explicit_url = "postgresql+psycopg:///ai_workspace?host=/tmp"

    assert database_url_from_env({"DATABASE_URL": explicit_url}) == explicit_url


def test_database_url_from_env_keeps_reserved_characters_in_password() -> None:
    password = "example@host:/?#%$"

    url = database_url_from_env(
        {
            "POSTGRES_USER": "ai_workspace",
            "POSTGRES_PASSWORD": password,
            "POSTGRES_HOST": "db",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "ai_workspace",
        }
    )

    assert isinstance(url, URL)
    assert url.username == "ai_workspace"
    assert url.password == password
    assert url.host == "db"
    assert url.port == 5432
    assert url.database == "ai_workspace"
