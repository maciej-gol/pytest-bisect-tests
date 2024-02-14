a = 1

def test_faulty() -> None:
    global a
    a = 2

def test_failing() -> None:
    assert a == 1
