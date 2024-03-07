# pytest-bisect-tests

Sometimes one test can affect the execution of another test. This simple script tries to find the offender.

This script can be called as standalone script, or via pytest option.

Example:

```python
# faulty_test.py
a = 1

def test_faulty() -> None:
    global a
    a = 2

def test_failing() -> None:
    assert a == 1


$ pytest-bisect-tests --failing-test "faulty_test.py::test_failing"
Checking if the test fails on its own.
Running 1 tests.
Trying to find the faulty test.
Running 2 tests.
Faulty test: faulty_test.py::test_faulty
```

## Comparison of UX

Standalone script:
[![asciicast](https://asciinema.org/a/wLxhvndvw912zjRYBM2mr3uTG.svg)](https://asciinema.org/a/wLxhvndvw912zjRYBM2mr3uTG)

pytest option:
[![asciicast](https://asciinema.org/a/EudozjTNeML0X18uhgbHO6hda.svg)](https://asciinema.org/a/EudozjTNeML0X18uhgbHO6hda)
## Installation


```shell
$ pip install pytest-bisect-tests
```

## Usage

### Standalone script
```shell
$ pytest-bisect-tests --failing-test "<identifier of the test as pytest shows them with -v>"
```

Additional arguments:

```shell
$ pytest-bisect-tests --help
usage: pytest-bisect-tests [-h] --failing-test FAILING_TEST [--run-options RUN_OPTIONS] [--collect-options COLLECT_OPTIONS] [--stdout]

options:
  -h, --help            show this help message and exit
  --failing-test FAILING_TEST
                        REQUIRED. The identifier of the test, as shown by pytest -v.
  --run-options RUN_OPTIONS
                        Arguments that will be passed directly to pytest. A single string.
  --collect-options COLLECT_OPTIONS
                        Arguments that will be passed to pytest during tests collection. A single string.
                        This is useful when, for example, you have a test grouping plugin that affects the tests run.
  --stdout              If passed, pytest output will be shown.
```

### As pytest option

This approach automatically discovers all tests in the suite and failing test, so it has minimal input options.

```shell
$ pytest --bisect-first-failure
```

## Alternatives
[detect-test-pollution](https://github.com/asottile/detect-test-pollution), an alternative package with similar functionality.
Lacks passing pytest run and collect options or showing the output from pytest. It also doesn't support pytest plugins that alter
how tests are collected (like [pytest-test-groups](https://github.com/mark-adams/pytest-test-groups)).
