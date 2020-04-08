from typing import Optional

from examples.examples.user_repository import UserFakeDbRepository, UserRepository, User


class UserService:
    def __init__(self, user_repository: Optional[UserRepository] = None):
        if user_repository is None:
            user_repository = UserFakeDbRepository()
        self.user_repository = user_repository

    def get_username(self, user_id: int) -> str:
        return self.user_repository.get_user(id=user_id).username

    def get_first_username(self) -> str:
        return self.user_repository.first_user.username

    def create_user(self, username: str) -> User:
        user = User(id=None, username=username)
        self.user_repository.save_user(user)
        return user
