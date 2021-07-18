# PyProf
[![PyPI version](https://badge.fury.io/py/pyprof.svg)](https://badge.fury.io/py/pyprof)
![Build Status](https://github.com/lizeyan/pyprof/actions/workflows/pythonpackage.yml/badge.svg)
![Coverage](https://coveralls.io/repos/github/lizeyan/pyprof/badge.svg?branch=dev&t=VBgxyx)

# Example
``` python
from pyprof import profile, Profiler, report
import time
from concurrent.futures import ThreadPoolExecutor
from tests.test_utils import close


# `profile` can be used as a decorator directly.
# In such cases, the name of the Profiler is automatically extracted
@profile
def f():
    time.sleep(0.1)
    # `profile` can be used as a context manager
    with profile("sleep"):
        time.sleep(0.03)


# `profile` can be used as a decorator with a specified name
@profile('single-thread')
def h():
    for i in range(10):
        f()


@profile('multi-thread')
def g():
    with ThreadPoolExecutor() as executor:
        for i in range(10):
            executor.submit(f)


def test_main():
    h()
    assert Profiler.get("/single-thread").count == 1
    assert close(Profiler.get("/single-thread").total, 10 * 0.13)
    # Profiler automatically find parent Profiler
    assert Profiler.get("/single-thread/f").count == 10
    assert close(Profiler.get("/single-thread/f").total, 10 * 0.13)
    assert close(Profiler.get("/single-thread/f").average, 0.13)
    assert close(Profiler.get("/single-thread/f").standard_deviation, 0.)
    assert close(Profiler.get("/single-thread/f/sleep").total, 10 * 0.03)
    assert close(Profiler.get("/single-thread/f/sleep").average, 0.03)
    assert close(Profiler.get("/single-thread/f/sleep").standard_deviation, 0.)

    g()
    assert Profiler.get("/multi-thread").count == 1
    # Profiler cannot automatically find parent Profiler in other threads
    assert Profiler.get("/f").count == 10
    assert close(Profiler.get("/f").total, 10 * 0.13)
    assert close(Profiler.get("/f").average, 0.13)
    assert close(Profiler.get("/f").standard_deviation, 0.)
    assert close(Profiler.get("/f/sleep").total, 10 * 0.03)
    assert close(Profiler.get("/f/sleep").average, 0.03)
    assert close(Profiler.get("/f/sleep").standard_deviation, 0.)

    # print a formatted time usage report
    print(report())

    # `profile` automatically print report if `report_printer` is given
    with profile('auto-print', report_printer=print):
        f()
    with profile('auto-print', report_printer=print):
        f()
    assert Profiler.get("/auto-print").count == 2

    # use `flush=True` to reset a Profiler and all its children
    with profile('auto-print', report_printer=print, flush=True):
        f()
    assert Profiler.get("/auto-print").count == 1

```

Output
```markdown
|path                  |%total     |%parent    |count   |total      |mean(±std)              |min-max              |
|                      |    100.00%|    100.00%|      12|     2.862s|     0.238(±     0.334)s|     0.137~     1.345|
|/f                    |     48.14%|     48.14%|      10|     1.378s|     0.138(±     0.000)s|     0.137~     0.138|
|/f/sleep              |     11.85%|     24.63%|      10|     0.339s|     0.034(±     0.001)s|     0.032~     0.035|
|/multi-thread         |      4.87%|      4.87%|       1|     0.139s|     0.139(±     0.000)s|     0.139~     0.139|
|/single-thread        |     47.00%|     47.00%|       1|     1.345s|     1.345(±     0.000)s|     1.345~     1.345|
|/single-thread/f      |     46.98%|     99.97%|      10|     1.345s|     0.134(±     0.002)s|     0.130~     0.138|
|/single-thread/f/sleep|     11.30%|     24.05%|      10|     0.323s|     0.032(±     0.002)s|     0.030~     0.035|

|path               |%total     |%parent    |count   |total      |mean(±std)              |min-max              |
|/auto-print        |      4.63%|      4.63%|       1|     0.139s|     0.139(±     0.000)s|     0.139~     0.139|
|/auto-print/f      |      4.63%|     99.97%|       1|     0.139s|     0.139(±     0.000)s|     0.139~     0.139|
|/auto-print/f/sleep|      1.17%|     25.37%|       1|     0.035s|     0.035(±     0.000)s|     0.035~     0.035|

|path               |%total     |%parent    |count   |total      |mean(±std)              |min-max              |
|/auto-print        |      8.71%|      8.71%|       2|     0.273s|     0.137(±     0.002)s|     0.134~     0.139|
|/auto-print/f      |      8.71%|     99.97%|       2|     0.273s|     0.136(±     0.002)s|     0.134~     0.139|
|/auto-print/f/sleep|      2.09%|     23.99%|       2|     0.065s|     0.033(±     0.002)s|     0.030~     0.035|

|path               |%total     |%parent    |count   |total      |mean(±std)              |min-max              |
|/auto-print        |      4.25%|      4.25%|       1|     0.139s|     0.139(±     0.000)s|     0.139~     0.139|
|/auto-print/f      |      4.24%|     99.98%|       1|     0.139s|     0.139(±     0.000)s|     0.139~     0.139|
|/auto-print/f/sleep|      1.06%|     24.90%|       1|     0.035s|     0.035(±     0.000)s|     0.035~     0.035|


```

# Roadmap
- [ ] Measure and control the overhead of `pyprof`
- [ ] Automatically decide column width for more columns in `report`
- [ ] Support capture parent profiler in a multi-thread context
- [ ] Support multi-process (currently Profilers in subprocesses are all detached)
