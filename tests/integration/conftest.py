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
from app.domain.models import Condo


@pytest.fixture
def temp_db(tmp_path: Path) -> SQLiteDatabase:
    """SQLite real em arquivo temporário (integração)."""
    db_path = tmp_path / "evcharge_integ.db"
    return SQLiteDatabase(str(db_path))


@pytest.fixture
def repos_db(temp_db: SQLiteDatabase):
    """Repos reais (DAO/Repository) conectados ao SQLite real."""
    return UserRepository(temp_db), CondoRepository(temp_db)


@pytest.fixture
def services_db(repos_db):
    users_repo, condos_repo = repos_db
    return (
        UserService(users_repo, condos_repo),
        CondoService(condos_repo, users_repo),
    )


@pytest.fixture
def sample_condos(services_db):
    """Cria dois condomínios base para os fluxos."""
    user_svc, condo_svc = services_db
    c1_id = condo_svc.register_condo("Alpha", 50, 2, "Lento", "SP", 0.75)
    c2_id = condo_svc.register_condo("Beta", 80, 3, "Rápido", "RJ", 1.10)
    return {"Alpha": c1_id, "Beta": c2_id}
