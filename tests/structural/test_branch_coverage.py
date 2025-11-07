import builtins
import sqlite3
from pathlib import Path
import pytest

from app.domain.models import User, Condo
from app.cli.menu import MenuCLI


def _seed_condos(services_db):
    user_svc, condo_svc = services_db
    cid_a = condo_svc.register_condo("Alpha", 50, 2, "Lento", "SP", 0.75)
    cid_b = condo_svc.register_condo("Beta", 80, 3, "Rápido", "RJ", 1.10)
    return {"Alpha": cid_a, "Beta": cid_b}


def test_user_service_get_user_invalid_by_raises(services_db):
    user_svc, condo_svc = services_db
    _seed_condos(services_db)
    with pytest.raises(ValueError):
        user_svc.get_user("email", "x@y.z")  # branch de erro


def test_user_service_read_last_measure_partial_fields(services_db):
    user_svc, condo_svc = services_db
    _seed_condos(services_db)
    uid = user_svc.register_user("Ana", "1", "Alpha", "11", "elétrico", "a1b2c3d4")
    # Força somente energia preenchida via repo (caminho parcial)
    u = user_svc.get_user("id", str(uid))
    u.last_energy = 5.0
    u.last_cost = None
    u.last_time_minutes = None
    user_svc.users.update(u)  # caixa-branca: atualiza direto no repo
    msg = user_svc.read_last_measure(uid)
    assert "não possui" in msg  # ainda assim deve informar ausência de medidas completas


def test_repositories_count_by_condo_zero(repos_db):
    users_repo, condos_repo = repos_db
    # sem inserir nada: count deve ser 0
    assert users_repo.count_by_condo("Inexistente") == 0


def test_duplicate_rfid_on_update_raises(services_db):
    user_svc, condo_svc = services_db
    _seed_condos(services_db)
    u1 = user_svc.register_user("A", "1", "Alpha", "11", "elétrico", "deadbeef")
    u2 = user_svc.register_user("B", "2", "Alpha", "22", "híbrido", "0011aabb")
    u = user_svc.get_user("id", str(u2))
    u.rfid_code = "deadbeef"  # tenta colidir com u1
    with pytest.raises(sqlite3.IntegrityError):
        user_svc.update_user(u)


def test_file_loader_invalid_numeric_structural(tmp_path: Path, services_db):
    # Cria TXT com número inválido (qtde_carregadores como texto)
    path = tmp_path / "condos_bad_num.txt"
    path.write_text(
        """NomeX;Lento;dois;SP;0.90;40
""",
        encoding="utf-8",
    )
    # Usa o CondoService.import_from_txt (exercita parser + service)
    _, condo_svc = services_db
    with pytest.raises(ValueError):
        condo_svc.import_from_txt(str(path))


def test_cli_invalid_option_branch(services_db, tmp_path, monkeypatch, capsys):
    user_svc, condo_svc = services_db
    cli = MenuCLI(user_svc, condo_svc, str(tmp_path / "exports"))
    inputs = iter([
        "999",  # opção inválida
        "0",    # sair
    ])
    monkeypatch.setattr(builtins, "input", lambda prompt='': next(inputs))
    cli.run()
    out = capsys.readouterr().out
    assert "Opção inválida" in out


def test_condo_service_delete_message_paths(services_db):
    user_svc, condo_svc = services_db
    ids = _seed_condos(services_db)
    # Sem usuários em Beta => deve conseguir
    ok, msg = condo_svc.delete_condo(ids["Beta"])  # caminho true
    assert ok is True and "deletado" in msg


def test_condo_service_delete_block_message_path(services_db):
    user_svc, condo_svc = services_db
    ids = _seed_condos(services_db)
    # Adiciona usuário em Alpha => bloqueia
    user_svc.register_user("Z", "10", "Alpha", "00", "elétrico", "0f0e0d0c")
    ok, msg = condo_svc.delete_condo(ids["Alpha"])  # caminho false
    assert ok is False and "não permitida" in msg

