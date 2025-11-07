# ==============================
# File: app/config.py
# ==============================
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


try:
    import yaml # type: ignore
except Exception:
    yaml = None # leitura YAML opcional; se ausente, usa JSON/env




class AppConfig:
    """Lê configuração externa (YAML, JSON e variáveis de ambiente)."""


    def __init__(self, data: Dict[str, Any]) -> None:
        self.database_path: str = data.get("database", {}).get("path", os.getenv("DB_PATH", "evcharge.db"))
        logging_cfg = data.get("logging", {})
        self.log_level: str = logging_cfg.get("level", os.getenv("LOG_LEVEL", "INFO"))
        self.log_file: Optional[str] = logging_cfg.get("file", os.getenv("LOG_FILE", "evcharge.log"))
        cli_cfg = data.get("cli", {})
        self.export_path: str = cli_cfg.get("export_path", os.getenv("EXPORT_PATH", "exports"))


    @staticmethod
    def load(config_file: str = "config.yaml") -> "AppConfig":
        path = Path(config_file)
        data: Dict[str, Any] = {}
        if path.exists():
            if path.suffix.lower() in (".yaml", ".yml") and yaml:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            elif path.suffix.lower() == ".json":
                data = json.loads(path.read_text(encoding="utf-8"))
            else:
                # tenta YAML, se falhar, tenta JSON
                try:
                    if yaml:
                        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                    else:
                        raise RuntimeError
                except Exception:
                    try:
                        data = json.loads(path.read_text(encoding="utf-8"))
                    except Exception:
                        data = {}
        # Merge mínimo com env já feito no __init__
        return AppConfig(data)

