from __future__ import annotations
import logging
from typing import Optional, Iterable, Tuple
from ..domain.models import User
from ..domain.interfaces import IUserRepository, ICondoRepository
from ..infrastructure.file_loader import UserFileLoader
from ..utils.validators import validate_rfid, validate_vehicle_type

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, users: IUserRepository, condos: ICondoRepository) -> None:
        self.users = users
        self.condos = condos

    def register_user(
        self,
        name: str,
        apartment: str,
        condo_name: str,
        plate_ending: str,
        vehicle_type: str,
        rfid_code: str,
    ) -> int:
        # valida existência do condomínio
        if not self.condos.get_by_name(condo_name):
            logger.warning("Tentativa de cadastro em condomínio inexistente: %s", condo_name)
            raise ValueError("Condomínio não encontrado. Cadastre o condomínio primeiro.")
        user = User(
            id=None,
            name=name,
            apartment=apartment,
            condo=condo_name,
            plate_ending=plate_ending,
            vehicle_type=validate_vehicle_type(vehicle_type),
            rfid_code=validate_rfid(rfid_code),
        )
        uid = self.users.create(user)
        logger.info("Usuário '%s' cadastrado com ID %s", name, uid)
        return uid

    def import_from_txt(self, path: str) -> Tuple[int, int, list[str]]:
        """Importa usuários de um TXT. Retorna (sucessos, falhas, erros).
        Regras: valida RFID, tipo de veículo e existência do condomínio.
        """
        records = UserFileLoader.load_from_txt(path)
        ok, fail = 0, 0
        errors: list[str] = []
        for i, r in enumerate(records, start=1):
            try:
                self.register_user(
                    r["name"], r["apartment"], r["condo"], r["plate_ending"], r["vehicle_type"], r["rfid_code"]
                )
                ok += 1
            except Exception as e:
                fail += 1
                errors.append(f"linha {i}: {e}")
        logger.info("Import usuários: ok=%s, falhas=%s", ok, fail)
        return ok, fail, errors

    def get_user(self, by: str, value: str) -> Optional[User]:
        if by == "id":
            return self.users.get_by_id(int(value))
        elif by == "name":
            return self.users.get_by_name(value)
        else:
            raise ValueError("Parâmetro 'by' deve ser 'id' ou 'name'")

    def list_users(self) -> Iterable[User]:
        return self.users.list_all()

    def update_user(self, user: User) -> None:
        # se mudar o condomínio, checar existência
        if user.condo and not self.condos.get_by_name(user.condo):
            raise ValueError("Condomínio informado não existe.")
        # normalizações
        user.vehicle_type = validate_vehicle_type(user.vehicle_type)
        user.rfid_code = validate_rfid(user.rfid_code)
        self.users.update(user)
        logger.info("Usuário ID %s atualizado.", user.id)

    def delete_user(self, user_id: int) -> None:
        self.users.delete(user_id)
        logger.info("Usuário ID %s deletado.", user_id)

    def set_last_measure(
        self, user_id: int, energy_kwh: float, cost_r: float, time_minutes: float
    ) -> None:
        user = self.users.get_by_id(user_id)
        if not user:
            raise ValueError("Usuário não encontrado.")
        user.last_energy = energy_kwh
        user.last_cost = cost_r
        user.last_time_minutes = time_minutes
        self.users.update(user)
        logger.info("Última medida atualizada para usuário ID %s.", user_id)

    def read_last_measure(self, user_id: int) -> str:
        user = self.users.get_by_id(user_id)
        if not user:
            raise ValueError("Usuário não encontrado.")
        if user.last_energy is None or user.last_cost is None or user.last_time_minutes is None:
            return "Usuário ainda não possui medidas de carregamento registradas."
        return (
            f"Energia: {user.last_energy:.3f} kWh | Custo: R$ {user.last_cost:.2f} | Tempo: {user.last_time_minutes:.1f} min"
        )
