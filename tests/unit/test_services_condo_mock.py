from app.domain.models import Condo


def test_register_and_get_condo(services_mock):
    user_service, condo_service = services_mock
    cid = condo_service.register_condo("Alpha", 50, 2, "Lento", "SP", 0.75)
    c = condo_service.get_condo("id", str(cid))
    assert c and c.name == "Alpha"
    c2 = condo_service.get_condo("name", "Alpha")
    assert c2 and c2.id == cid


def test_update_condo(services_mock):
    user_service, condo_service = services_mock
    cid = condo_service.register_condo("Alpha", 50, 2, "Lento", "SP", 0.75)
    c = condo_service.get_condo("id", str(cid))
    c.chargers_count = 3
    condo_service.update_condo(c)
    c2 = condo_service.get_condo("id", str(cid))
    assert c2.chargers_count == 3


def test_delete_condo_block_when_users(services_mock):
    user_service, condo_service = services_mock
    condo_service.register_condo("Beta", 100, 3, "Rápido", "RJ", 1.0)
    uid = user_service.register_user("Bob", "1001", "Beta", "56", "híbrido", "0fbb65a9")
    ok, msg = condo_service.delete_condo(1)
    assert ok is False and "não permitida" in msg
    user_service.delete_user(uid)
    ok, msg = condo_service.delete_condo(1)
    assert ok is True


def test_import_condos_from_txt_ignores_duplicates(services_mock, tmp_path):
    user_service, condo_service = services_mock
    p = tmp_path / "condos.txt"
    p.write_text("""Alpha;Lento;2;SP;0.75;50
Alpha;Rápido;3;SP;0.95;70
Beta;Rápido;3;RJ;1.10;80
""", encoding="utf-8")
    created = condo_service.import_from_txt(str(p))
    assert created == 2
