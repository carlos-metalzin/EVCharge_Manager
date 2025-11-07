import os
import sqlite3
from pathlib import Path
import pytest

from app.domain.models import User, Condo
from app.infrastructure.db import SQLiteDatabase
from app.infrastructure.repositories import UserRepository, CondoRepository


def test_full_flow_user_condo_measure_update_delete(services_db, sample_condos):
    user_svc, condo_svc = services_db

    # 1) Cadastrar usuário em condomínio existente
    uid = user_svc.register_user(
        name="Ana",
        apartment="12B",
        condo_name="Alpha",
        plate_ending="34",
        vehicle_type="elétrico",
        rfid_code="b3950a25",
    )
    u = user_svc.get_user("id", str(uid))
    assert u and u.condo == "Alpha"

    # 2) Registrar medida e ler
    user_svc.set_last_measure(uid, 10.0, 7.5, 30)
    msg = user_svc.read_last_measure(uid)
    assert "10.000" in msg and "R$ 7.50" in msg

    # 3) Atualizar usuário (mudar apartamento e tipo)
    u.apartment = "14C"
    u.vehicle_type = "HÍBRIDO"
    user_svc.update_user(u)
    u2 = user_svc.get_user("id", str(uid))
    assert u2.apartment == "14C" and u2.vehicle_type == "híbrido"

    # 4) Deletar usuário e então deletar condomínio
    user_svc.delete_user(uid)
    ok, msg = condo_svc.delete_condo(sample_condos["Alpha"])  # não há mais usuários
    assert ok is True


descriptions = ["híbrido", "HÍBRIDO", "eletrico"]
@pytest.mark.parametrize("vtype", descriptions)
def test_register_user_vehicle_types_variants(services_db, sample_condos, vtype):
    user_svc, condo_svc = services_db
    uid = user_svc.register_user("Bob", "1001", "Beta", "56", vtype, "0fbb65a9")
    u = user_svc.get_user("id", str(uid))
    assert u and u.vehicle_type in {"híbrido", "elétrico"}


def test_import_condos_and_users_from_txt_integration(services_db, tmp_path: Path):
    user_svc, condo_svc = services_db

    condos_txt = tmp_path / "condominios.txt"
    condos_txt.write_text(
        """# nome;tipo_carregador;qtde_carregadores;estado;preco_kwh;qtde_apartamentos
Gamma;Lento;2;SP;0.80;60
Delta;Rápido;3;MG;0.95;120
""",
        encoding="utf-8",
    )
    created = condo_svc.import_from_txt(str(condos_txt))
    assert created == 2

    users_txt = tmp_path / "usuarios.txt"
    users_txt.write_text(
        """# nome;apartamento;condominio;final_placa;tipo_veiculo;rfid
Carla;22A;Gamma;90;elétrico;abcDEF12
Rafa;801;Delta;07;híbrido;deadBEEF
Bad;1;SemCondo;00;elétrico;0011ZZ11
""",
        encoding="utf-8",
    )
    ok, fail, errors = user_svc.import_from_txt(str(users_txt))
    assert ok == 2 and fail == 1 and any("Condomínio" in e for e in errors)


def test_delete_condo_block_then_allow(services_db, sample_condos):
    user_svc, condo_svc = services_db
    # cadastra um usuário em Beta
    uid = user_svc.register_user("Eve", "33", "Beta", "12", "elétrico", "aa11bb22")

    ok, msg = condo_svc.delete_condo(sample_condos["Beta"])  # deve bloquear
    assert ok is False and "não permitida" in msg

    user_svc.delete_user(uid)
    ok, msg = condo_svc.delete_condo(sample_condos["Beta"])  # agora libera
    assert ok is True


def test_unique_rfid_enforced_with_db(services_db, sample_condos):
    user_svc, condo_svc = services_db
    user_svc.register_user("Ana", "1", "Alpha", "11", "elétrico", "deadbeef")
    with pytest.raises(sqlite3.IntegrityError):
        user_svc.register_user("Bob", "2", "Alpha", "22", "híbrido", "deadbeef")


def test_persistence_across_new_repositories(tmp_path: Path):
    # cria DB e grava um usuário
    db_path = tmp_path / "persist.db"
    db = SQLiteDatabase(str(db_path))
    users = UserRepository(db)
    condos = CondoRepository(db)
    condos.create(Condo(id=None, name="Omega", apartments_count=10, chargers_count=1, charger_type="Lento", state="SP", energy_price=0.7))
    uid = users.create(User(id=None, name="Zoe", apartment="1", condo="Omega", plate_ending="00", vehicle_type="elétrico", rfid_code="1122aabb"))

    # reabre com novos objetos (simulando outro ponto do sistema)
    db2 = SQLiteDatabase(str(db_path))
    users2 = UserRepository(db2)
    u = users2.get_by_id(uid)
    assert u and u.name == "Zoe"


def test_get_by_id_and_name_consistency(services_db, sample_condos):
    user_svc, _ = services_db
    uid = user_svc.register_user("Kai", "PH1", "Alpha", "77", "elétrico", "a1b2c3d4")
    u_by_id = user_svc.get_user("id", str(uid))
    u_by_name = user_svc.get_user("name", "Kai")
    assert u_by_id and u_by_name and u_by_id.id == u_by_name.id


def test_read_last_measure_without_set(services_db, sample_condos):
    user_svc, _ = services_db
    uid = user_svc.register_user("Mia", "45", "Alpha", "55", "híbrido", "ffeeddcc")
    msg = user_svc.read_last_measure(uid)
    assert "não possui" in msg


def test_update_user_change_to_nonexistent_condo_raises(services_db, sample_condos):
    user_svc, _ = services_db
    uid = user_svc.register_user("Noah", "702", "Alpha", "21", "elétrico", "abcd1234")
    u = user_svc.get_user("id", str(uid))
    u.condo = "X-NAO-EXISTE"
    with pytest.raises(ValueError):
        user_svc.update_user(u)
