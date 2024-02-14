# Tests if grouping plugins work. In this case, `_group1` tests will run in one group, and `_group2` in another.
a = 0


def test_faulty_group1() -> None:
    global a
    a = 1


def test_failing_group1() -> None:
    assert a != 1


def test_faulty_group2() -> None:
    global a
    a = 2


def test_failing_group2() -> None:
    assert a != 2
