from pathlib import Path
import logging
import os
from app.config import AppConfig
from app.logging_config import setup_logging


def test_appconfig_yaml(tmp_path: Path, monkeypatch):
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text("""
database:
  path: my.db
logging:
  level: DEBUG
  file: logs/app.log
cli:
  export_path: out
""", encoding="utf-8")
    cfg = AppConfig.load(str(cfg_path))
    assert cfg.database_path.endswith("my.db")
    assert cfg.log_level == "DEBUG"
    assert cfg.log_file.endswith("logs/app.log")
    assert cfg.export_path == "out"


def test_appconfig_env_defaults(monkeypatch, tmp_path: Path):
    # arquivo vazio → usa env como fallback no __init__
    monkeypatch.setenv("DB_PATH", "env.db")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("LOG_FILE", "env.log")
    monkeypatch.setenv("EXPORT_PATH", "env_out")
    cfg = AppConfig.load(str(tmp_path / "nao_existe.yaml"))
    assert cfg.database_path.endswith("env.db")
    assert cfg.log_level == "WARNING"
    assert cfg.log_file == "env.log"
    assert cfg.export_path == "env_out"


def test_setup_logging_creates_file(tmp_path: Path, caplog):
    log_path = tmp_path / "test.log"
    setup_logging("DEBUG", str(log_path))
    logging.getLogger("x").debug("hello")
    assert log_path.exists()
    assert log_path.read_text(encoding="utf-8")
