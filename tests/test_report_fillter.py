import time

from pyprof import profile, Profiler, report, clean


def test_report_filter():
    clean()

    @profile
    def f():
        time.sleep(1e-3)

    @profile
    def g():
        time.sleep(1e-2)

    with profile("p") as p:
        f()
        g()
    assert len(p.report().splitlines()) == 3
    assert len(p.report(min_total_percent=0.5).splitlines()) == 2
    assert len(p.report(min_total_percent=1.0).splitlines()) == 1
