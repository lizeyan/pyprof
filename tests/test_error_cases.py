from pyprof import Profiler


def test_unmatched_toc():
    p = Profiler('p1')
    p.tic()
    p.toc()
    assert p.count == 1
    p.toc()
    assert p.count == 1
    p.tic()
    p.toc()
    assert p.count == 2
