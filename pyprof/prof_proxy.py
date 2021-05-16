from threading import Thread

from pyprof import Profiler


def profile(name: str) -> Profiler:
    raise NotImplementedError()


def parent_thread() -> Thread:
    raise NotImplementedError()
