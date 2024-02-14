from typing import List
import pytest

from pytest_bisect_tests.bisect import AlreadyFailingTest, NoResultFound, run_bisect


@pytest.mark.parametrize(
    "test_names",
    [
        ["faulty"],
        ["x", "faulty"],
        ["faulty", "x"],
        ["faulty", "x", "x"],
        ["x", "faulty", "x"],
        ["x", "x", "faulty"],
    ],
)
def test_should_find_faulty_test(test_names: List[str]) -> None:
    assert run_bisect(
        test_names,
        failing_test="whatever",
        test_runner=lambda suite: "faulty" not in suite,
    )


@pytest.mark.parametrize(
    "test_names",
    [
        [],
        ["x"],
        ["x", "x"],
        ["x", "x", "x"],
    ],
)
def test_should_raise_no_result_found_exception_when_no_faulty_test_found(
    test_names: List[str],
) -> None:
    with pytest.raises(NoResultFound):
        run_bisect(
            test_names,
            failing_test="whatever",
            test_runner=lambda suite: "faulty" not in suite,
        )


def test_should_raise_already_failing_test_exception_when_failing_test_doesnt_work_in_isolation() -> (
    None
):
    with pytest.raises(AlreadyFailingTest):
        run_bisect(["a", "b"], failing_test="whatever", test_runner=lambda _: False)
