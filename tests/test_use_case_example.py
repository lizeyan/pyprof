"""
This file work as a show-case example, and it shows all public APIs and all common usages.
"""
from pyprof import profile, Profiler, report
import time
from concurrent.futures import ThreadPoolExecutor
from tests.test_utils import close


# `profile` can be used as a decorator directly.
# In such cases, the name of the Profiler is automatically extracted
@profile
def f():
    time.sleep(0.1)
    # `profile` can be used as a context manager
    with profile("sleep"):
        time.sleep(0.03)


# `profile` can be used as a decorator with a specified name
@profile('single-thread')
def h():
    for i in range(10):
        f()


@profile('multi-thread')
def g():
    with ThreadPoolExecutor() as executor:
        for i in range(10):
            executor.submit(f)


def test_main():
    h()
    assert Profiler.get("/single-thread").count == 1
    assert close(Profiler.get("/single-thread").total, 10 * 0.13)
    # Profiler automatically find parent Profiler
    assert Profiler.get("/single-thread/f").count == 10
    assert close(Profiler.get("/single-thread/f").total, 10 * 0.13)
    assert close(Profiler.get("/single-thread/f").average, 0.13)
    assert close(Profiler.get("/single-thread/f").standard_deviation, 0.)
    assert close(Profiler.get("/single-thread/f/sleep").total, 10 * 0.03)
    assert close(Profiler.get("/single-thread/f/sleep").average, 0.03)
    assert close(Profiler.get("/single-thread/f/sleep").standard_deviation, 0.)

    g()
    assert Profiler.get("/multi-thread").count == 1
    # Profiler cannot automatically find parent Profiler in other threads
    assert Profiler.get("/f").count == 10
    assert close(Profiler.get("/f").total, 10 * 0.13)
    assert close(Profiler.get("/f").average, 0.13)
    assert close(Profiler.get("/f").standard_deviation, 0.)
    assert close(Profiler.get("/f/sleep").total, 10 * 0.03)
    assert close(Profiler.get("/f/sleep").average, 0.03)
    assert close(Profiler.get("/f/sleep").standard_deviation, 0.)

    # print a formatted time usage report
    print(report())
    # filter components
    print(report(min_total_percent=0.1, min_parent_percent=0.5))

    # `profile` automatically print report if `report_printer` is given
    with profile('auto-print', report_printer=print):
        f()
    with profile('auto-print', report_printer=print):
        f()
    assert Profiler.get("/auto-print").count == 2

    # use `flush=True` to reset a Profiler and all its children
    with profile('auto-print', report_printer=print, flush=True):
        f()
    assert Profiler.get("/auto-print").count == 1


if __name__ == '__main__':
    test_main()
