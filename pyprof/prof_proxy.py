import types
from collections import defaultdict
from functools import wraps
from threading import Thread, current_thread
from typing import overload, Callable, Any

from .pyprof import Profiler


class ProfilerProxy:
    active_proxy: dict[Thread, list[tuple["ProfilerProxy", "Profiler"]]] = defaultdict(list)

    def __init__(self, name: str, report_printer: Callable[[str], Any] = None):
        self.name = name
        self.report_printer = report_printer

    def __enter__(self):
        current_stack = self.active_proxy[current_thread()]
        profiler = Profiler(
            self.name,
            current_stack[-1][1] if current_stack else None
        )
        self.active_proxy[current_thread()].append((self, profiler))
        profiler.__enter__()
        return profiler

    def __exit__(self, exc_type, exc_val, exc_tb):
        _, profiler = self.active_proxy[current_thread()].pop()
        profiler.__exit__(exc_type, exc_val, exc_tb)
        if self.report_printer is not None:
            self.report_printer(profiler.report_header() + profiler.report())

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper


@overload
def profile(name: str, report_printer=None) -> Callable:
    ...


@overload
def profile(func: Callable) -> Callable:
    ...


def profile(arg: str or Callable, report_printer=None) -> Callable:
    if isinstance(arg, str):
        return ProfilerProxy(arg, report_printer=report_printer)

    func = arg

    @wraps(func)
    def wrapper(*args, **kwargs):
        with ProfilerProxy(
                func.__qualname__
        ):
            return func(*args, **kwargs)

    return wrapper


__all__ = ['profile']
