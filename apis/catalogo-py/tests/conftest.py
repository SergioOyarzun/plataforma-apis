import os

# Antes de importar la app: usar SQLite en vez de PostgreSQL
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)  # cada prueba parte con la base vacía
    with TestClient(app) as c:
        yield c