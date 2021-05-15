def close(a: float, b: float) -> bool:
    return abs(a - b) < 1e-4 * abs(a + b)
