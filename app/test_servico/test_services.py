from __future__ import annotations
import unittest
from app.infrastructure.mockdb import MockUserRepository, MockCondoRepository
from app.services.user_service import UserService
from app.services.condo_service import CondoService


class ServicesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.users = MockUserRepository()
        self.condos = MockCondoRepository()
        self.user_service = UserService(self.users, self.condos)
        self.condo_service = CondoService(self.condos, self.users)

    def test_user_requires_condo(self):
        with self.assertRaises(ValueError):
            self.user_service.register_user("Ana", "12B", "Inexistente", "34", "elétrico", "b3950a25")

    def test_create_and_measure(self):
        self.condo_service.register_condo("Alpha", 50, 2, "Lento", "SP", 0.75)
        uid = self.user_service.register_user("Ana", "12B", "Alpha", "34", "elétrico", "b3950a25")
        self.user_service.set_last_measure(uid, 12.5, 9.37, 45)
        msg = self.user_service.read_last_measure(uid)
        self.assertIn("12.500", msg)
        self.assertIn("R$ 9.37", msg)

    def test_delete_condo_block_when_users(self):
        self.condo_service.register_condo("Beta", 100, 3, "Rápido", "RJ", 1.0)
        uid = self.user_service.register_user("Bob", "1001", "Beta", "56", "híbrido", "0fbb65a9")
        ok, msg = self.condo_service.delete_condo(1)
        self.assertFalse(ok)
        self.assertIn("não permitida", msg)
        # agora deletar usuário e tentar novamente
        self.user_service.delete_user(uid)
        ok, msg = self.condo_service.delete_condo(1)
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
