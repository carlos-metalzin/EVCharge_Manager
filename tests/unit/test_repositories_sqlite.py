import sqlite3
from app.domain.models import User


def test_user_crud_sqlite(sqlite_repos, seed_condos_sqlite):
    users_repo, condos_repo = sqlite_repos
    (alpha, beta) = seed_condos_sqlite
    uid = users_repo.create(User(id=None, name="Ana", apartment="12B", condo=alpha, plate_ending="34", vehicle_type="elétrico", rfid_code="b3950a25"))
    u = users_repo.get_by_id(uid)
    assert u and u.name == "Ana"
    u.name = "Ana Paula"
    users_repo.update(u)
    u2 = users_repo.get_by_id(uid)
    assert u2.name == "Ana Paula"
    assert users_repo.count_by_condo(alpha) == 1
    users_repo.delete(uid)
    assert users_repo.get_by_id(uid) is None


def test_user_unique_rfid_sqlite(sqlite_repos, seed_condos_sqlite):
    users_repo, condos_repo = sqlite_repos
    (alpha, _) = seed_condos_sqlite
    users_repo.create(User(id=None, name="A", apartment="1", condo=alpha, plate_ending="11", vehicle_type="elétrico", rfid_code="deadbeef"))
    try:
        users_repo.create(User(id=None, name="B", apartment="2", condo=alpha, plate_ending="22", vehicle_type="híbrido", rfid_code="deadbeef"))
        assert False, "Deveria falhar por UNIQUE(rfid_code)"
    except sqlite3.IntegrityError:
        pass
