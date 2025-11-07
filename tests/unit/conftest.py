import os, sys
from pathlib import Path
import pytest

from app.infrastructure.db import SQLiteDatabase
from app.infrastructure.repositories import UserRepository, CondoRepository
from app.infrastructure.mockdb import MockUserRepository, MockCondoRepository
from app.services.user_service import UserService
from app.services.condo_service import CondoService
from app.domain.models import Condo


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture
def temp_db(tmp_path: Path):
    db_path = tmp_path / "test_evcharge.db"
    return SQLiteDatabase(str(db_path))


@pytest.fixture
def sqlite_repos(temp_db):
    return UserRepository(temp_db), CondoRepository(temp_db)


@pytest.fixture
def services_mock():
    users = MockUserRepository()
    condos = MockCondoRepository()
    return UserService(users, condos), CondoService(condos, users)


@pytest.fixture
def seed_condos_sqlite(sqlite_repos):
    users_repo, condos_repo = sqlite_repos
    # cria dois condomínios básicos
    condos_repo.create(Condo(id=None, name="Alpha", apartments_count=50, chargers_count=2, charger_type="Lento", state="SP", energy_price=0.75))
    condos_repo.create(Condo(id=None, name="Beta", apartments_count=80, chargers_count=3, charger_type="Rápido", state="RJ", energy_price=1.1))
    return ("Alpha", "Beta")


@pytest.fixture
def users_and_condos_services_mock(services_mock):
    user_service, condo_service = services_mock
    condo_service.register_condo("Alpha", 50, 2, "Lento", "SP", 0.75)
    condo_service.register_condo("Beta", 80, 3, "Rápido", "RJ", 1.10)
    return user_service, condo_service

