import pytest

from examples.examples.user_repository import UserRepository, User
from examples.examples.user_service import UserService


class DummyUserRepository(UserRepository):
    def get_user(self, id: int) -> User:
        return User(id=id, username=f"dummy-user-{id}")

    @property
    def first_user(self) -> User:
        print("first user")
        return User(id=1, username="first")

    @classmethod
    def save_user(cls, user: User) -> None:
        pass


class TestGetUser:
    def test_with_dependency_injection(self):
        repository = DummyUserRepository()
        service = UserService(repository)
        assert service.get_username(user_id=123) == "dummy-user-123"

    def test_with_mock_patch_and_return_value(self, mocker):
        mocker.patch(
            "examples.examples.user_service.UserFakeDbRepository.get_user",
            autospec=True,
            return_value=User(id=1, username="testuser_patched"),
        )
        service = UserService()
        assert service.get_username(user_id=1) == "testuser_patched"

    def test_with_mock_patch_and_asserting_call(self, mocker):
        mock = mocker.patch(
            "examples.examples.user_service.UserFakeDbRepository.get_user",
            autospec=True,
            return_value=User(id=1, username="testuser_patched"),
        )
        service = UserService()
        service.get_username(user_id=1)
        mock.assert_called_once_with(service.user_repository, id=1)

    def test_with_mock_patch_and_side_effect(self, mocker):
        def get_user_side_effect(repo_instance, id):
            return User(id=id, username=f"username-{id}")

        mocker.patch(
            "examples.examples.user_service.UserFakeDbRepository.get_user",
            autospec=True,
            side_effect=get_user_side_effect,
        )
        service = UserService()
        assert service.get_username(user_id=1) == "username-1"

    def test_with_mock_patch_object_and_return_value(self, mocker):
        service = UserService()
        mocker.patch.object(
            service.user_repository,
            "get_user",
            autospec=True,
            return_value=User(id=1, username="testuser_object_patched"),
        )
        assert service.get_username(user_id=1) == "testuser_object_patched"

    def test_with_mock_patch_object_and_asserting_call(self, mocker):
        service = UserService()
        mock = mocker.patch.object(
            service.user_repository,
            "get_user",
            autospec=True,
            return_value=User(id=1, username="testuser_object_patched"),
        )
        service.get_username(user_id=1)
        # no user repository as first argument
        mock.assert_called_once_with(id=1)

    def test_with_mock_patch_object_and_side_effect(self, mocker):
        # no user repository as first argument
        def get_user_side_effect(id):
            return User(id=id, username=f"username-{id}")

        service = UserService()
        mocker.patch.object(
            service.user_repository,
            "get_user",
            autospec=True,
            side_effect=get_user_side_effect,
        )

        assert service.get_username(user_id=1) == "username-1"


class TestGetFirstUserName:
    def test_with_dependency_injection(self):
        repository = DummyUserRepository()
        service = UserService(repository)
        assert service.get_first_username() == "first"

    def test_with_mock_patch_and_return_value(self, mocker):
        mocker.patch(
            "examples.examples.user_service.UserFakeDbRepository.first_user",
            new_callable=mocker.PropertyMock,
            return_value=User(id=1, username="first_patched"),
        )
        service = UserService()
        assert service.get_first_username() == "first_patched"

    @pytest.mark.skip(msg="Don't work and runs the property")
    def test_with_mock_patch_object_does_not_work(self, mocker):
        service = UserService()

        with pytest.raises(AttributeError):
            mocker.patch.object(
                service.user_repository,
                "first_user",
                new_callable=mocker.PropertyMock,
                return_value=User(id=1, username="first_patched"),
            )

    def test_with_mock_patch_object_workaround(self, mocker):
        service = UserService()
        mocker.patch.object(
            service.user_repository,
            "get_user",
            autospec=True,
            return_value=User(id=1, username="first_object_patched"),
        )
        assert service.get_first_username() == "first_object_patched"


class TestCreateUser:
    def test_with_mock_patch_in_python_3_7_plus(self, mocker):
        mock_save = mocker.patch(
            "examples.examples.user_service.UserFakeDbRepository.save_user",
            autospec=True,
            return_value=User(id=1, username="first_patched"),
        )
        service = UserService()
        user = service.create_user("new_user")
        mock_save.assert_called_once_with(user)

    def test_with_mock_patch_in_python_3_6_minus(self, mocker):
        mock_save = mocker.patch(
            "examples.examples.user_service.UserFakeDbRepository.save_user",
            spec=UserRepository.save_user,
            return_value=User(id=1, username="first_patched"),
        )
        service = UserService()
        user = service.create_user("new_user")
        mock_save.assert_called_once_with(user)
