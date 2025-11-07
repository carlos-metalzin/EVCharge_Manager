from __future__ import annotations
from typing import Dict, Iterable, Optional
from ..domain.interfaces import IUserRepository, ICondoRepository, IDatabase
from ..domain.models import User, Condo

class InMemoryDatabase(IDatabase):
    # Apenas para cumprir a interface; não expõe conexão real
    def connect(self): # type: ignore[override]
        raise RuntimeError("InMemoryDatabase não fornece conexão SQL.")

class MockUserRepository(IUserRepository):
    def __init__(self) -> None:
        self._data: Dict[int, User] = {}
        self._seq = 1


    def create(self, user: User) -> int:
        uid = self._seq
        self._seq += 1
        self._data[uid] = User(id=uid, **{k: v for k, v in user.__dict__.items() if k != "id"})
        return uid


    def get_by_id(self, user_id: int) -> Optional[User]:
        return self._data.get(user_id)


    def get_by_name(self, name: str) -> Optional[User]:
        for u in self._data.values():
            if u.name == name:
                return u
        return None


    def list_all(self) -> Iterable[User]:
        return list(self._data.values())


    def update(self, user: User) -> None:
        assert user.id is not None
        if user.id in self._data:
            self._data[user.id] = user


    def delete(self, user_id: int) -> None:
        self._data.pop(user_id, None)


    def count_by_condo(self, condo_name: str) -> int:
        return sum(1 for u in self._data.values() if u.condo == condo_name)

class MockCondoRepository(ICondoRepository):
    def __init__(self) -> None:
        self._data: Dict[int, Condo] = {}
        self._seq = 1


    def create(self, condo: Condo) -> int:
        cid = self._seq
        self._seq += 1
        self._data[cid] = Condo(id=cid, **{k: v for k, v in condo.__dict__.items() if k != "id"})
        return cid


    def get_by_id(self, condo_id: int) -> Optional[Condo]:
        return self._data.get(condo_id)


    def get_by_name(self, name: str) -> Optional[Condo]:
        for c in self._data.values():
            if c.name == name:
                return c
        return None


    def list_all(self) -> Iterable[Condo]:
        return list(self._data.values())


    def update(self, condo: Condo) -> None:
        assert condo.id is not None
        if condo.id in self._data:
            self._data[condo.id] = condo


    def delete(self, condo_id: int) -> None:
        self._data.pop(condo_id, None)