from __future__ import annotations
from dataclasses import dataclass
from typing import Optional




@dataclass
class User:
    id: Optional[int]
    name: str
    apartment: str
    condo: str
    plate_ending: str
    vehicle_type: str # "híbrido" | "elétrico"
    rfid_code: str
    last_cost: Optional[float] = None
    last_energy: Optional[float] = None
    last_time_minutes: Optional[float] = None




@dataclass
class Condo:
    id: Optional[int]
    name: str
    apartments_count: int
    chargers_count: int
    charger_type: str # Lento | Rápido
    state: str
    energy_price: float