from typing import Callable, List


class NoResultFound(Exception): ...


class AlreadyFailingTest(Exception): ...


def run_bisect(
    test_names: List[str], failing_test: str, test_runner: Callable[[List[str]], bool]
) -> str:
    if not test_names:
        raise NoResultFound

    print("Checking if the test fails on its own.")
    if not test_runner([failing_test]):
        raise AlreadyFailingTest

    print("Trying to find the faulty test.")
    try:
        test_names.remove(failing_test)
    except ValueError:
        pass

    i, j = 0, len(test_names) - 1

    while i < j:
        pivot = (i + j + 1) // 2
        if test_runner([*test_names[pivot : j + 1], failing_test]):
            j = pivot - 1
        else:
            i = pivot

    if test_runner([test_names[i], failing_test]):
        raise NoResultFound

    return test_names[i]
