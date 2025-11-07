from __future__ import annotations
import sqlite3
from pathlib import Path
import logging
from typing import Optional
from ..domain.interfaces import IDatabase
from ..schema_sql import SCHEMA_SQL # type: ignore


logger = logging.getLogger(__name__)




class SQLiteDatabase(IDatabase):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()


    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn


    def _ensure_schema(self) -> None:
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript(SCHEMA_SQL)
            conn.commit()
            logger.debug("Esquema do banco verificado/criado.")
        finally:
            conn.close()