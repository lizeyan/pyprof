def close(a: float, b: float) -> bool:
    return abs(a - b) < max(1e-1 * abs(a + b), 1e-4)


__all__ = ['close']
