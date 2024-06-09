from io import BytesIO
import os
import shlex
import subprocess
from typing import List, Optional

class TestCollectionError(Exception):
    pass


class PytestRunner:
    def __init__(
        self,
        run_options: str = "",
        collect_options: str = "",
        stdout: bool = False,
    ) -> None:
        self.__run_options = shlex.split(run_options) if run_options else []
        self.__collect_options = shlex.split(collect_options) if collect_options else []
        self.__stdout = None if stdout else subprocess.DEVNULL

    def run(self, test_names: List[str]) -> bool:
        return run_pytest_with_test_names(
            test_names=test_names, args=["pytest", "--quiet"], stdout=self.__stdout
        )

    def collect_tests(self) -> List[str]:
        r, w = os.pipe()
        os.set_inheritable(w, True)
        try:
            process = subprocess.Popen(
                [
                    "pytest",
                    "--collect-only",
                    "--bisect-tests-ids-to-fd",
                    str(w),
                    *self.__run_options,
                    *self.__collect_options,
                ],
                close_fds=False,
                stdout=self.__stdout,
                stderr=subprocess.DEVNULL,
            )
            os.close(w)
            with os.fdopen(r, closefd=False) as f:
                tests = [l.strip() for l in f.readlines()]
            if process.wait() != 0:
                raise TestCollectionError("Failed to collect tests.")
            return tests
        finally:
            os.closerange(r, w)


def run_pytest_with_test_names(
    test_names: List[str], args: List[str], stdout: Optional[int]
) -> bool:
    print("Running", len(test_names), "tests.")
    r, w = os.pipe()
    os.set_inheritable(r, True)
    try:
        p = subprocess.Popen(
            [
                *args,
                "--bisect-tests-ids-from-fd",
                str(r),
            ],
            close_fds=False,
            stdout=stdout,
            stderr=subprocess.DEVNULL,
        )
        os.write(w, "\n".join(test_names).encode())
        os.close(w)
        return p.wait() == 0
    finally:
        os.closerange(r, w)
