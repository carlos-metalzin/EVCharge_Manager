from __future__ import annotations
import logging
from typing import Iterable, Optional, List
from ..domain.interfaces import IUserRepository, ICondoRepository, IDatabase
from ..domain.models import User, Condo

logger = logging.getLogger(__name__)


class UserRepository(IUserRepository):
    def __init__(self, db: IDatabase) -> None:
        self.db = db

    def create(self, user: User) -> int:
        logger.debug("Criando usuário: %s", user)
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO users(name, apartment, condo, plate_ending, vehicle_type, rfid_code, last_cost, last_energy, last_time_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user.name,
                    user.apartment,
                    user.condo,
                    user.plate_ending,
                    user.vehicle_type,
                    user.rfid_code,
                    user.last_cost,
                    user.last_energy,
                    user.last_time_minutes,
                ),
            )
            conn.commit()
            uid = int(cur.lastrowid)
            logger.info("Usuário criado com ID %s", uid)
            return uid

    def get_by_id(self, user_id: int) -> Optional[User]:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return User(**row) if row else None

    def get_by_name(self, name: str) -> Optional[User]:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE name = ?", (name,)).fetchone()
            return User(**row) if row else None

    def list_all(self) -> Iterable[User]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
            return [User(**row) for row in rows]

    def update(self, user: User) -> None:
        assert user.id is not None, "User.id é obrigatório para update"
        logger.debug("Atualizando usuário ID %s: %s", user.id, user)
        with self.db.connect() as conn:
            conn.execute(
                """
                UPDATE users SET name=?, apartment=?, condo=?, plate_ending=?, vehicle_type=?,
                                rfid_code=?, last_cost=?, last_energy=?, last_time_minutes=?
                WHERE id=?
                """,
                (
                    user.name,
                    user.apartment,
                    user.condo,
                    user.plate_ending,
                    user.vehicle_type,
                    user.rfid_code,
                    user.last_cost,
                    user.last_energy,
                    user.last_time_minutes,
                    user.id,
                ),
            )
            conn.commit()

    def delete(self, user_id: int) -> None:
        logger.debug("Deletando usuário ID %s", user_id)
        with self.db.connect() as conn:
            conn.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()

    def count_by_condo(self, condo_name: str) -> int:
        with self.db.connect() as conn:
            row = conn.execute("SELECT COUNT(*) as c FROM users WHERE condo=?", (condo_name,)).fetchone()
            return int(row["c"]) if row else 0


class CondoRepository(ICondoRepository):
    def __init__(self, db: IDatabase) -> None:
        self.db = db

    def create(self, condo: Condo) -> int:
        logger.debug("Criando condomínio: %s", condo)
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO condos(name, apartments_count, chargers_count, charger_type, state, energy_price)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    condo.name,
                    condo.apartments_count,
                    condo.chargers_count,
                    condo.charger_type,
                    condo.state,
                    condo.energy_price,
                ),
            )
            conn.commit()
            cid = int(cur.lastrowid)
            logger.info("Condomínio criado com ID %s", cid)
            return cid

    def get_by_id(self, condo_id: int) -> Optional[Condo]:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM condos WHERE id = ?", (condo_id,)).fetchone()
            return Condo(**row) if row else None

    def get_by_name(self, name: str) -> Optional[Condo]:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM condos WHERE name = ?", (name,)).fetchone()
            return Condo(**row) if row else None

    def list_all(self) -> Iterable[Condo]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM condos ORDER BY id").fetchall()
            return [Condo(**row) for row in rows]

    def update(self, condo: Condo) -> None:
        assert condo.id is not None, "Condo.id é obrigatório para update"
        logger.debug("Atualizando condomínio ID %s: %s", condo.id, condo)
        with self.db.connect() as conn:
            conn.execute(
                """
                UPDATE condos SET name=?, apartments_count=?, chargers_count=?, charger_type=?, state=?, energy_price=?
                WHERE id=?
                """,
                (
                    condo.name,
                    condo.apartments_count,
                    condo.chargers_count,
                    condo.charger_type,
                    condo.state,
                    condo.energy_price,
                    condo.id,
                ),
            )
            conn.commit()

    def delete(self, condo_id: int) -> None:
        logger.debug("Deletando condomínio ID %s", condo_id)
        with self.db.connect() as conn:
            conn.execute("DELETE FROM condos WHERE id=?", (condo_id,))
            conn.commit()