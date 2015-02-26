""" tools.py: provides auxiliary functions for general purposes. """

from copy import deepcopy


def drepr(x, sort = True, indent = 0):
    """ Formats dictionary x in a readable way.
    Taken from http://ze.phyr.us/python-dict-repr/
    """
    if isinstance(x, dict):
        r = '{\n'
        for (key, value) in (sorted(x.items()) if sort else x.iteritems()):
            r += (' ' * (indent + 4)) + repr(key) + ': '
            r += drepr(value, sort, indent + 4) + ',\n'
        r = r.rstrip(',\n') + '\n'
        r += (' ' * indent) + '}'
    elif hasattr(x, '__iter__'):
        r = '[\n'
        for value in (sorted(x) if sort else x):
            r += (' ' * (indent + 4)) + drepr(value, sort, indent + 4) + ',\n'
        r = r.rstrip(',\n') + '\n'
        r += (' ' * indent) + ']'
    else:
        r = repr(x)
    return r

    
def unfold(d, s = None):
    """ Runs each function in dictionary d with itself as an argument.
    Thus, a self-referrenced dictionary can be created.
    """

    if s is None:
        s = d
    for k, v in d.iteritems():
        d[k] = (type(v) is dict and unfold(v, s)) or (callable(v) and v(s)) or v
    return d



def update(lhs, rhs):
    """ Recursively updates lhs with values of rhs. """

    for k, v in rhs.iteritems():
        if (k in lhs) and (type(lhs[k]) is dict) and (type(v) is dict):
            update(lhs[k], v)
        else:
            lhs[k] = v

    return lhs 


def merge(lhs, rhs):
    """ Returns updated copy of lhs with rhs """

    result = deepcopy(lhs)
    update(result, rhs)
    return result 



def cached(f):
    class Closure:pass
    cl = Closure()
    cl.data = {}

    def result(*args):
        if args not in cl.data:
            cl.data[args] = f(*args)
        return cl.data[args]
    
    return result
