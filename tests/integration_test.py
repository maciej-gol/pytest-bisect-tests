from pathlib import Path
import shlex
import subprocess
from typing import Tuple
import typing

import pytest
from _pytest.fixtures import SubRequest

HERE = Path(__file__).parent


def _standalone_caller(
    failing_test: str, collect_options: str, run_options: str
) -> Tuple[str, int]:
    args = ["pytest-bisect-tests", "--failing-test", failing_test]
    if collect_options:
        args.extend(["--collect-options", collect_options])
    if run_options:
        args.extend(["--run-options", run_options])

    p = subprocess.Popen(
        args,
        cwd=HERE.parent / "integration_data",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        retcode = p.wait(30)
        out, _ = p.communicate(timeout=30)
        return out.decode(), retcode
    except subprocess.TimeoutExpired:
        p.kill()
        pytest.fail("process timedout")


def _inpytest_caller(
    failing_test: str, collect_options: str, run_options: str
) -> Tuple[str, int]:
    args = ["pytest", "--bisect-first-failure"]
    if collect_options:
        args.extend(shlex.split(collect_options))
    if run_options:
        args.extend(shlex.split(run_options))

    p = subprocess.Popen(
        args,
        cwd=HERE.parent / "integration_data",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        retcode = p.wait(30)
        out, _ = p.communicate(timeout=30)
        return out.decode(), retcode
    except subprocess.TimeoutExpired:
        p.kill()
        pytest.fail("process timedout")


class PluginCaller(typing.Protocol):
    def __call__(
        self, failing_test: str, collect_options: str, run_options: str
    ) -> Tuple[str, int]: ...


@pytest.fixture(
    params=[_standalone_caller, _inpytest_caller], ids=["standalone", "inpytest"]
)
def plugin_caller(request: SubRequest) -> PluginCaller:
    return request.param


def test_should_detect_faulty_test(plugin_caller: PluginCaller) -> None:
    out, code = plugin_caller(
        failing_test="integration_data/faulty_test.py::test_failing",
        collect_options="",
        run_options="faulty_test.py",
    )

    assert "Faulty test: integration_data/faulty_test.py::test_faulty" in out
    assert code == 0


def test_should_work_with_items_modifying_plugins(plugin_caller: PluginCaller) -> None:
    out, code = plugin_caller(
        failing_test="integration_data/test_groups_test.py::test_failing_group2",
        collect_options="--test-group-count 2 --test-group 2",
        run_options="test_groups_test.py",
    )

    assert "Faulty test: integration_data/test_groups_test.py::test_faulty" in out
    assert code == 0
