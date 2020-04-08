# Fixtures
Test fixtures are setup functions which allows some test to run.
The vast majority of software testing require some sort of preparation to run.
`pytest` offers a nice way to build them modularly by using the `@pytest.fixture` decorator.

For the full example please check [The fixture test file](../examples/tests/test_fixture.py)

## Fixture as functions or methods

A fixture can be created with a function or a method in the test case.
To access a fixture return value you can inject it in the test arguments
```python
@pytest.fixture
def func_value_of_one():
    return 1


class TestFixtureExample:
    @pytest.fixture
    def method_value_of_two(self):
        return 2
    
    def test_basic_fixtures(self, func_value_of_one, method_value_of_two):
        assert func_value_of_one == 1
        assert method_value_of_two == 2
```

Method fixtures are available only for the class they are defined, while function fixtures are
available for all tests in the file.

```python
class TestFixtureMethodVsFunction2:
    def test_function_fixture_access(self, func_value_of_one):
        assert func_value_of_one == 1

    def test_method_fixture_access(self, method_value_of_two):
        # This test fails because it has no visibility of the `method_value_of_two` fixture
        assert method_value_of_two == 2
```

Whenever possible prefer the method-style fixtures. They make for a more organized code.
The can also access the test instance which might be useful in some rare cases.

Also because, by default fixtures are injected with the same name as the function/method they are defined,
method fixtures can avoid a silly mistake of forgetting to inject the fixture.
```python
class TestFixtureMethodVsFunction3:
    test_id = 1

    @pytest.fixture
    def name_of_test(self):
        return 'test-' + str(self.test_id)

    def test_fixture_with_test_instance_access(self, name_of_test):
        assert name_of_test == 'test-1'

    def test_forget_to_inject_function_fixture(self):
        assert func_value_of_one == 1

    def test_forget_to_inject_method_fixture(self):
        assert name_of_test == 'test-1'
```

In the above example `test_forget_to_inject_function_fixture` would fail with with
an `AssertionError`. That's because since it was not injected `func_value_of_one` points
to the function defined in the beginning of the file and is accessible. The assertion fail
becase such function is not equal to `1`.
Meanwhile `test_forget_to_inject_method_fixture` with a `NameError('name 'name_of_test' is not defined')`
exception. Since the fixture is not injected and `name_of_test` is not an available name.
The former is much easier to debug than the latter.

## Fixture dependency

A fixture can depend on other fixtures, but don't worry pytest is smart enough
to warn you about circular dependencies.

```python
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

    def test_circular_dependency(self, circular_1):
        pass
```

## Using fixture without injection
Sometimes you will need to run a fixture for all your tests or run a fixture but not
needing its value. For that you can set the `autouse` option, which will make the fixture
always run or use the `pytest.mark.usefixtures` decorator.
Be aware that for fixtures as methods with `autouse` the fixture will be auto-used in the
tests under the test case's class only. While a function fixture with `autouse` will be run
for *every* test in the file.

Also `pytest.mark.usefixtures` can be used as a decorator for one specific test or for a whole
test case class (in which the fixture will be run for all tests in the test case).

`pytest.mark.usefixtures` is preferred since it gives the opt-in to the test writer
not to the fixture writer.

Of course, if you do need the value of an automatically used feature, you can still
inject it.

```python
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
```

## Fixture scope
By default the scope of a fixture is `function` meaning it will be run for every test it is required.
But the scope can be changed for `class`, `session` or `module` which will change the
how often the fixture is run.

```python
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
```

### Changing fixture and side effects
Of course it is possible to create fixtures without `pytest`, however
it is highly recommended to use it, specially regarding scope issues when changing a fixture object.

```python
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
```
In `test_change_attribute` we change the `username` attribute of 3 fixtures.
As wee see in `test_side_effects` these changes are carried over to another test. With
the exception of `user_fixture` which is a `pytest.fixture` with `function` scope
the attribute changes were carried over to the other test.

The change in `user_fixture_class_scoped` will be carried over for any other test in the `TestFixtureSideEffects`
since it is `pytest.fixture` which is `class` scoped.

The `user` case is worst. Since it is a change directly to the object which will affect any following test
(in test case class or not).

Note also that the behavior of `test_side_effects` will change depending on whether it is ran stand alone
or with other tests.

It is worth noting that `function` scoped fixtures are not immune to side effects as can be seen below:


```python
class TestFunctionScopedFixtureSideEffects:
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
```
In `test_admin_and_common_user` `user.is_admin == True` because of how `admin_user` fixture changed it.
And since the fixture is only run once per test, by the time `test_admin_and_common_user` request both
`user` and `admin_user` fixtures, the `user` fixture is already ran because `admin_user` depends on it 
(and changes its attribute).

Regarding dependency and scope, one fixture can only depend on other fixtures which have scope equal or 
greater than itself. So a `class` scoped fixture can't depend on a `function` scoped one, for example.

```python
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

    def test_fails_due_to_wrong_feature_dependency(self, class_scoped_depending_on_function_scoped):
        assert class_scoped_depending_on_function_scoped == 'class-func'
```


## Fixture clean-up

Every fixture will run before the test it's included in. However some times it is also necessary to do a clean-up after the tests.
To achieve this, the feature should `yield` a value instead of returning it. The clean-up run time will depend on
the fixture's scope. If it is `function`, after it test where it is used, if it is `class` after it test case and
so on.

```python
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
```
