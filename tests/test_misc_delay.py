import init 
from time import time

from scread.misc.delay import delayed, dmap


class Closure: pass


def test_dmap():
    cl = Closure()
    cl.log = []
   
    square = lambda x: x*x
    n = 10
    data = range(0, n)

    def report(i, n):
        cl.log.append(i)

    cl.log[:] = []
    slow_square = delayed(0.05)(lambda x: x*x)
    assert dmap(slow_square, data, report, 0.1) == map(square, data)
    assert len(cl.log) == 4

    cl.log[:] = []
    fast_square = delayed(0.025)(lambda x: x*x)
    assert dmap(fast_square, data, report, 0.1) == map(square, data)
    assert len(cl.log) == 2


def test_delay():
    cl = Closure()
    cl.log = []
   
    def with_report(f):
        def result(*args):
            cl.log.append(time())
            return f(*args)
        return result
  
    square = lambda x: x*x
    n = 10
    data = range(0, n)


    cl.log[:] = []
    slow_square = delayed(0.05)(with_report(lambda x: x*x))
    assert map(slow_square, data) == map(square, data)
    
    diff = map(lambda (x, y): x-y, zip(cl.log[1:n], cl.log[0:(n-1)]))
    assert reduce(max, diff) < 0.1
    assert reduce(min, diff) > 0.05
   

    cl.log[:] = []
    fast_square = delayed(0.01)(with_report(lambda x: x*x))
    assert map(fast_square, data) == map(square, data)

    diff = map(lambda (x, y): x-y, zip(cl.log[1:n], cl.log[0:(n-1)]))
    assert reduce(max, diff) < 0.05 
    assert reduce(min, diff) > 0.01


   
