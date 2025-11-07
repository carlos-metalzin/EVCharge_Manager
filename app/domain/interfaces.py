from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Optional
from .models import User, Condo




class IDatabase(ABC):
    @abstractmethod
    def connect(self):
        """Retorna uma conexão (sqlite3.Connection compatível)."""
        raise NotImplementedError




class IUserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> int: ...


    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]: ...


    @abstractmethod
    def get_by_name(self, name: str) -> Optional[User]: ...


    @abstractmethod
    def list_all(self) -> Iterable[User]: ...


    @abstractmethod
    def update(self, user: User) -> None: ...


    @abstractmethod
    def delete(self, user_id: int) -> None: ...


    @abstractmethod
    def count_by_condo(self, condo_name: str) -> int: ...




class ICondoRepository(ABC):
    @abstractmethod
    def create(self, condo: Condo) -> int: ...


    @abstractmethod
    def get_by_id(self, condo_id: int) -> Optional[Condo]: ...


    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Condo]: ...


    @abstractmethod
    def list_all(self) -> Iterable[Condo]: ...


    @abstractmethod
    def update(self, condo: Condo) -> None: ...


    @abstractmethod
    def delete(self, condo_id: int) -> None: ...