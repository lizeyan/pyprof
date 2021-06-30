from pyprof import profile, Profiler, clean


# noinspection PyProtectedMember
def test_flush():
    clean()

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
