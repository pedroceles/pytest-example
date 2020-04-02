# TODO: DISCLAIMER SCOPE CHANGE
# TODO: xFail
from dataclasses import dataclass
import uuid

import pytest


@pytest.fixture
def func_value_of_one():
    return 1


class TestFixtureMethodVsFunction:
    @pytest.fixture
    def method_value_of_two(self):
        return 2

    def test_basic_fixtures(self, func_value_of_one, method_value_of_two):
        assert func_value_of_one == 1
        assert method_value_of_two == 2


class TestFixtureMethodVsFunction2:
    def test_function_fixture_access(self, func_value_of_one):
        assert func_value_of_one == 1

    @pytest.mark.xfail(reason='Fixture not available')  # This tells pytest to expect this test to fail
    def test_method_fixture_access(self, method_value_of_two):
        # This test fails because it has no visibility of the `method_value_of_two` fixture
        assert method_value_of_two == 2


class TestFixtureMethodVsFunction3:
    test_id = 1

    @pytest.fixture
    def name_of_test(self):
        return 'test-' + str(self.test_id)

    def test_fixture_with_test_instance_access(self, name_of_test):
        assert name_of_test == 'test-1'

    @pytest.mark.xfail(reason='Fixture not injected, but fixture function name is. Will raise AssertionError')
    def test_forget_to_inject_function_fixture(self):
        assert func_value_of_one == 1

    @pytest.mark.xfail(reason='Fixture not injected, fixture is method. Will raise NameError')
    def test_forget_to_inject_method_fixture(self):
        assert name_of_test == 'test-1'


class TestFixtureDependency:
    @pytest.fixture
    def value_of_one(self):
        return 1

    @pytest.fixture
    def value_of_plus_one(self, value_of_one):
        return value_of_one + 1

    @pytest.fixture
    def circular_1(self, circular_2):
        return False

    @pytest.fixture
    def circular_2(self, circular_1):
        return False

    def test_fixture_dependency(self, value_of_plus_one):
        assert value_of_plus_one == 2

    @pytest.mark.xfail(reason='Fixture has circular dependency')
    def test_circular_dependency(self, circular_1):
        pass


class TestFixtureUsageWithoutInjection:
    auto_used = False
    selectively_used = False

    @pytest.fixture(autouse=True)
    def always_used_fixture(self):
        print('I`m always used')
        self.auto_used = True
        return 'always'

    @pytest.fixture
    def selectively_used_fixture(self):
        print('I`m selectively used')
        self.selectively_used = True
        return 'maybe'

    def test_autoused_fixture(self):
        assert self.auto_used is True
        assert self.selectively_used is False

    @pytest.mark.usefixtures('selectively_used_fixture')
    def test_selectively_used_fixture(self):
        assert self.auto_used is True
        assert self.selectively_used is True

    def test_fixtures_values(self, always_used_fixture, selectively_used_fixture):
        assert self.auto_used is True
        assert self.selectively_used is True
        assert always_used_fixture == 'always'
        assert selectively_used_fixture == 'maybe'


class TestFixtureScope:
    function_scoped_fixture_calls = 0
    class_scoped_fixture_calls = 0

    @pytest.fixture(autouse=True)
    def function_scoped(self):
        self.__class__.function_scoped_fixture_calls += 1

    @pytest.fixture(scope='class', autouse=True)
    def class_scoped(self):
        self.__class__.class_scoped_fixture_calls += 1

    def test_first(self):
        assert self.function_scoped_fixture_calls == 1
        assert self.class_scoped_fixture_calls == 1

    def test_second(self):
        assert self.function_scoped_fixture_calls == 2
        assert self.class_scoped_fixture_calls == 1


@dataclass
class User:
    id: int
    username: str
    is_admin: bool = False


user = User(id=1, username='user')


class TestFixtureSideEffects:
    @pytest.fixture
    def user_fixture(self):
        return User(id=1, username='user')

    @pytest.fixture(scope='class')
    def user_fixture_class_scoped(self):
        return User(id=1, username='user')

    def test_change_attribute(self, user_fixture, user_fixture_class_scoped):
        user.username = 'otheruser'
        user_fixture.username = 'otheruser'
        user_fixture_class_scoped.username = 'otheruser'

    def test_side_effects(self, user_fixture, user_fixture_class_scoped):
        assert user.username == 'otheruser'
        assert user_fixture.username == 'user'
        assert user_fixture_class_scoped.username == 'otheruser'


class TestFunctionScopedSideEffect:
    @pytest.fixture
    def user(self):
        return User(id=1, username='user')

    @pytest.fixture
    def admin_user(self, user):
        user.is_admin = True
        return user

    def test_common_user(self, user):
        assert not user.is_admin

    def test_admin_and_common_user(self, user, admin_user):
        assert user.is_admin
        assert admin_user.is_admin


class TestScopeDependency:
    @pytest.fixture
    def function_scoped(self):
        return 'func'

    @pytest.fixture(scope='class')
    def class_scoped(self):
        return 'class'

    @pytest.fixture
    def function_scoped_depending_on_class_scoped(self, class_scoped):
        return 'func-' + class_scoped

    @pytest.fixture(scope='class')
    def class_scoped_depending_on_function_scoped(self, function_scoped):
        return 'class-' + function_scoped

    def test_passes_due_to_ok_dependency(self, function_scoped_depending_on_class_scoped):
        assert function_scoped_depending_on_class_scoped == 'func-class'

    @pytest.mark.xfail(reason='Fails because of wrong feature dependency')
    def test_fails_due_to_wrong_feature_dependency(self, class_scoped_depending_on_function_scoped):
        assert class_scoped_depending_on_function_scoped == 'class-func'

class TestFixtureCleanup:
    @pytest.fixture
    def fixture_with_cleanup(self):
        print('running fixture before test')
        yield 'fixture'
        print('cleaning up after test')

    def test_feature_with_cleanup(self, fixture_with_cleanup):
        # Check printed messages while running this test
        print('running test')
        assert fixture_with_cleanup == 'fixture'
