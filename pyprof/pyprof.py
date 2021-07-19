import time
import warnings
from functools import lru_cache, wraps
from io import StringIO
from math import sqrt
from threading import current_thread, Thread, Lock
from typing import Callable, Dict, Set, List


class Profiler:
    _instances: Dict[str, "Profiler"] = {}
    _lock = Lock()

    @staticmethod
    def get(full_path: str) -> "Profiler":
        """
        Get a Profiler by its full path
        :param full_path:
        :return:
        """
        return Profiler._instances[full_path]

    @staticmethod
    def _generate_full_path(name: str, parent: "Profiler"):
        """
        Format the full path given the current name the parent Profiler
        :param name:
        :param parent: should already be resolved
        :return:
        """
        if parent == "__ROOT__":
            parent = None
        elif parent is None:
            parent = _root_profiler
        else:
            parent = parent
        if parent is None or parent == "__ROOT__":
            full_path = f"{name}"
        else:
            full_path = f"{parent.full_path if parent is not None else ''}/{name}"
        return parent, full_path

    def _need_init(self, flush=False):
        """
        1. _initialized is not set
        2. flush=True
        3. _initialized before any parent
        :param flush:
        :return:
        """
        if not hasattr(self, '_initialized') or flush:
            return True

    def __init__(self, name: str = "", parent: "Profiler" = None, flush=False):
        """
        If the Profiler is inited before, then the __init__ will be skipped
        :param name:
        :param parent:
        :param flush:
        """
        self._name = name
        self._parent, self._full_path = self._generate_full_path(name, parent)
        del name, parent

        # skip init if necessary
        if not self._need_init(flush=flush):
            return

        if self._parent is not None:
            self._parent._children.add(self)

        # destroy existing children if any
        if hasattr(self, '_children'):
            for _ in self._children:
                _._destroy()
        self._children: Set["Profiler"] = set()

        self._elapsed_times = []
        self._cached_statistics = {}

        self._tics: Dict[Thread, float] = {}
        self._initialized = time.perf_counter()

    def _destroy(self):
        del Profiler._instances[self._full_path]
        for _ in self._children:
            # noinspection PyProtectedMember
            _._destroy()
        self._children = set()

    def __new__(cls, name: str = "", parent: "Profiler" = None, flush=False):
        parent, full_path = Profiler._generate_full_path(name, parent)
        if full_path not in Profiler._instances:
            Profiler._instances[full_path] = super(Profiler, cls).__new__(cls)
        return Profiler._instances[full_path]

    def __enter__(self):
        self.tic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.toc()

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                ret = func(*args, **kwargs)
            return ret

        return wrapper

    def tic(self):
        """
        Record the current perf_counter
        :return:
        """
        with self._lock:
            self._tics[current_thread()] = time.perf_counter()

    @staticmethod
    def __fill_parent_times_if_not_triggered(profiler: 'Profiler', elapsed_time: float):
        """
        In case that parent Profiler is not triggered while the children Profiler are
        """
        if profiler is None:
            return
        profiler._elapsed_times.append(elapsed_time)
        profiler._cached_statistics = {}
        Profiler.__fill_parent_times_if_not_triggered(profiler._parent, elapsed_time)

    def toc(self):
        """
        Record the difference between the most recent tic and clean the tic
        :return:
        """
        with self._lock:
            if current_thread() not in self._tics:
                warnings.warn("Unmatched toc")
                return
            self._elapsed_times.append(time.perf_counter() - self._tics[current_thread()])
            if self._parent is not None and not self._parent._tics:  # parent Profiler is not in tic
                self.__fill_parent_times_if_not_triggered(self._parent, self._elapsed_times[-1])
            self._cached_statistics = {}
            del self._tics[current_thread()]

    @property
    def sorted_times(self) -> List[float]:
        if "sorted_elapsed_times" not in self._cached_statistics:
            self._cached_statistics['sorted_elapsed_times'] = sorted(self._elapsed_times)
        return self._cached_statistics['sorted_elapsed_times']

    @property
    def times(self) -> List[float]:
        return self._elapsed_times

    @property
    def name(self) -> str:
        return self._name

    @property
    def full_path(self) -> str:
        return self._full_path

    @property
    def count(self) -> int:
        """
        Get the number of tic-toc-pairs
        :return:
        """
        return len(self.times)

    @property
    def total(self) -> float:
        """
        Get the total time of all tic-toc-pairs
        :return:
        """
        if self.count == 0:
            return 0
        if "total" not in self._cached_statistics:
            self._cached_statistics['total'] = sum(self.times)
        return self._cached_statistics['total']

    def tail(self, percentile: float) -> float:
        if self.count == 0:
            return 0
        idx = int(percentile * 0.01 * self.count)
        return self.sorted_times[idx]

    @property
    def average(self) -> float:
        if self.count == 0:
            return 0
        if "average" not in self._cached_statistics:
            self._cached_statistics['average'] = sum(self.times) / self.count
        return self._cached_statistics['average']

    @property
    def standard_deviation(self) -> float:
        if self.count == 0:
            return 0
        if "std" not in self._cached_statistics:
            self._cached_statistics['std'] = sqrt(sum([(_ - self.average) ** 2 for _ in self.times]) / self.count)
        return self._cached_statistics['std']

    @property
    def min_time(self) -> float:
        if self.count == 0:
            return 0
        return self.sorted_times[0]

    @property
    def max_time(self) -> float:
        if self.count == 0:
            return 0
        return self.sorted_times[-1]

    def report(self, full_path_width=None, min_total_percent: float = 0, min_parent_percent: float = 0) -> str:
        if full_path_width is not None:
            full_path_width = full_path_width
        else:
            full_path_width = self._max_children_full_path_length()
        total_percent = self.total / max(_root_profiler.total, 1e-4) * 100
        if self._parent is not None:
            parent_percent = self.total / max(self._parent.total, 1e-4) * 100
        else:
            parent_percent = total_percent
        with StringIO() as ret:
            if total_percent >= min_total_percent * 100 and parent_percent >= min_parent_percent * 100:
                print(
                    f"|{self.full_path:<{full_path_width}}"
                    f"|{total_percent:10.2f}%"
                    f"|{parent_percent:10.2f}%"
                    f"|{self.count:8}"
                    f"|{self.total:10.3f}s"
                    f"|{self.average:10.3f}(±{self.standard_deviation:10.3f})s"
                    f"|{self.min_time:10.3f}~{self.max_time:10.3f}"
                    f"|",
                    file=ret,
                )
            for child in sorted(self._children, key=lambda _: _.name):
                print(child.report(
                    full_path_width=full_path_width,
                    min_total_percent=min_total_percent,
                    min_parent_percent=min_parent_percent,
                ), file=ret, end="")
            return ret.getvalue()

    def report_header(self) -> str:
        full_path_width = self._max_children_full_path_length()
        with StringIO() as ret:
            print(
                f"|{'path':<{full_path_width}}"
                f"|{'%total':11}"
                f"|{'%parent':11}"
                f"|{'count':<8}"
                f"|{'total':11}"
                f"|{'mean(±std)':<24}"
                f"|{'min-max':<21}"
                f"|",
                file=ret,
            )
            return ret.getvalue()

    @lru_cache(maxsize=None)
    def _max_children_full_path_length(self):
        return max([len(self.full_path)] + [child._max_children_full_path_length() for child in self._children])

    def __str__(self):
        return self.report()

    def __eq__(self, other):
        if not isinstance(other, Profiler):
            return False
        else:
            return self.full_path == other.full_path

    def __hash__(self):
        return hash(self.full_path)


def clean():
    """
    Reset the global instance and clean all instances
    :return:
    """
    global _root_profiler
    Profiler._instances = {}
    Profiler._active_instances = {}
    # noinspection PyTypeChecker
    _root_profiler = Profiler("", "__ROOT__")


def report(min_total_percent: float = 0., min_parent_percent: float = 0.) -> str:
    body = _root_profiler.report(min_total_percent=min_total_percent, min_parent_percent=min_parent_percent)
    return f'{_root_profiler.report_header()}{body}'


# noinspection PyTypeChecker
_root_profiler = None  # type: Profiler
clean()

__all__ = ["Profiler", "clean", "report"]
