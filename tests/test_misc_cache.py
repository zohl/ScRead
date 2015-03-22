import init 
from scread.misc.cache import cached, refresh


log = []

@cached('a')
def fibs(n):
    log.append('tick')
    if n <= 0: return 0
    if n == 1: return 1
    return fibs(n-1) + fibs(n-2)

@refresh('a')
def reset_a():
    pass


@cached('b')
def conj(n):
    log.append('tick')
    if n == 1: return 1
    # return 0 if it doesn't converge :D
    return conj((3*n + 1) if n%2 else (n/2))

@refresh('b')
def reset_b():
    pass


@cached('a')
@refresh('b')
def reset_b_if_a():
    pass



def test_caching():
    log[:] = []
    reset_a()
    assert fibs(100) == fibs(100)
    assert len(log) == 101
    

def test_refreshing():
    log[:] = []
    reset_a()

    res = fibs(100)
    reset_a()
    assert res == fibs(100)
    assert len(log) == 202


def test_namespaces():
    log[:] = []
    reset_a()
    reset_b()

    fibs(100)
    l1 = len(log)

    conj(100)
    l2 = len(log) - l1

    reset_a()
    fibs(100)
    assert len(log) == l1 + l1 + l2
   
    conj(100)
    assert len(log) == l1 + l1 + l2



def test_hierarhy():
    log[:] = []
    reset_a()
    reset_b()
    
    conj(100)
    l1 = len(log)

    reset_b_if_a()
    conj(100)
    assert len(log) == l1 + l1, '"b" namespace was reset'
    
    reset_b_if_a()
    conj(100)
    assert len(log) == l1 + l1, 'reset_b_if_a is cached, no side effects'
