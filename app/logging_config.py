from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional




def setup_logging(level: str = "INFO", filename: Optional[str] = None) -> None:
    log_level = getattr(logging, level.upper(), logging.INFO)
    handlers = []
    # Console handler
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    handlers.append(console)


    # File handler (opcional)
    if filename:
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        fh = RotatingFileHandler(filename, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        fh.setLevel(log_level)
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        handlers.append(fh)


    logging.basicConfig(level=log_level, handlers=handlers, force=True)