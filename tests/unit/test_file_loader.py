from pathlib import Path
import pytest
from app.infrastructure.file_loader import CondoFileLoader, UserFileLoader


def test_condo_loader_ok(tmp_path: Path):
    p = tmp_path / "condos.txt"
    p.write_text("""# nome;tipo;qtde;estado;preco;apts
Alpha;Lento;2;SP;0.75;50
Beta;Rápido;3;RJ;1.10;80
""", encoding="utf-8")
    condos = CondoFileLoader.load_from_txt(str(p))
    assert len(condos) == 2
    assert condos[0].name == "Alpha" and condos[1].charger_type == "Rápido"


def test_condo_loader_invalid_line(tmp_path: Path):
    p = tmp_path / "condos_bad.txt"
    p.write_text("Alpha;Lento;2;SP;0.75", encoding="utf-8")  # falta um campo
    with pytest.raises(ValueError):
        CondoFileLoader.load_from_txt(str(p))


def test_condo_loader_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        CondoFileLoader.load_from_txt(str(tmp_path / "inexistente.txt"))


def test_user_loader_ok(tmp_path: Path):
    p = tmp_path / "users.txt"
    p.write_text("""# nome;ap;condo;placa;tipo;rfid
Ana;12B;Alpha;34;elétrico;b3950a25
Bob;101;Beta;56;Hibrido;0fbb65a9
""", encoding="utf-8")
    items = UserFileLoader.load_from_txt(str(p))
    assert len(items) == 2
    assert items[0]["name"] == "Ana" and items[1]["rfid_code"].lower() == "0fbb65a9"


def test_user_loader_invalid_line(tmp_path: Path):
    p = tmp_path / "users_bad.txt"
    p.write_text("Ana;12B;Alpha;34;elétrico", encoding="utf-8")  # falta rfid
    with pytest.raises(ValueError):
        UserFileLoader.load_from_txt(str(p))


def test_user_loader_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        UserFileLoader.load_from_txt(str(tmp_path / "nope.txt"))

