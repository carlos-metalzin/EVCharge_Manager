import os
import sys
from pathlib import Path
import pytest

# Garante que o diretório raiz (EVCharge_Manager) esteja no sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.infrastructure.db import SQLiteDatabase
from app.infrastructure.repositories import UserRepository, CondoRepository
from app.services.user_service import UserService
from app.services.condo_service import CondoService


@pytest.fixture
def temp_db(tmp_path: Path) -> SQLiteDatabase:
    db_path = tmp_path / "evcharge_struct.db"
    return SQLiteDatabase(str(db_path))


@pytest.fixture
def repos_db(temp_db: SQLiteDatabase):
    return UserRepository(temp_db), CondoRepository(temp_db)


@pytest.fixture
def services_db(repos_db):
    users_repo, condos_repo = repos_db
    return (
        UserService(users_repo, condos_repo),
        CondoService(condos_repo, users_repo),
    )