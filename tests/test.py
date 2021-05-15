from pyprof import profile, clean
# noinspection PyProtectedMember
from pyprof.pyprof import _root_profiler
import time
from .test_utils import close


def test_snippet_context_manager():
    clean()
    with profile("p1") as p1:
        time.sleep(0.01)
    with profile("p2") as p2:
        time.sleep(0.01)
        with profile("p3") as p3:
            time.sleep(0.02)
    assert close(p1.total(), 0.01)
    assert close(p2.total(), 0.03)
    assert close(p3.total(), 0.02)
    assert p3.name == "p3"
    assert p3.full_path == "/p2/p3"
    assert p1.name == "p1"
    assert p1.full_path == "p1"
    assert p2.full_path == "p2"
    assert p1.count


def test_function():
    clean()

    @profile("p3")
    def p3():
        time.sleep(0.03)

    @profile("p1")
    def f1():
        @profile("p2")
        def f2():
            time.sleep(0.02)
        time.sleep(0.01)
        f2()
