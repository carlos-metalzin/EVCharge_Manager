from __future__ import annotations
import logging
from .config import AppConfig
from .logging_config import setup_logging
from .infrastructure.db import SQLiteDatabase
from .infrastructure.repositories import UserRepository, CondoRepository
from .services.user_service import UserService
from .services.condo_service import CondoService
from .cli.menu import MenuCLI

def main() -> None:
    cfg = AppConfig.load("config.yaml")
    setup_logging(cfg.log_level, cfg.log_file)
    logging.getLogger(__name__).info("Iniciando EVCharge Manager")


    # DI: injeta implementações concretas
    db = SQLiteDatabase(cfg.database_path)
    users_repo = UserRepository(db)
    condos_repo = CondoRepository(db)


    user_service = UserService(users_repo, condos_repo)
    condo_service = CondoService(condos_repo, users_repo)


    cli = MenuCLI(user_service, condo_service, export_dir=cfg.export_path)
    cli.run()

if __name__ == "__main__":
    main()