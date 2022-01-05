from collections import defaultdict
from functools import wraps
from threading import Thread, current_thread
from typing import overload, Callable, Any, Union, Dict, List, Tuple, Optional

from .pyprof import Profiler


class ProfilerProxy:
    active_proxy: Dict[Thread, List[Tuple["ProfilerProxy", "Profiler"]]] = defaultdict(list)

    def __init__(
            self, name: str, report_printer: Callable[[str], Any] = None, flush=False,
            min_total_percent: float = 0., min_parent_percent: float = 0.
    ):
        self.name = name
        self.report_printer = report_printer
        self.flush = flush
        self.min_total_percent = min_total_percent
        self.min_parent_percent = min_parent_percent

    @classmethod
    def nearest_proxy(cls) -> Optional[Tuple['ProfilerProxy', Profiler]]:
        current_stack = cls.active_proxy[current_thread()]
        return current_stack[-1] if current_stack else None

    def __enter__(self):
        profiler = Profiler(
            self.name,
            current_profiler(),
            flush=self.flush,
        )
        self.flush = False  # flush for the first tic-toc only
        self.active_proxy[current_thread()].append((self, profiler))
        profiler.__enter__()
        return profiler

    def __exit__(self, exc_type, exc_val, exc_tb):
        _, profiler = self.active_proxy[current_thread()].pop()
        profiler.__exit__(exc_type, exc_val, exc_tb)
        if self.report_printer is not None:
            self.report_printer(
                profiler.report_header() + profiler.report(
                    min_total_percent=self.min_total_percent,
                    min_parent_percent=self.min_parent_percent,
                )
            )

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper


@overload
def profile(
        name: str, *, report_printer=None, flush: bool = False,
        min_total_percent: float = 0.,
        min_parent_percent: float = 0.,
) -> Callable:
    ...


@overload
def profile(func: Callable) -> Callable:
    ...


def profile(
        arg: Union[str, Callable], *, report_printer=None,
        flush: bool = False,
        min_total_percent: float = 0.,
        min_parent_percent: float = 0.,
) -> Callable:
    # work as a context manager
    if isinstance(arg, str):
        return ProfilerProxy(
            arg, report_printer=report_printer, flush=flush,
            min_total_percent=min_total_percent,
            min_parent_percent=min_parent_percent,
        )

    func = arg

    # work as a decorator
    @wraps(func)
    def wrapper(*args, **kwargs):
        with ProfilerProxy(
                name=func.__qualname__,
                report_printer=report_printer,
                flush=flush,
        ):
            return func(*args, **kwargs)

    return wrapper


def current_profiler() -> Optional[Profiler]:
    """
    :return: return the current profiler in the profiler stack defined by profile()
    """
    p = ProfilerProxy.nearest_proxy()
    return p[1] if p else None


__all__ = ['profile', 'current_profiler']
