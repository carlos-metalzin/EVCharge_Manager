from __future__ import annotations
import csv
import logging
from pathlib import Path
from typing import Callable
from ..services.user_service import UserService
from ..services.condo_service import CondoService
from ..utils.validators import non_empty_str, to_float, to_int, validate_rfid

logger = logging.getLogger(__name__)


class MenuCLI:
    def __init__(self, user_service: UserService, condo_service: CondoService, export_dir: str) -> None:
        self.user_service = user_service
        self.condo_service = condo_service
        self.export_dir = export_dir
        Path(self.export_dir).mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        while True:
            print("=== EVCharge Manager ===")
            print("1) Cadastrar condomínio")
            print("2) Importar condomínios de TXT")
            print("3) Cadastrar usuário")
            print("4) Consultar usuário (por ID ou nome)")
            print("5) Consultar condomínio (por ID ou nome)")
            print("6) Atualizar usuário")
            print("7) Atualizar condomínio")
            print("8) Registrar/Ver última medida de usuário")
            print("9) Deletar usuário")
            print("10) Deletar condomínio")
            print("11) Listar usuários e exportar CSV")
            print("12) Listar condomínios e exportar CSV")
            print("13) Importar usuários de TXT")
            print("0) Sair")
            op = input("> Escolha: ").strip()

            try:
                if op == "1":
                    self._cad_condo()
                elif op == "2":
                    self._import_txt_condos()
                elif op == "3":
                    self._cad_user()
                elif op == "4":
                    self._consult_user()
                elif op == "5":
                    self._consult_condo()
                elif op == "6":
                    self._update_user()
                elif op == "7":
                    self._update_condo()
                elif op == "8":
                    self._measures()
                elif op == "9":
                    self._delete_user()
                elif op == "10":
                    self._delete_condo()
                elif op == "11":
                    self._list_users_export()
                elif op == "12":
                    self._list_condos_export()
                elif op == "13":
                    self._import_txt_users()
                elif op == "0":
                    print("Até mais!")
                    break
                else:
                    print("Opção inválida.")
            except Exception as e:
                logger.exception("Erro na operação: %s", e)
                print(f"Erro: {e}")

    def _cad_condo(self) -> None:
        name = non_empty_str(input("Nome do condomínio: "), "Nome")
        charger_type = non_empty_str(input("Tipo do carregador (Lento/Rápido): "), "Tipo")
        chargers_count = to_int(input("Quantidade de carregadores: "), "Quantidade de carregadores")
        state = non_empty_str(input("Estado (UF): "), "Estado")
        energy_price = to_float(input("Preço de energia (R$/kWh): "), "Preço de energia")
        apartments_count = to_int(input("Nº de apartamentos: "), "Nº apartamentos")
        cid = self.condo_service.register_condo(name, apartments_count, chargers_count, charger_type, state, energy_price)
        print(f"Condomínio cadastrado com ID {cid}")

    def _import_txt_condos(self) -> None:
        path = non_empty_str(input("Caminho do arquivo TXT de condomínios: "), "Arquivo")
        created = self.condo_service.import_from_txt(path)
        print(f"{created} condomínio(s) importado(s).")

    def _cad_user(self) -> None:
        name = non_empty_str(input("Nome do morador: "), "Nome")
        apartment = non_empty_str(input("Apartamento: "), "Apartamento")
        condo = non_empty_str(input("Condomínio (nome): "), "Condomínio")
        plate_ending = non_empty_str(input("Últimos 2 dígitos da placa: "), "Final da placa")
        vehicle_type = non_empty_str(input("Tipo do veículo (híbrido/elétrico): "), "Tipo")
        rfid = validate_rfid(input("Código RFID (8 hex, ex.: b3950a25): "))
        uid = self.user_service.register_user(name, apartment, condo, plate_ending, vehicle_type, rfid)
        print(f"Usuário cadastrado com ID {uid}")

    def _import_txt_users(self) -> None:
        path = non_empty_str(input("Caminho do arquivo TXT de usuários: "), "Arquivo")
        ok, fail, errors = self.user_service.import_from_txt(path)
        print(f"Importação concluída: {ok} criado(s), {fail} falha(s).")
        if errors:
            print("Erros:")
            for e in errors:
                print(" - ", e)

    def _consult_user(self) -> None:
        by = non_empty_str(input("Consultar por 'id' ou 'name': "), "Modo")
        value = non_empty_str(input("Valor: "), "Valor")
        u = self.user_service.get_user(by, value)
        if not u:
            print("Usuário não encontrado.")
            return
        print(
            f"ID={u.id} | Nome={u.name} | RFID={u.rfid_code} | Ap={u.apartment} | Cond={u.condo} | Placa={u.plate_ending} | Tipo={u.vehicle_type} | "
            f"Último: energia={u.last_energy} kWh, custo={u.last_cost}, tempo={u.last_time_minutes} min"
        )

    def _consult_condo(self) -> None:
        by = non_empty_str(input("Consultar por 'id' ou 'name': "), "Modo")
        value = non_empty_str(input("Valor: "), "Valor")
        c = self.condo_service.get_condo(by, value)
        if not c:
            print("Condomínio não encontrado.")
            return
        print(
            f"ID={c.id} | Nome={c.name} | Apts={c.apartments_count} | Carregadores={c.chargers_count} ({c.charger_type}) | "
            f"UF={c.state} | Preço=R$ {c.energy_price:.3f}/kWh"
        )

    def _update_user(self) -> None:
        uid = to_int(input("ID do usuário para atualizar: "), "ID")
        u = self.user_service.get_user("id", str(uid))
        if not u:
            print("Usuário não encontrado.")
            return
        # campos opcionais; se vazio, mantém
        name = input(f"Nome [{u.name}]: ").strip() or u.name
        ap = input(f"Apartamento [{u.apartment}]: ").strip() or u.apartment
        cond = input(f"Condomínio [{u.condo}]: ").strip() or u.condo
        plate = input(f"Final da placa [{u.plate_ending}]: ").strip() or u.plate_ending
        vtype = input(f"Tipo do veículo [{u.vehicle_type}]: ").strip() or u.vehicle_type
        rfid_in = input(f"RFID [{u.rfid_code}]: ").strip()
        rfid = validate_rfid(rfid_in) if rfid_in else u.rfid_code
        u.name, u.apartment, u.condo, u.plate_ending, u.vehicle_type, u.rfid_code = name, ap, cond, plate, vtype, rfid
        self.user_service.update_user(u)
        print("Usuário atualizado.")

    def _update_condo(self) -> None:
        cid = to_int(input("ID do condomínio para atualizar: "), "ID")
        c = self.condo_service.get_condo("id", str(cid))
        if not c:
            print("Condomínio não encontrado.")
            return
        name = input(f"Nome [{c.name}]: ").strip() or c.name
        ctype = input(f"Tipo carregador [{c.charger_type}]: ").strip() or c.charger_type
        ccnt = input(f"Qtde carregadores [{c.chargers_count}]: ").strip()
        state = input(f"UF [{c.state}]: ").strip() or c.state
        price = input(f"Preço kWh [{c.energy_price}]: ").strip()
        apts = input(f"Qtde apartamentos [{c.apartments_count}]: ").strip()
        c.name = name
        c.charger_type = ctype
        c.chargers_count = int(ccnt) if ccnt else c.chargers_count
        c.state = state
        c.energy_price = float(price.replace(",", ".")) if price else c.energy_price
        c.apartments_count = int(apts) if apts else c.apartments_count
        self.condo_service.update_condo(c)
        print("Condomínio atualizado.")

    def _measures(self) -> None:
        uid = to_int(input("ID do usuário: "), "ID")
        action = input("Digite 'ver' para ler ou 'set' para registrar medida: ").strip().lower()
        if action == "ver":
            msg = self.user_service.read_last_measure(uid)
            print(msg)
        elif action == "set":
            e = to_float(input("Energia (kWh): "), "Energia")
            c = to_float(input("Custo (R$): "), "Custo")
            t = to_float(input("Tempo (min): "), "Tempo")
            self.user_service.set_last_measure(uid, e, c, t)
            print("Medida registrada.")
        else:
            print("Ação inválida.")

    def _delete_user(self) -> None:
        uid = to_int(input("ID do usuário: "), "ID")
        self.user_service.delete_user(uid)
        print("Usuário deletado.")

    def _delete_condo(self) -> None:
        cid = to_int(input("ID do condomínio: "), "ID")
        ok, msg = self.condo_service.delete_condo(cid)
        print(msg)

    def _list_users_export(self) -> None:
        users = list(self.user_service.list_users())
        for u in users:
            print(f"{u.id};{u.name};{u.rfid_code};{u.apartment};{u.condo};{u.plate_ending};{u.vehicle_type};{u.last_energy};{u.last_cost};{u.last_time_minutes}")
        if users:
            path = Path(self.export_dir) / "users.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, delimiter=';')
                w.writerow(["ID","Nome","RFID","Apartamento","Condomínio","FinalPlaca","Tipo","UltEnergia","UltCusto","UltTempoMin"])
                for u in users:
                    w.writerow([u.id,u.name,u.rfid_code,u.apartment,u.condo,u.plate_ending,u.vehicle_type,u.last_energy,u.last_cost,u.last_time_minutes])
            print(f"Exportado para {path}")
        else:
            print("Sem usuários cadastrados.")

    def _list_condos_export(self) -> None:
        condos = list(self.condo_service.list_condos())
        for c in condos:
            print(f"{c.id};{c.name};{c.apartments_count};{c.chargers_count};{c.charger_type};{c.state};{c.energy_price}")
        if condos:
            path = Path(self.export_dir) / "condos.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, delimiter=';')
                w.writerow(["ID","Nome","Apts","QtdeCarreg","Tipo","UF","PrecoKWh"])
                for c in condos:
                    w.writerow([c.id,c.name,c.apartments_count,c.chargers_count,c.charger_type,c.state,c.energy_price])
            print(f"Exportado para {path}")
        else:
            print("Sem condomínios cadastrados.")
