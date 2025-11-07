# app/schema_sql.py
SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS condos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    apartments_count INTEGER NOT NULL,
    chargers_count INTEGER NOT NULL,
    charger_type TEXT NOT NULL, -- Lento, Rápido
    state TEXT NOT NULL,
    energy_price REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    apartment TEXT NOT NULL,
    condo TEXT NOT NULL,
    plate_ending TEXT NOT NULL, -- últimos 2 dígitos
    vehicle_type TEXT NOT NULL, -- híbrido ou elétrico
    rfid_code TEXT NOT NULL UNIQUE, -- novo campo obrigatório e único
    last_cost REAL,
    last_energy REAL,
    last_time_minutes REAL,
    FOREIGN KEY (condo) REFERENCES condos(name) ON UPDATE CASCADE ON DELETE RESTRICT
);
"""
