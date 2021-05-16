from collections import defaultdict
from functools import wraps
from threading import Thread, current_thread
from typing import overload, Callable

from .pyprof import Profiler


class ProfilerProxy:
    active_proxy: dict[Thread, list[tuple["ProfilerProxy", "Profiler"]]] = defaultdict(list)

    def __init__(self, name: str):
        self.name = name

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

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper


@overload
def profile(name: str) -> Callable:
    ...


@overload
def profile(func: Callable) -> Callable:
    ...


def profile(arg: str or Callable) -> Callable:
    if isinstance(arg, str):
        return ProfilerProxy(arg)

    func = arg

    @wraps(func)
    def wrapper(*args, **kwargs):
        with ProfilerProxy(func.__name__):
            return func(*args, **kwargs)

    return wrapper


__all__ = ['profile']
