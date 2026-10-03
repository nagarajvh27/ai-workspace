import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ai_workspace.api import create_app
from ai_workspace.persistence import PostgresDocumentRepository
from ai_workspace.services import DocumentService

database_url = os.environ["DATABASE_URL"]

engine = create_engine(database_url)
session_factory = sessionmaker(bind=engine)

document_repository = PostgresDocumentRepository(
    session_factory
)
document_service = DocumentService(document_repository)

app = create_app(document_service)
