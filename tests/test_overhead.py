import time

from pyprof import profile, Profiler

real_time = 0.


@profile
def f():
    tic = time.perf_counter()
    time.sleep(1e-2)
    global real_time
    real_time += time.perf_counter() - tic


def test_overhead():
    n_times = 100
    for i in range(n_times):
        f()
    total_time = Profiler.get("/f").total
    print(f'total={total_time:.4f}s real_time={real_time:.4f}s')
    average_overhead = (total_time - real_time) / n_times
    assert average_overhead < 1e-4  # 0.1ms
    print(f'average overhead={average_overhead * 1000:.4f}ms')


if __name__ == '__main__':
    test_overhead()
