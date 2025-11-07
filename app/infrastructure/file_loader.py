from __future__ import annotations
from pathlib import Path
from typing import List, Dict
from ..domain.models import Condo


class CondoFileLoader:
    """Lê condomínios de um arquivo .txt no formato:
    nome;tipo_carregador;qtde_carregadores;estado;preco_kwh;qtde_apartamentos

    Exemplo de linha:
    Condominio Solar;Lento;4;SP;0.92;120
    """

    @staticmethod
    def load_from_txt(path: str, encoding: str = "utf-8") -> List[Condo]:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        condos: List[Condo] = []
        for idx, line in enumerate(p.read_text(encoding=encoding).splitlines(), start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [x.strip() for x in line.split(";")]
            if len(parts) != 6:
                raise ValueError(
                    f"Linha {idx} inválida: '{line}'. Esperado 6 campos: nome;tipo;qtde;estado;preco;apts"
                )
            name, charger_type, chargers_count, state, price, apts = parts
            condos.append(
                Condo(
                    id=None,
                    name=name,
                    charger_type=charger_type,
                    chargers_count=int(chargers_count),
                    state=state,
                    energy_price=float(price),
                    apartments_count=int(apts),
                )
            )
        return condos


class UserFileLoader:
    """Lê usuários de um arquivo .txt no formato:
    nome;apartamento;condominio;final_placa;tipo_veiculo;rfid

    Exemplos de linhas válidas:
    Ana Silva;12B;Conjunto Solar das Palmeiras;34;elétrico;b3950a25
    João Souza;1001;Residencial Atlântico;56;HÍBRIDO;0fbb65a9
    """

    @staticmethod
    def load_from_txt(path: str, encoding: str = "utf-8") -> List[Dict[str, str]]:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        users: List[Dict[str, str]] = []
        for idx, line in enumerate(p.read_text(encoding=encoding).splitlines(), start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [x.strip() for x in line.split(";")]
            if len(parts) != 6:
                raise ValueError(
                    f"Linha {idx} inválida: '{line}'. Esperado 6 campos: nome;ap;condo;placa;tipo;rfid"
                )
            name, apartment, condo, plate_ending, vehicle_type, rfid = parts
            users.append({
                "name": name,
                "apartment": apartment,
                "condo": condo,
                "plate_ending": plate_ending,
                "vehicle_type": vehicle_type,
                "rfid_code": rfid,
            })
        return users