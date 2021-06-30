from pyprof import profile, clean, Profiler, report
import time
import numpy as np
from .test_utils import close


# noinspection PyProtectedMember
def test_profile_proxy():
    clean()
    from pyprof.pyprof import _root_profiler
    times = np.abs(np.random.normal(0.1, 0.01, 10))

    with profile("p1"):
        time.sleep(0.5)
        for t in times:
            with profile("p2"):
                time.sleep(t)

    p1 = Profiler("p1")
    p2 = Profiler("p2", p1)
    assert _root_profiler._children == {p1}
    assert p1.count == 1
    assert p2.count == len(times)
    assert close(p2.average, np.mean(times).item())
    assert close(p1.total, 0.5 + sum(times))
    print()
    print(report())


# noinspection PyProtectedMember
def test_profile_proxy_decorator():
    times = np.abs(np.random.normal(0.1, 0.01, 10))

    @profile
    def f(_):
        time.sleep(_)

    @profile("p1")
    def g():
        time.sleep(0.5)
        for t in times:
            f(t)
    clean()
    from pyprof.pyprof import _root_profiler

    g()
    p1 = Profiler("p1")
    p2 = Profiler("test_profile_proxy_decorator.<locals>.f", p1)
    assert _root_profiler._children == {p1}
    assert p1.count == 1
    assert p2.count == len(times)
    assert close(p2.average, np.mean(times).item())
    assert close(p1.total, 0.5 + sum(times))
    print()
    print(report())
