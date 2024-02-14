from pathlib import Path
import subprocess

import pytest

HERE = Path(__file__).parent


def test_should_detect_faulty_test() -> None:
    p = subprocess.Popen(
        [
            "pytest-bisect-tests",
            "--failing-test",
            "integration_data/faulty_test.py::test_failing",
            "--run-options",
            "faulty_test.py",
        ],
        cwd=HERE.parent / "integration_data",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        p.wait(30)
        out, err = p.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        p.kill()
        pytest.fail("process timedout")

    assert "Faulty test: integration_data/faulty_test.py::test_faulty" in out.decode()
    assert p.wait() == 0


def test_should_work_with_items_modifying_plugins() -> None:
    p = subprocess.Popen(
        [
            "pytest-bisect-tests",
            "--failing-test",
            "integration_data/test_groups_test.py::test_failing_group2",
            "--collect-options",
            "--test-group-count 2 --test-group 2",
            "--run-options",
            "test_groups_test.py",
        ],
        cwd=HERE.parent / "integration_data",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        p.wait(30)
        out, err = p.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        p.kill()
        pytest.fail("process timedout")

    assert (
        "Faulty test: integration_data/test_groups_test.py::test_faulty" in out.decode()
    )
    assert p.wait() == 0
