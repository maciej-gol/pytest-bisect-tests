import os
from typing import Generator, List, cast
from pluggy import Result

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--bisect-tests-ids-from-fd", default=-1, type=int)
    parser.addoption("--bisect-tests-ids-to-fd", default=-1, type=int)


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
