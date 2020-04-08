from abc import ABC, abstractmethod
from dataclasses import dataclass
import time


@dataclass
class User:
    id: int
    username: str
    is_admin: bool = False


class UserRepository(ABC):
    @abstractmethod
    def get_user(self, id: int) -> User:
        ...

    @property
    @abstractmethod
    def first_user(self) -> User:
        ...

    @classmethod
    @abstractmethod
    def save_user(cls, user: User) -> None:
        ...


class UserFakeDbRepository(UserRepository):
    def get_user(self, id: int) -> User:
        '''Simulates a db query'''
        time.sleep(10)
        return User(id=id, username=f'user-{id}')

    @property
    def first_user(self) -> User:
        return self.get_user(id=1)

    @classmethod
    def save_user(cls, user: User) -> None:
        time.sleep(1)


