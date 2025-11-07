from __future__ import annotations
import re


def non_empty_str(value: str, field: str) -> str:
    v = (value or "").strip()
    if not v:
        raise ValueError(f"{field} não pode ser vazio.")
    return v


def to_float(value: str, field: str) -> float:
    try:
        return float(value.replace(",", "."))
    except Exception:
        raise ValueError(f"{field} deve ser numérico.")


def to_int(value: str, field: str) -> int:
    try:
        return int(value)
    except Exception:
        raise ValueError(f"{field} deve ser inteiro.")


RFID_RE = re.compile(r"^[0-9a-fA-F]{8}$")


def validate_rfid(value: str) -> str:
    """Valida RFID como string hex de 8 caracteres (ex.: b3950a25).
    Normaliza para minúsculas.
    """
    v = (value or "").strip()
    if not RFID_RE.fullmatch(v):
        raise ValueError("RFID deve ser uma string hexadecimal de 8 caracteres (ex.: b3950a25).")
    return v.lower()


def validate_vehicle_type(value: str) -> str:
    """Normaliza tipo de veículo para 'híbrido' ou 'elétrico' (case/acentos tolerados)."""
    v = (value or "").strip().lower()
    v = v.replace("hibrido", "híbrido").replace("eletrico", "elétrico")
    if v not in {"híbrido", "elétrico"}:
        raise ValueError("Tipo de veículo deve ser 'híbrido' ou 'elétrico'.")
    return v