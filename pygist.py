import types
import numpy

class sstr(object):
    """Simple String.  Used for pretty output in IPython (no quotes)."""
    def __init__(self, name): self._name = name        
    def __repr__(self): return str(self._name)
    def __str__(self): return str(self._name)

def every(args): return reduce(lambda x,y: x and y, args, True)

##################################################
## Introspection
def gist(obj, verbose=False, pretty=True):
    """See what an object is all about.  Make a dict where the keys
    are the names of each type of attribute in the object.  The values
    are a list of the names of the attribute of that type."""
    if pretty: string = sstr
    else: string = str

    info = []
    for name in dir(obj):
        if verbose or (not verbose and not name.startswith('_')):
            try: attr = getattr(obj, name)
            except: attr = Exception
            info.append((name, type(attr)))

    types = sorted(set([el[1] for el in info]))
    result = {}
    for t in types:
        names = [string(name) for name, theType in info if theType is t]        
        result[string(t.__name__)] = names
        #result.append((t.__name__, names))
    return result

simpleTypes = [bool, complex, float, int, long, str, unicode,
               types.NoneType,
               numpy.bool8,
               numpy.complex64, numpy.complex128,
               numpy.float32, numpy.float64,
               numpy.int0, numpy.int8, numpy.int16, numpy.int32, numpy.int64,
               numpy.uint0, numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64]

if hasattr(numpy, 'float128') and hasattr(numpy, 'complex256'):
    simpleTypes += [numpy.float128, numpy.complex256]
        
compositeTypes = [list, tuple, dict, set, frozenset, numpy.ndarray,]

def rtype(obj, max=50):
    """Recursive type() function.  Try to give a concise description
    of the type of an object and all objects it contains."""
    def rtypesEqual(els):
        firstType = rtype(els[0])
        return every([ rtype(el) == firstType for el in els])
    def typesEqual(els):
        firstType = type(els[0])
        return every([ type(el) is firstType for el in els])
    def typesSimple(els):
        return every([ type(el) in simpleTypes for el in els])
    def name(obj):
        return type(obj).__name__
    def shape(obj):
        if type(obj) is numpy.ndarray: return str(obj.shape)
        return str(len(obj))
    def contents(obj):
        if   type(obj) in (list, tuple): return obj
        elif type(obj) in (set, frozenset): return list(obj)
        elif type(obj) is dict: return [obj[k] for k in sorted(obj.keys())]
        elif type(obj) is numpy.ndarray: return obj.flat
        return None
    
    if type(obj) in compositeTypes:
        if typesEqual(contents(obj)) and typesSimple(contents(obj)):
            return '%s of %s %s' % (name(obj), shape(obj), name(contents(obj)[0]))
        elif rtypesEqual(contents(obj)):
            return ['%s of %s' % (name(obj), shape(obj)), rtype(contents(obj)[0])]
        elif len(contents(obj)) > max:
            return ['%s of' % name(obj)] \
                   + [rtype(el) for el in contents(obj) [:max] ] \
                   + ['........']
        else: 
            return ['%s of' % name(obj)] \
                   + [rtype(el) for el in contents(obj)]         
    return name(obj)

