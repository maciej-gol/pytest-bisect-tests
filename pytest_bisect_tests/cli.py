import argparse
import sys
from pytest_bisect_tests.bisect import run_bisect

from pytest_bisect_tests.pytest_runner import (
    PytestRunner,
    TestCollectionError,
)


def main() -> None:
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--failing-test",
        required=True,
        help="REQUIRED. The identifier of the test, as shown by pytest -v.",
    )
    parser.add_argument(
        "--run-options",
        help="Arguments that will be passed directly to pytest. A single string.",
    )
    parser.add_argument(
        "--collect-options",
        help=(
            "Arguments that will be passed to pytest during tests collection. A single string.\n"
            "This is useful when, for example, you have a test grouping plugin that affects the tests run."
        ),
    )
    parser.add_argument(
        "--stdout", action="store_true", help="If passed, pytest output will be shown."
    )
    args = parser.parse_args()

    pytest_runner = PytestRunner(
        run_options=args.run_options,
        collect_options=args.collect_options,
        stdout=args.stdout,
    )
    try:
        test_names = pytest_runner.collect_tests()
    except TestCollectionError:
        if not args.stdout:
            print("Failed to collect tests. Use --stdout to see the output from pytest test collection.")
        else:
            print("Failed to collect tests. Consult output from pytest.")
        sys.exit(1)

    result = run_bisect(
        test_names=test_names,
        failing_test=args.failing_test,
        test_runner=pytest_runner.run,
    )
    print("Faulty test:", result)


if __name__ == "__main__":
    main()
