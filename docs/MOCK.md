# Mocks
Mocks are a powerful tool for testing. Mocks allow you to fake certain code
dependencies and focus your test attention to what matters. It also minimizes test
setup boilerplate.

As always there are multiple ways to create mocks. Python standard library comes
with the [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) package.
and we will be extensively using the [pytest-mock](https://github.com/pytest-dev/pytest-mock)
plugin. It is a thin wrapper around `unittest.mock` adding some great functionality
and exposing the `mocker` fixture.

This page provides code snippets, but the full test can be checked in 
[test_mock_example.py](../examples/tests/test_mock_example.py)
and [test_user_service.py](../examples/tests/test_user_service.py).

## The powerful MagicMock
The `unittest.mock` has several classes to help with mocking. The most popular one is `MagicMock`
that can be accessed through the `mocker` fixture as well. One of the most common actions when mocking
is to fake a return value:


# TODO: update snippets
```python
class TestMagicMockReturnValue:
    def test_return_value(self, mocker):
        mock = mocker.MagicMock(return_value=2)
        assert mock() == 2

```

When creating a mock, you can also set attributes:

```python
class TestMagicMockAttribute:
    def test_attribute(self, mocker):
        mock = mocker.MagicMock(my_attribute=123)
        assert mock.my_attribute == 123
```

With `side_effect` we can have more control over the calling result
```python
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
```

By default a MagicMock will return another MagicMock. As well as any attribute that you access will return another MagicMock

```python
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
```

As we will see later on, this is usually too much power an can lead to a false sense of security in your tests.
That's why it is possible to create a mock with specification. Check [Autospeccing](https://docs.python.org/3/library/unittest.mock.html#auto-speccing)
for more info.

```python
from unittest.mock import create_autospec
from dataclasses import dataclass


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
```

## Applying mocks in real code

### Test subject
Now we will apply mocking to testing our code. Our test subject will be the [user_service](../examples/examples/user_service.py) which 
uses the [user_repository](../examples/examples/user_repository.py).

Here it is a snipped of them
```python
# user_repository.py
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
        time.sleep(10)

# user_service.py (test subject)
from typing import Optional

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
```

### Mock regular method

The `UserFakeDbRepository.get_user` is deliberately slow to fake a call that should not be done in a unit test.
`UserService` uses a naive [Dependency Injection](https://martinfowler.com/articles/injection.html).
 Although naive, it already makes our code more testable.


Our first test subject will be `UserService.get_username`. This method uses their repository to get the user object
and returns its `username` attribute. We will need ot mock the `get_user` function of the repository and will dive into
three different strategies.

#### Leveraging dependency injection
The first strategy is the most elegant one and requires no external tools (like the mock library). We can leverage
the fact that `UserService` uses the `UserRepository` through dependency injection and create a dummy
implementation of and passing to the testing instance.

```python
from examples.examples.user_repository import UserRepository, User


class DummyUserRepository(UserRepository):
    def get_user(self, id: int) -> User:
        return User(id=id, username=f'dummy-user-{id}')
    # ...
```

Now we can test easily:

```python
class TestGetUser:
    def test_with_dependency_injection(self):
        repository = DummyUserRepository()
        service = UserService(repository)
        assert service.get_username(id=123) == 'dummy-user-123'
```

This strategy has several advantages.
* It does not depend on any external tool, just on the code api itself.
* It works because the code uses dependency injection. Good code promotes good tess and vice versa.
* It is usually quite simple to implement.
* Makes testing code simple to read.

However, given python's dynamic nature, this strategy has a major pitfall. If the `UserRepository.get_user` API
change in any way, we could have a falsy passing test. For example if `get_user` signatures changes to this:

```
class UserRepository(ABC):
    @abstractmethod
    def get_user(self, user_id: int) -> User:  # from id to user_id
        ...
```
The code for `get_username` is no longer correct since it calls the repository explicitly passing the id kwarg
```python
class UserService:
    # ...
    def get_username(self, user_id: int) -> str:
        return self.user_repository.get_user(id=user_id).username
```

However, our test would not break because `DummyUserRepository.get_user` is still with the old API.
So we end up testing old behavior with old interface.

If your codebase is type checked with a tool like [mypy](http://mypy-lang.org/) you are in good hands.
Since the wrong api call would be caught at type checking.

If possible prefer this method (meaning the API change is being safe guarded by other tests, like type checking),
prefer this strategy because of its advantages.

#### using mock.patch

Another way is to replace the user repository with a `MagicMock`. `unittest.mock` provides the `patch` method
which helps with that. `pytest-mock` provides an even better wrapper through the `mocker` fixture.

```python
class TestGetUser:
    # ...
    def test_with_mock_patch_and_return_value(self, mocker):
        mocker.patch(
            'examples.examples.user_service.UserFakeDbRepository.get_user',
            autospec=True,
            return_value=User(id=1, username='testuser')
        )
        service = UserService()
        assert service.get_username(user_id=1) == 'testuser'
```

`patch` will receive a target and, during the test, will replace the target with a `MagicMock`. In this test
we are leveraging the fact the the default `UserReporsitory` for the `UserService` is `UserFakeDbRepository`.

It is worth noting that although `UserFakeDbRepository` is implemented in the `examples.examples.user_repository`
module, while mocking we should always patch the object where it is looked up in the test subject not where the mocked
object is implemented.

`autospec=True` tells `patch` to create a `MagicMock` respecting the specification of the mocked object (similar
to using `create_autospec` using the object to be mocked). We can also pass `MagicMock` configuration arguments, like
`return_value`.

Although we did assert the result here, we did not test the the `user_id` in `get_username` is correctly passed to
the `id` argument of the repository's `get_user`. We can do that asserting a call, `MagicMock` provides a lot of 
helper methods for that.

```python
class TestGetUser:
    # ...
    def test_with_mock_patch_and_asserting_call(self, mocker):
        mock = mocker.patch(
            'examples.examples.user_service.UserFakeDbRepository.get_user',
            autospec=True,
            return_value=User(id=1, username='testuser_patched')
        )
        service = UserService()
        service.get_username(user_id=1)
        mock.assert_called_once_with(service.user_repository, id=1)
```
Here we are asserting how the mocked function was called. `mocker.patch` returns that `MagicMock` it created to patch
the target. This is what our code will use in the test. We assert that the mock was called in a specific way.

Here the importance of the autospeccing is highlighted. It is not uncommon for the `assert_called_once_with` to be 
mispelled (like `assetr_called_once_with`). If the mock did not have an specification we would have created a 
`MagicMock` that was too permissive, meaning any attribute you access on it will generate another mock. So you
would actually be calling the mock automatically created by accessing `assetr_called_once_with`, rather then asserting
anything. Your test would also pass silently.
Because we have spec, the mock object will follow the spec and will mimic the API of the specification plus the mock
helper methods API. Because `assetr_called_once_with` is not neither in the spec nor in the mock API that test fails.

Therefore:
* Always mock with specification
* Always make your test fail for the first time to see they are running properly

  We could have started the test with `mock.assert_called_once_with(service.user_repository, id=2)` (wrong id)
  and make sure the test fails. If we forgot the spec and also mispelled the method the test would wrongly pass.
  
You will notice that we pass the repository instance as the first argument of `assert_called_once_with` that's
because we are mocking the [unbound](https://www.geeksforgeeks.org/bound-unbound-and-static-methods-in-python/)
method `get_user` of the class `UserFakeDbRepository`. Because it is unbound the mock will register as argument
the instance of the repository passed to `self` of `get_user`.

If for some reason you don't have access to the instance, you can use `mocker.ANY` which will compare truthly with
anything. `mock.assert_called_once_with(mocker.ANY, id=1)`.

##### using side effects
Notice that we did not have this previous test when we used `DummyUserRepository`. That's because it was indirectly
being tested through `DummyUserRepository.get_user` implementations, that appended the id in the `username`.
In the previous example we could not do that because we had a static `return_value`. We can change that with `side_effect`:

```python
    def test_with_mock_patch_and_side_effect(self, mocker):
        def get_user_side_effect(repo_instance, id):
            return User(id=id, username=f'username-{id}')

        mocker.patch(
            'examples.examples.user_service.UserFakeDbRepository.get_user',
            autospec=True,
            side_effect=get_user_side_effect
        )
        service = UserService()
        assert service.get_username(user_id=1) == 'username-1'
```

Here we use `side_effect` to provide an implementation of the mocked target.

#### using mock.patch.object
A sibling approach is to mock just one object.
```python
class TestGetUser:
    # ...
    def test_with_mock_patch_object_and_return_value(self, mocker):
        service = UserService()
        mocker.patch.object(
            service.user_repository,
            'get_user',
            autospec=True,
            return_value=User(id=1, username='testuser_object_patched')
        )
        assert service.get_username(user_id=1) == 'testuser_object_patched'
```
Here we are just mocking the `get_user` of our `service.user_repository` instance. If we instantiated another service
with another repository instance it would not be mocked. A side effect of that is that now we are mocking the
[bound](https://www.geeksforgeeks.org/bound-unbound-and-static-methods-in-python/) `get_user` of the `user_repository`
instance. Therefore there are some changes with asserting calls and side effects that won't have access to the instance
of the repository.

```python
class TestGetUser:
    # ...
    def test_with_mock_patch_object_and_asserting_call(self, mocker):
        service = UserService()
        mock = mocker.patch.object(
            service.user_repository,
            'get_user',
            autospec=True,
            return_value=User(id=1, username='testuser_object_patched')
        )
        service.get_username(user_id=1)
        # no user repository as first argument
        mock.assert_called_once_with(id=1)

    def test_with_mock_patch_object_and_side_effect(self, mocker):
        # no user repository as first argument
        def get_user_side_effect(id):
            return User(id=id, username=f'username-{id}')
        service = UserService()
        mocker.patch.object(
            service.user_repository,
            'get_user',
            autospec=True,
            side_effect = get_user_side_effect
        )

        assert service.get_username(user_id=1) == 'username-1'
```


### mocking other kinds of methods
Mocking strategy might change given different types of methods.
For this example, let's test the `UserService.get_first_username`. It uses
the `UserRepository.first_user` `property`.

#### Leveraging dependency injection
Nothing changes too much in this case. We just need to implement the property.

```python
from examples.examples.user_repository import UserRepository, User


class DummyUserRepository(UserRepository):
    @property
    def first_user(self) -> User:
        return User(id=1, username='first')
    # ...

class TestGetFirstUserName:
    def test_with_dependency_injection(self):
        repository = DummyUserRepository()
        service = UserService(repository)
        assert service.get_first_username() == 'first'
```

#### using mock.patch
When using `patch` we will need to change the config a little bit.
We want our mock to behave like a property, not like a callable. Therefore we will use the `PropertyMock` instead
of `MagicMock`. To do that we use the `new_callable` option and drop the `autospec`.

```python
class TestGetFirstUserName:
    # ...
    def test_with_mock_patch_and_return_value(self, mocker):
        mocker.patch(
            'examples.examples.user_service.UserFakeDbRepository.first_user',
            new_callable=mocker.PropertyMock,
            return_value=User(id=1, username='first_patched')
        )
        service = UserService()
        assert service.get_first_username() == 'first_patched'
```

#### using mock.patch.object
This is not possible and will fail with an `AttributeError`, since behind the scenes
It tries to set the attribute representing the property and in this case there is not set
option for the property.

Not only that, but because mocks must be "resetable", while mocking it will retrieve the original
value of the mocking target. Because this is a property the property's method is triggered. This is another
problem if the property depends on external services like a database connection or external API.

Therefore the best approach is to use `mock.patch`. In this case however, because the property is simple,
and is just a proxy to the `UserRepository.get_user` we can indirectly mock the `get_user` method and get
the desired result as side effect.
```python
class TestGetFirstUserName:
    # ...
    def test_with_mock_patch_object_workaround(self, mocker):
        service = UserService()
        mocker.patch.object(
            service.user_repository,
            'get_user',
            autospec=True,
            return_value=User(id=1, username='first_object_patched')
        )
        assert service.get_first_username() == 'first_object_patched'
```

### staticmethod and classmethod
Mocking `staticmethod` and `classmethod` will be the same as mocking a regular method as described here.
The caveat is that because of a [bug](https://bugs.python.org/issue23078) that was resolved in python 3.7 you will need to pass the spec manually
instead of using autospec. Only if you are in python 3.6 or lower.
Let's check that by testing the `UserService.create_user` which uses the `UserRepository.save_user` `classmethod`:

```python
class TestCreateUser:
    def test_with_mock_patch_in_python_3_7_plus(self, mocker):
        mock_save = mocker.patch(
            'examples.examples.user_service.UserFakeDbRepository.save_user',
            autospec=True,
            return_value=User(id=1, username='first_patched')
        )
        service = UserService()
        user = service.create_user('new_user')
        mock_save.assert_called_once_with(user)

    def test_with_mock_patch_in_python_3_6_minus(self, mocker):
        mock_save = mocker.patch(
            'examples.examples.user_service.UserFakeDbRepository.save_user',
            spec=UserRepository.save_user,
            return_value=User(id=1, username='first_patched')
        )
        service = UserService()
        user = service.create_user('new_user')
        mock_save.assert_called_once_with(user)
```
