import random
# noinspection PyProtectedMember
import time

import numpy as np
from concurrent.futures import ThreadPoolExecutor
from pyprof import clean, Profiler, report
from .test_utils import close


def test_snippet_context_manager():
    clean()
    # noinspection PyProtectedMember
    from pyprof.pyprof import _root_profiler

    assert _root_profiler.full_path == ""
    p1 = Profiler("p1")
    p2 = Profiler("p2")
    p3 = Profiler("p3", p2)
    p4 = Profiler("p4", p3)
    assert p1.average == 0
    assert p2.tail(10) == 0
    assert Profiler("p1").full_path == "/p1"
    assert p2.full_path == "/p2"
    assert Profiler("p3", p2).full_path == "/p2/p3"
    assert Profiler("p4", p3).full_path == "/p2/p3/p4"
    assert set(p1._children) == set()
    assert set(p2._children) == {p3}
    assert set(p3._children) == {p4}
    assert p4 == Profiler("p4", p3)
    assert p4 is Profiler("p4", p3)

    times = np.abs(np.random.normal(0.1, 0.01, 10))
    with p3:
        for t in times:
            _ = random.random()
            if _ <= 0.3:
                p4.tic()
                time.sleep(t)
                p4.toc()
            elif _ <= 0.5:
                with p4:
                    time.sleep(t)
            else:
                p4(lambda: time.sleep(t))()
    assert p4.count == len(times)
    assert close(p4.average, np.mean(times).item())
    assert close(p4.standard_deviation, np.std(times).item())
    assert close(p4.max_time, np.max(times).item())
    assert close(p4.tail(50), np.percentile(times, 50).item())
    assert close(p4.tail(90), np.percentile(times, 90).item())
    assert p3.total > np.sum(times)

    assert p2._max_children_full_path_length() == 9
    rpt = report()
    print()
    print(rpt)
    assert len(rpt.splitlines()) == 5 + 1
    assert str(_root_profiler) == '\n'.join(rpt.splitlines()[1:]) + '\n'


def test_multi_thread_profiler():
    clean()
    # noinspection PyProtectedMember
    from pyprof.pyprof import _root_profiler

    assert _root_profiler.full_path == ""
    p1 = Profiler("p1")
    p2 = Profiler("p2")
    p3 = Profiler("p3", p2)
    p4 = Profiler("p4", p3)
    assert p1.average == 0
    assert p2.tail(10) == 0
    assert Profiler("p1").full_path == "/p1"
    assert p2.full_path == "/p2"
    assert Profiler("p3", p2).full_path == "/p2/p3"
    assert Profiler("p4", p3).full_path == "/p2/p3/p4"
    assert set(p1._children) == set()
    assert set(p2._children) == {p3}
    assert set(p3._children) == {p4}
    assert p4 == Profiler("p4", p3)
    assert p4 is Profiler("p4", p3)

    times = np.abs(np.random.normal(0.1, 0.01, 10))
    with p3:
        with ThreadPoolExecutor(max_workers=8) as pool:
            pool.map(p4(lambda t: time.sleep(t)), times)
    assert p4.count == len(times)
    assert close(p4.average, np.mean(times).item())
    assert close(p4.standard_deviation, np.std(times).item())
    assert close(p4.max_time, np.max(times).item())
    assert close(p4.tail(50), np.percentile(times, 50).item())
    assert close(p4.tail(90), np.percentile(times, 90).item())
    assert p3.total < np.sum(times)

    assert p2._max_children_full_path_length() == 9
    rpt = report()
    print()
    print(rpt)
    assert len(rpt.splitlines()) == 5 + 1
    assert str(_root_profiler) == '\n'.join(rpt.splitlines()[1:]) + '\n'
