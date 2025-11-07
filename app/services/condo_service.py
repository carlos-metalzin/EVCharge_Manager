from __future__ import annotations
import logging
from typing import Optional, Iterable, Tuple
from ..domain.models import Condo
from ..domain.interfaces import ICondoRepository, IUserRepository
from ..infrastructure.file_loader import CondoFileLoader


logger = logging.getLogger(__name__)

class CondoService:
    def __init__(self, condos: ICondoRepository, users: IUserRepository) -> None:
        self.condos = condos
        self.users = users

    def register_condo(
        self,
        name: str,
        apartments_count: int,
        chargers_count: int,
        charger_type: str,
        state: str,
        energy_price: float,
    ) -> int:
        condo = self.condos.get_by_name(name)

        if condo:
            raise ValueError("Já existe um condomínio com esse nome.")
        c = Condo(
            id=None,
            name=name,
            apartments_count=apartments_count,
            chargers_count=chargers_count,
            charger_type=charger_type,
            state=state,
            energy_price=energy_price,
        )
        cid = self.condos.create(c)
        logger.info("Condomínio '%s' cadastrado com ID %s", name, cid)
        return cid

    def import_from_txt(self, path: str) -> int:
        condos = CondoFileLoader.load_from_txt(path)
        created = 0
        for c in condos:
            if self.condos.get_by_name(c.name):
                logger.warning("Condomínio já existe e foi ignorado: %s", c.name)
                continue
            self.condos.create(c)
            created += 1
        logger.info("Importação concluída. %s condomínios criados.", created)
        return created

    def get_condo(self, by: str, value: str) -> Optional[Condo]:
        if by == "id":
            return self.condos.get_by_id(int(value))
        elif by == "name":
            return self.condos.get_by_name(value)
        else:
            raise ValueError("Parâmetro 'by' deve ser 'id' ou 'name'")

    def list_condos(self) -> Iterable[Condo]:
        return self.condos.list_all()

    def update_condo(self, condo: Condo) -> None:
        self.condos.update(condo)
        logger.info("Condomínio ID %s atualizado.", condo.id)

    def delete_condo(self, condo_id: int) -> Tuple[bool, str]:
        condo = self.condos.get_by_id(condo_id)
        if not condo:
            return False, "Condomínio não encontrado."
        if self.users.count_by_condo(condo.name) > 0:
            return False, "Existem usuários vinculados a este condomínio; exclusão não permitida."
        self.condos.delete(condo_id)
        logger.info("Condomínio ID %s deletado.", condo_id)
        return True, "Condomínio deletado com sucesso."


