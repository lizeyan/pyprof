from pyprof import profile, Profiler, clean


def test_flush():
    clean()
    from pyprof.pyprof import _root_profiler

    @profile('p1')
    def f():
        pass

    @profile('p1', flush=True)
    def g():
        pass

    with profile("p1"):
        pass
    with profile("p1"):
        pass
    assert Profiler("p1").count == 2
    with profile("p1", flush=True):
        pass
    assert Profiler("p1").count == 1
    f()
    f()
    assert Profiler("p1").count == 3
    g()
    assert Profiler("p1").count == 1
