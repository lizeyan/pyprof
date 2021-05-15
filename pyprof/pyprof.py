from typing import Callable, overload


class Profiler:
    _instances = {}

    def __init__(self, name: str = "", parent: "Profiler" = None):
        self._name = name
        self._parent = parent
        self._full_path = f"{self._parent.full_path if self._parent is not None else ''}/{self.name}"
        self._children = []

        if parent is not None:
            self._parent._children.append(self)

    def __new__(cls, name: str = "", parent: "Profiler" = None):
        raise NotImplementedError()

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()

    def __call__(self, func: Callable) -> Callable:
        pass

    def tic(self):
        raise NotImplementedError()

    def toc(self):
        raise NotImplementedError()

    @property
    def name(self):
        return self._name

    @property
    def full_path(self):
        return self._full_path

    def type(self) -> str:
        raise NotImplementedError()

    def count(self) -> int:
        raise NotImplementedError()

    def total(self) -> float:
        raise NotImplementedError()

    def tail(self, percentile: float) -> float:
        raise NotImplementedError()

    def average(self) -> float:
        raise NotImplementedError()

    def standard_deviation(self) -> float:
        raise NotImplementedError()

    def min(self) -> float:
        raise NotImplementedError()

    def max(self) -> float:
        raise NotImplementedError()

    @property
    def report(self) -> str:
        raise NotImplementedError()

    def __str__(self):
        return self.report

    def __eq__(self, other):
        if not isinstance(other, Profiler):
            return False
        else:
            return self.full_path == other.full_path

    def __hash__(self):
        return self.full_path


_root_profiler = Profiler()


def profile(name: str) -> Profiler:
    raise NotImplementedError()


def report() -> str:
    return _root_profiler.report


def clean():
    """
    Reset the global instance and clean all instances
    :return:
    """
    global _root_profiler
    _root_profiler = Profiler()
    Profiler._instances = {}


__all__ = ["Profiler", "clean", "profile", "report"]
