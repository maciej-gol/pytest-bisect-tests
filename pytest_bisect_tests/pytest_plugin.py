import os
import subprocess
import sys
from typing import Generator, List, Optional, Union, cast
from pluggy import Result

import pytest

from pytest_bisect_tests.bisect import NoResultFound, run_bisect
from pytest_bisect_tests.pytest_runner import run_pytest_with_test_names


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--bisect-tests-ids-from-fd", default=-1, type=int)
    parser.addoption("--bisect-tests-ids-to-fd", default=-1, type=int)
    parser.addoption("--bisect-first-failure", action="store_true")


@pytest.hookimpl(hookwrapper=True)
def pytest_collection_modifyitems(
    config: pytest.Config,
    items: List[pytest.Item],
) -> Generator[None, Result[List[None]], None]:
    result = yield

    read_fd = cast(int, config.getoption("--bisect-tests-ids-from-fd"))
    if read_fd >= 0:
        items_by_id = {item.nodeid: item for item in items}
        with os.fdopen(read_fd, mode="r") as f:
            tests = [l.strip() for l in f.readlines()]
            items[:] = [
                items_by_id[test_id] for test_id in tests if test_id in items_by_id
            ]

    write_fd = cast(int, config.getoption("--bisect-tests-ids-to-fd"))
    if write_fd >= 0:
        os.write(write_fd, "\n".join([item.nodeid for item in items]).encode())
        os.close(write_fd)


def pytest_cmdline_main(
    config: pytest.Config,
) -> Optional[Union[pytest.ExitCode, int]]:
    if config.option.bisect_first_failure:
        from _pytest.main import wrap_session

        def doit(
            config: pytest.Config, session: pytest.Session
        ) -> Union[pytest.ExitCode, int]:
            pytest_args = sys.argv[:]
            pytest_args.remove("--bisect-first-failure")

            print("Running all tests until first failure...")
            try:
                subprocess.check_call(
                    [*pytest_args, "--cache-clear", "-x"],
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                )
            except subprocess.CalledProcessError:
                pass

            failed_tests = list(config.cache.get("cache/lastfailed", default={}))
            if not failed_tests:
                print("Error: No test failed.")
                return 1

            if len(failed_tests) > 1:
                print("Error: Multiple tests failed:")
                for test in failed_tests:
                    print("-", test)
                return 1

            all_tests = list(config.cache.get("cache/nodeids", default=[]))
            print("Collected", len(all_tests), "tests.")
            print(f"Failing test: {failed_tests[0]!r}.")
            try:
                faulty_test = run_bisect(
                    test_names=all_tests,
                    failing_test=failed_tests[0],
                    test_runner=lambda names: run_pytest_with_test_names(
                        names,
                        args=pytest_args,
                        stdout=subprocess.DEVNULL,
                    ),
                )
                print("Faulty test:", faulty_test)
                return 0
            except NoResultFound:
                print("Error: No faulty test found.")
                return 1

        return wrap_session(config, doit)

    return None
