import os
import sys
from pathlib import Path
import itertools
import pytest

# Garante que o diretório raiz (EVCharge_Manager) esteja no sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.infrastructure.db import SQLiteDatabase
from app.infrastructure.repositories import UserRepository, CondoRepository
from app.services.user_service import UserService
from app.services.condo_service import CondoService
from app.cli.menu import MenuCLI


@pytest.fixture
def cli_builder(tmp_path: Path):
    """Factory para criar uma instância *nova* do CLI (sistema sob teste) com DB/exports isolados.
    Uso: cli, export_dir = cli_builder()
    """
    counter = itertools.count(1)

    def _make():
        n = next(counter)
        db_path = tmp_path / f"func_{n}.db"
        export_dir = tmp_path / f"exports_{n}"
        db = SQLiteDatabase(str(db_path))
        users_repo = UserRepository(db)
        condos_repo = CondoRepository(db)
        user_svc = UserService(users_repo, condos_repo)
        condo_svc = CondoService(condos_repo, users_repo)
        cli = MenuCLI(user_svc, condo_svc, str(export_dir))
        return cli, export_dir

    return _make
