# pytest

[pytest](https://docs.pytest.org/en/latest/) is testing framework for the python language.
Python already comes with a set of tools for testing in the [unittest](https://docs.python.org/3/library/unittest.html) module.
However pytest adds some functionality that greatly enhance the test experience making it fun:
- You can use standard `assert` in your test (drop `self.assertEqual` and siblings.)
- You can have stand-alone test cases class (no need to inherit from `TestCase`) or tests as functions
- It is plugable and customizable. There are tons of plugins for added functionality out there. One of the
most famous is [pytest-mock](https://github.com/pytest-dev/pytest-mock)
- It allows for easy development and management of [fixtures](https://docs.pytest.org/en/latest/fixture.html).
