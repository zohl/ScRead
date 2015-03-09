""" cache.py: provides 'cached' and 'refresh' decorators """

def _mk_interface():
    class Closure:pass
    gcl = Closure()
    gcl.namespaces = {}


    def cached(namespace):
        def decorator(f):
            cl = Closure()
            cl.data = {}
            if namespace not in gcl.namespaces:
                gcl.namespaces[namespace] = []
            gcl.namespaces[namespace].append(cl.data)

            def result(*args):
                if args not in cl.data:
                    cl.data[args] = f(*args)
                return cl.data[args]
            return result
        return decorator


    def refresh(namespace):
        def decorator(f):
            def result(*args):
                for cache in gcl.namespaces[namespace]:
                    cache.clear()
                return f(*args)
            return result
        return decorator

    return [cached, refresh]


[cached, refresh] = _mk_interface()
