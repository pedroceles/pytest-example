from dataclasses import dataclass

import pytest
from examples.examples.user_service import UserService
from unittest.mock import MagicMock, create_autospec


class TestMagicMockReturnValue:
    def test_return_value(self, mocker):
        mock = mocker.MagicMock(return_value=2)
        assert mock() == 2


class TestMagicMockAttribute:
    def test_attribute(self, mocker):
        mock = mocker.MagicMock(my_attribute=123)
        assert mock.my_attribute == 123


class TestMagicMockSideEffect:
    def test_different_return_value_with_side_effect(self, mocker):
        mock = mocker.MagicMock(side_effect=[1, 2, 3])
        assert mock() == 1  # First Call
        assert mock() == 2  # Second Call
        assert mock() == 3  # Third Call

    def test_raising_exception_with_side_effect(self, mocker):
        mock = mocker.MagicMock(side_effect=ValueError('mocked value error'))
        with pytest.raises(ValueError):
            assert mock()

    def test_mock_implementation_with_side_effect(self, mocker):
        def double(number: int) -> int:
            return number * 2

        mock = mocker.MagicMock(side_effect=double)
        assert mock(3) == 6


class TestMagicMockAutoMocks:
    def test_mock_returns_new_mock_by_default(self, mocker):
        mock = mocker.MagicMock()
        returned_mock = mock()
        assert isinstance(returned_mock, MagicMock)
        assert mock != returned_mock

    def test_mock_auto_generates_other_mocks(self, mocker):
        mock = mocker.MagicMock()
        other_mock = mock.some_attribute
        yet_another_mock = mock.some_other_attribute
        assert isinstance(other_mock, MagicMock)
        assert isinstance(yet_another_mock, MagicMock)
        assert other_mock != yet_another_mock != mock


class TestMagicMockSpec:
    def test_mock_without_spec(self, mocker):
        mock = mocker.MagicMock()
        mock(1, 2, 3, 4, can_be_called_with_any_args=True)
        mock.can_access_any_attribute

    def test_mock_with_function_spec(self, mocker):
        def double(number: int) -> int:
            return number * 2

        mock = create_autospec(double)
        with pytest.raises(TypeError, match="too many positional arguments"):
            mock(1, 2, 3, 4, can_be_called_with_any_args=True)
        with pytest.raises(AttributeError, match="'function' object has no attribute 'can_access_any_attribute'"):
            mock.can_access_any_attribute

    def test_mock_with_class_spec(self, mocker):
        @dataclass
        class User:
            id: int
            name: str
        mock_class = create_autospec(User)
        with pytest.raises(TypeError, match="too many positional arguments"):
            mock_class(1, 2, 3, 4, can_be_called_with_any_args=True)
        with pytest.raises(AttributeError, match="Mock object has no attribute 'can_access_any_attribute'"):
            mock_class.can_access_any_attribute
        user_mock = mock_class(id=1, name='username')
        assert isinstance(user_mock, User)

    def test_mock_with_class_instance_spec(self, mocker):
        @dataclass
        class User:
            id: int
            name: str
        user_instance = User(id=1, name='test')
        mock_instance = create_autospec(user_instance)
        with pytest.raises(TypeError, match="'NonCallableMagicMock' object is not callable"):
            mock_instance(1, 2, 3, 4, can_be_called_with_any_args=True)
        with pytest.raises(AttributeError, match="Mock object has no attribute 'can_access_any_attribute'"):
            mock_instance.can_access_any_attribute
        with pytest.raises(TypeError, match="'NonCallableMagicMock' object is not callable"):
            mock_instance(id=1, name='username')
        assert isinstance(mock_instance.id, int)
        assert mock_instance.id != 1  # it is mock with int spec. But not the same value.

        assert isinstance(mock_instance.name, str)
        assert mock_instance.name != 'test'  # it is a mock with str spec. But not the same value.
