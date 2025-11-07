import builtins
from pathlib import Path
import io
import os


def run_cli_with_inputs(cli, inputs, monkeypatch, capsys):
    it = iter(inputs)
    monkeypatch.setattr(builtins, "input", lambda prompt='': next(it))
    cli.run()
    return capsys.readouterr().out


def test_acceptance_register_condo_and_user_then_query_by_name(cli_builder, monkeypatch, capsys):
    cli, _ = cli_builder()
    out = run_cli_with_inputs(
        cli,
        [
            "1", "Alpha", "Lento", "2", "SP", "0.75", "50",  # cadastra condomínio
            "3", "Alice", "12B", "Alpha", "34", "elétrico", "b3950a25",  # cadastra usuário
            "4", "name", "Alice",  # consulta por nome
            "0",
        ],
        monkeypatch, capsys,
    )
    assert "Condomínio cadastrado" in out
    assert "Usuário cadastrado com ID" in out
    assert "Nome=Alice" in out


def test_reject_user_in_nonexistent_condo(cli_builder, monkeypatch, capsys):
    cli, _ = cli_builder()
    out = run_cli_with_inputs(
        cli,
        [
            "3", "Bob", "101", "SemCondo", "56", "híbrido", "0fbb65a9",  # tenta cadastrar sem condomínio
            "0",
        ],
        monkeypatch, capsys,
    )
    assert "Condomínio não encontrado" in out


def test_delete_condo_block_then_delete_after_user_removed(cli_builder, monkeypatch, capsys):
    cli, _ = cli_builder()
    out = run_cli_with_inputs(
        cli,
        [
            # cria condomínio Beta (id 1) e usuário (id 1)
            "1", "Beta", "Rápido", "1", "RJ", "1.00", "10",
            "3", "Carol", "1", "Beta", "11", "elétrico", "aa11bb22",
            # tenta deletar condomínio com usuário dentro → bloqueia
            "10", "1",
            # deleta usuário e tenta de novo
            "9", "1",
            "10", "1",
            "0",
        ],
        monkeypatch, capsys,
    )
    assert "não permitida" in out  # bloqueio
    assert "Condomínio" in out and "deletado" in out  # sucesso final


def test_import_condos_from_txt_functional(cli_builder, tmp_path: Path, monkeypatch, capsys):
    cli, _ = cli_builder()
    condos_txt = tmp_path / "condominios.txt"
    condos_txt.write_text(
        """# nome;tipo_carregador;qtde_carregadores;estado;preco_kwh;qtde_apartamentos
Gamma;Lento;2;SP;0.80;60
Delta;Rápido;3;MG;0.95;120
""",
        encoding="utf-8",
    )
    out = run_cli_with_inputs(
        cli,
        [
            "2", str(condos_txt),  # importar
            "5", "name", "Gamma",  # consultar por nome
            "0",
        ],
        monkeypatch, capsys,
    )
    assert "2 condomínio(s) importado(s)." in out
    assert "Nome=Gamma" in out


def test_import_users_from_txt_functional(cli_builder, tmp_path: Path, monkeypatch, capsys):
    cli, _ = cli_builder()
    # primeiro importa condomínios
    condos_txt = tmp_path / "condominios.txt"
    condos_txt.write_text(
        """Alpha;Lento;2;SP;0.75;50
Beta;Rápido;3;RJ;1.10;80
""",
        encoding="utf-8",
    )
    users_txt = tmp_path / "usuarios.txt"
    users_txt.write_text(
        """# nome;apartamento;condominio;final_placa;tipo_veiculo;rfid
Carla;22A;Alpha;90;elétrico;abcDEF12
Rafa;801;Beta;07;híbrido;deadBEEF
Bad;1;SemCondo;00;elétrico;0011ZZ11
""",
        encoding="utf-8",
    )
    out = run_cli_with_inputs(
        cli,
        [
            "2", str(condos_txt),  # importar condos
            "13", str(users_txt),  # importar users
            "0",
        ],
        monkeypatch, capsys,
    )
    assert "Importação concluída: 2 criado(s), 1 falha(s)." in out


def test_register_set_and_view_measure_functional(cli_builder, monkeypatch, capsys):
    cli, _ = cli_builder()
    out = run_cli_with_inputs(
        cli,
        [
            "1", "Alpha", "Lento", "2", "SP", "0.75", "50",
            "3", "Dora", "12C", "Alpha", "34", "elétrico", "b3950a25",
            "8", "1", "set", "12.5", "9.37", "45",
            "8", "1", "ver",
            "0",
        ],
        monkeypatch, capsys,
    )
    assert "Medida registrada." in out
    assert "12.500" in out and "R$ 9.37" in out


def test_export_users_csv_functional(cli_builder, monkeypatch, capsys):
    cli, export_dir = cli_builder()
    out = run_cli_with_inputs(
        cli,
        [
            "1", "Alpha", "Lento", "2", "SP", "0.75", "50",
            "3", "Eva", "10", "Alpha", "01", "híbrido", "0fbb65a9",
            "11",  # exportar usuários
            "0",
        ],
        monkeypatch, capsys,
    )
    users_csv = export_dir / "users.csv"
    assert users_csv.exists()
    txt = users_csv.read_text(encoding="utf-8")
    assert "ID;Nome;RFID" in txt and "Eva" in txt


def test_export_condos_csv_functional(cli_builder, monkeypatch, capsys):
    cli, export_dir = cli_builder()
    out = run_cli_with_inputs(
        cli,
        [
            "1", "Zeta", "Rápido", "3", "SC", "1.05", "90",
            "12",  # exportar condomínios
            "0",
        ],
        monkeypatch, capsys,
    )
    condos_csv = export_dir / "condos.csv"
    assert condos_csv.exists()
    txt = condos_csv.read_text(encoding="utf-8")
    assert "ID;Nome;Apts" in txt and "Zeta" in txt


def test_update_user_change_rfid_functional(cli_builder, monkeypatch, capsys):
    cli, _ = cli_builder()
    out = run_cli_with_inputs(
        cli,
        [
            "1", "Alpha", "Lento", "2", "SP", "0.75", "50",
            "3", "Lia", "44", "Alpha", "22", "elétrico", "a1b2c3d4",
            "6", "1",  # atualizar usuário id 1
            "", "", "", "", "", "00ff11aa",  # mantém campos, muda RFID
            "4", "id", "1",  # consultar por id
            "0",
        ],
        monkeypatch, capsys,
    )
    assert "Usuário atualizado." in out
    assert "RFID=00ff11aa" in out


def test_update_condo_change_price_functional(cli_builder, monkeypatch, capsys):
    cli, _ = cli_builder()
    out = run_cli_with_inputs(
        cli,
        [
            "1", "Theta", "Lento", "1", "PR", "0.80", "30",
            "7", "1",  # atualizar condomínio id 1
            "", "", "", "", "1.23", "",  # só muda preço kWh
            "5", "id", "1",  # consultar
            "0",
        ],
        monkeypatch, capsys,
    )
    assert "Condomínio atualizado." in out
    assert "Preço=R$ 1.230/kWh" in out
