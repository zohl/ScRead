""" delay.py: provides functions to deal with slow/expensive calls. """

from time import sleep, time
from tools import Closure

def delayed(ss):
    def decorator(f):
        def result(*args):
            res = f(*args)
            sleep(ss)
            return res
        return result
    return decorator


def dmap(f, xs, callback, ss = 3):
    cl = Closure()
    n = len(xs)

    def mf((i, x)):
        curr = time()
        if curr - cl.last > ss:
            cl.last = curr
            callback(i, n)
        return f(x)

    cl.last = time()
    return map(mf, zip(range(0,n), xs))
    
