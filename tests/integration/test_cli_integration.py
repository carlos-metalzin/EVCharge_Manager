import builtins
from pathlib import Path
from app.cli.menu import MenuCLI


def test_cli_basic_flow_add_condo_and_user(services_db, tmp_path: Path, monkeypatch, capsys):
    user_svc, condo_svc = services_db
    export_dir = tmp_path / "exports"
    cli = MenuCLI(user_svc, condo_svc, str(export_dir))

    # sequência de entradas: cadastrar condomínio (1) -> dados -> cadastrar usuário (3) -> dados -> sair (0)
    inputs = iter([
        "1",                 # menu: Cadastrar condomínio
        "Sigma Plaza",       # nome
        "Lento",             # tipo carregador
        "2",                 # qtde carregadores
        "SP",                # estado
        "0.88",              # preço kWh
        "40",                # nº aptos
        "3",                 # menu: Cadastrar usuário
        "Alice",             # nome morador
        "12B",               # apartamento
        "Sigma Plaza",       # condomínio
        "34",                # final placa
        "elétrico",          # tipo veículo
        "a0b1c2d3",          # RFID
        "0",                 # sair
    ])

    monkeypatch.setattr(builtins, "input", lambda prompt='': next(inputs))

    cli.run()

    out = capsys.readouterr().out
    assert "Condomínio cadastrado com ID" in out
    assert "Usuário cadastrado com ID" in out
