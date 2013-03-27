# Names:
# Available (in order of preference)
# grasp graspy pygrasp pysense discern pygrok getit intuit pyintuit pydiscern pyfathom pygetit 
# Taken
# grok sense gist pygist fathom

import types, re

# Handle numpy types if numpy is available.
try: import numpy
except ImportError: numpy = False

# Try to register IPython magic commands if IPython is available
try: import magic
except ImportError: pass

##################################################
# Information about types for apropos searches.
##################################################
#
# You can add your own types to the lists below if you want apropos to
# descend into them.  If you have a container that you want apropos to
# search, but it doesn't respond appropriately to the methods listed
# below, you can give it a function called __apropos__.  This function
# takes no arguments and should return an iterator.  The iterator
# should return the contents of the object, as tuples of
# (element_object, name_string, access_string)
#
# Types in dict_types must respond to __iter__ and [string].  Designed
# for things you access via [string]
# 
# Types in list_types must respond to __iter__().  Designed for things
# you access via [int]
# 
# Types in instance_types must give sensible results to dir(),
# getattr().  Designed for things you access via .

apropos_dict_types = [types.DictType]
apropos_list_types = [types.ListType, types.TupleType]
apropos_instance_types = [types.InstanceType, types.ModuleType]

##################################################
# Information about types for recursive_types() function.
##################################################
recursive_type_simple_types = [bool, complex, float, int, long, str, unicode,
                               types.NoneType]

if numpy: 
    recursive_type_simple_types += [numpy.bool8,
            numpy.complex64, numpy.complex128, numpy.float32, numpy.float64,
            numpy.int0, numpy.int8, numpy.int16,  numpy.int32, numpy.int64,
            numpy.uint0, numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64]
    
    if hasattr(numpy, 'float128') and hasattr(numpy, 'complex256'):
        recursive_type_simple_types += [numpy.float128, numpy.complex256]
        
recursive_type_composite_types = [list, tuple, dict, set, frozenset]

if numpy:
    recursive_type_composite_types += [numpy.ndarray]

##############################
## Utilities.
class sstr(object):
    """Simple String.  Used for pretty output in IPython (no quotes)."""
    def __init__(self, name): self._name = name        
    def __repr__(self): return str(self._name)
    def __str__(self): return str(self._name)

def every(args): 
    """Return True if all elements of args are True."""
    return reduce(lambda x,y: x and y, args, True)

##################################################
## Introspection
##################################################
def gist(obj, verbose=False, pretty=True):
    """See what an object is all about.  Make a dict where the keys
    are the names of each type of attribute in the object.  The values
    are a list of the names of the attribute of that type.

    >>> gist((1,2,3))
    {builtin_function_or_method: [count, index]}

    >>> gist(numpy.array([1,2,3]))
    {buffer: [data],
      int: [itemsize, nbytes, ndim, size],
      builtin_function_or_method: [all, any, argmax]
      tuple: [shape, strides],
      ndarray: [T, imag, real]}

    """
    if pretty: string = sstr
    else: string = str

    info = []
    for name in dir(obj):
        if verbose or not name.startswith('_'):
            try: attr = getattr(obj, name)
            # TODO -- bare except clause here.  What exceptions am I
            # afraid of?
            except: attr = Exception
            info.append((name, type(attr)))

    types = sorted(set([el[1] for el in info]))
    # TODO result used to be a list, not a dict.  Do I prefer that
    # since I'll have deterministic ordering in printouts?  Might make
    # programmatic processing of output worse, but I don't do that
    # anyway and I can always just pass the list to a dict.
    result = {}
    for tt in types:
        names = [string(name) for name, the_type in info if the_type is tt]        
        result[string(t.__name__)] = names
        #result.append((t.__name__, names))
    return result

def recursive_type(obj, max=50):
    """Recursive type() function.  Try to give a concise description of
    the type of an object and all objects it contains.

    >>> recursive_type(1) 
    'int'

    >>> recursive_type((1, 1.1, 2))
    ['tuple of', 'int', 'float', 'int']

    >>> recursive_type((1, 2, 3))
    'tuple of 3 int'

    >>> recursive_type(([1,2], [3,4], [5,6]))
    ['tuple of 3', 'list of 2 int']

    >>> recursive_type((numpy.array([1,2]), numpy.array([3,4]), numpy.array([5,6])))
    ['tuple of 3', 'ndarray of (2,) int64']

    """
    def rtypes_equal(els):
        """Return True if all rtypes equal"""
        first_type = recursive_type(els[0])
        return every([ recursive_type(el) == first_type for el in els])
    def types_equal(els):
        """Return True if all types equal"""
        first_type = type(els[0])
        return every([ type(el) is first_type for el in els])
    def types_simple(els):
        """Return True if all types simple"""
        return every([ type(el) in recursive_type_simple_types for el in els])
    def name(obj):
        """Return the name of obj"""
        return type(obj).__name__
    def shape(obj):
        """Return the shape of obj"""
        if numpy and type(obj) is numpy.ndarray: return str(obj.shape)
        return str(len(obj))
    def contents(obj):
        """Return an iterable object with the contents of obj"""
        if   type(obj) in (list, tuple): return obj
        elif type(obj) in (set, frozenset): return list(obj)
        elif type(obj) is dict: return [obj[k] for k in sorted(obj.keys())]
        elif numpy and type(obj) is numpy.ndarray: return obj.flat
        return None
    
    if type(obj) in recursive_type_composite_types:
        if types_equal(contents(obj)) and types_simple(contents(obj)):
            return ('%s of %s %s' % 
                    (name(obj), shape(obj), name(contents(obj)[0])))
        elif rtypes_equal(contents(obj)):
            return ['%s of %s' % 
                    (name(obj), shape(obj)), recursive_type(contents(obj)[0])]
        elif len(contents(obj)) > max:
            return ['%s of' % name(obj)] \
                   + [recursive_type(el) for el in contents(obj) [:max] ] \
                   + ['........']
        else: 
            return ['%s of' % name(obj)] \
                   + [recursive_type(el) for el in contents(obj)]         
    return name(obj)

##################################################
## Apropos: searching for things
##################################################

##############################
## Main apropos interface function.
def apropos(needle, haystack=None, name=None,
            search=None, **kw):
    """Recursively search through haystack looking for needle.  Typical
    usage is apropos('string', module).
    
    haystack can be any python object.  Typically it's a module.  If
    it's not given, it's the dict returned by globals() (ie, watch
    out, it's going to take a while).

    name is the name of the top level object.  It's first bit of the
    'accessor' strings that are returned.  If not specified, defaults
    to 'arg'.
    
    Matches determined by search.  search(needle, name, obj) returns
    true if the object should be considered a match.  By default,
    search matches if needle is a substring of the name of the object.

    Return a list of strings showing the path to reach the matching
    object

    """
    if haystack is None:
        # TODO Think this is wrong.  Want call to globals to be from user's
        # namespace, not the module space here.  Is there a way to
        # climb up the call stack and steal it from them?  Probably...
        haystack = globals()
        name = ''
    elif name is None:
        if hasattr(haystack, "__name__"):
            name = haystack.__name__
        else:
            name = 'arg'
    
    if search is None: search = search_name

    return _apropos(needle, haystack, name, search, **kw)

##############################
## Common apropos search functions
def search_name(needle, name, obj):
    """Match if needle is contained in name"""
    return name and needle in name    

def search_value(needle, name, obj):
    """Match if needle is contained in the string representation of obj"""
    # String representation of dicts, lists, and tuples includes the
    # objects within them, so don't consider that to be a match on the
    # desired value.  Wait to get inside the container class...
    #
    # TODO What I really want to do is match the container if none of
    # its contents matched.
    if type(obj) not in (types.TupleType, types.ListType,
                         types.DictType):
        return needle in str(obj)
        # NOTE -- should be repr() above?

def search_doc(needle, name, obj):
    """Match if needle is contained in the docstring of obj"""
    return hasattr(obj, '__doc__') and obj.__doc__ \
           and needle in obj.__doc__
    
def search_name_regexp(needle, name, obj):
    """Match if regexp needle matches name"""
    return name and re.search(needle, name)

def search_value_regexp(needle, name, obj):
    """Match if regexp needle matches the string representation of obj"""
    if type(obj) not in (types.TupleType, types.ListType,
                         types.DictType):
        return re.search(needle, str(obj))

def search_doc_regexp(needle, name, obj):
    """Match if regexp needle matches the docstring of obj"""
    return hasattr(obj, '__doc__') \
           and obj.__doc__ \
           and re.search(needle, obj.__doc__)

##############################
## Apropos interface: commonly use cases with convenient syntax

def apropos_name(needle, haystack=None, **kw):
    """Recursively search for attributes with where needle is a substring
    of the name.  See apropos() for addtional keyword arguments.
    Typical usage is apropos_name('string', module).

    Return a list of strings showing the path to reach the matching
    object

    """
    return apropos(needle, haystack, search=search_name, **kw)

def apropos_value(needle, haystack=None, **kw):
    """Recursively search for attributes with where needle is a substring
    the string representation of the object.  See apropos() for
    addtional keyword arguments.  Typical usage is
    apropos_value('string', module).

    Return a list of strings showing the path to reach the matching
    object

    """
    return apropos(needle, haystack, search=search_value, **kw)

def apropos_doc(needle, haystack=None, **kw):
    """Recursively search for attributes with where needle is a substring
    of the documentation string of the object.  See apropos() for
    addtional keyword arguments.  Typical usage is
    apropos_doc('string', module).

    Return a list of strings showing the path to reach the matching
    object

    """
    return apropos(needle, haystack, search=search_doc, **kw)

def apropos_name_regexp (needle, haystack=None, **kw):
    """Recursively search for attributes with where needle is a regexp
    matching the name.  See apropos() for addtional keyword arguments.
    Typical usage is apropos_name_regexp('string', module).

    Return a list of strings showing the path to reach the matching
    object

    """
    return apropos(needle, haystack, search=search_name_regexp, **kw)

def apropos_value_regexp(needle, haystack=None, **kw):
    """Recursively search for attributes with where needle is a regexp
    matching the string representation of the object.  See apropos()
    for addtional keyword arguments.  Typical usage is
    apropos_value_regexp('string', module).

    Return a list of strings showing the path to reach the matching
    object

    """
    return apropos(needle, haystack, search=search_value_regexp, **kw)

def apropos_doc_regexp(needle, haystack=None, **kw):
    """Recursively search for attributes with where needle is a regexp
    matching the docstring of the object.  See apropos() for addtional
    keyword arguments.  Typical usage is apropos_doc_regexp('string',
    module).

    Return a list of strings showing the path to reach the matching
    object

    """
    return apropos(needle, haystack, search=search_doc_regexp, **kw)

##################################################
## Apropos implementation guts.
def _apropos(needle, haystack, haystack_name,
             search, max_depth=None, **kw):
    """Recursively search through haystack looking for needle.

    haystack can be any python object.  Typically it's a module.  If
    it's not given, it's the dict returned by globals() (ie, watch
    out, it's going to take a while).
    
    Matches determined by search.  search(needle, name, obj) returns
    true if the object should be considered a match.  By default,
    search matches if needle is a substring of the name of the object.

    name is the name of the top level object.  It's first bit of the
    'accessor' strings that are returned.  If not specified, defaults
    to 'arg'.

    Return a list of strings showing the path to reach the matching
    object.

    """
    def search_internal(haystack, haystack_name, full_name, depth):
        '''Free variable: needle, search_types'''
        # TODO -- figure out WTF is going on with unicode strings here.
        # for now, just skip them.
        try: 
            if search(needle, haystack_name, haystack):
                found.append(full_name)
        except (UnicodeDecodeError, UnicodeEncodeError):
            if print_warning[0]:
                print "String problems at", full_name
                print_warning[0] = False

        # break apart if obj is not already searched
        if type(haystack) in search_types \
                and (not max_depth or depth < max_depth) \
                and id(haystack) not in searched_ids:
            # Prevent loops with circular references by setting this
            # _before_ descending into sub-objects
            searched_ids.append(id(haystack))

            for hay, hay_name, hay_access in introspect(haystack, **kw):
                search_internal(hay, hay_name, full_name + hay_access, depth+1)

    print_warning = [True]
    searched_ids = []
    found = []
    search_types = apropos_dict_types + apropos_list_types + apropos_instance_types

    search_internal(haystack, haystack_name, haystack_name, 0)
    return found

def introspect(obj, **kw):
    """Return an object that's capable of iterating over the contents of
    obj

    """
    if type(obj) in apropos_dict_types:
        return DictIntrospector(obj, **kw)
    if type(obj) in apropos_list_types:
        return ListIntrospector(obj, **kw)
    if type(obj) in apropos_instance_types:
        return InstanceIntrospector(obj, **kw)

    # User objects
    if hasattr(obj, '__apropos__'):
        return obj.__apropos__(**kw)

    # Stymied
    print "apropos.py: Warning, don't know how to deal with " + str(obj)
    return NullIntrospector()

# NOTE These introspectors simplify the code, but they seem to take about five
# times as long, very unfortunately.
class Introspector (object):
    """Object that implements the iterator interface"""
    def __iter__(self):
        return self

    def next(self):
        pass

class DictIntrospector (Introspector):
    """Object that can iterate over the contents of a dict"""
    # types that respond to __iter__, obj.[key] to get a value
    def __init__(self, dict, exclude=None):
        self.dict = dict
        self.iter = self.dict.__iter__()        
        self.exclude = exclude
        
    def next(self):
        # return tuple of obj, name, access_name
        k = self.iter.next()
        # TODO -- completely skip non-string key entries
        while type(k) is not types.StringType \
              or (self.exclude and k.startswith(self.exclude)):
            k = self.iter.next()
        return self.dict[k], k, '[' + k + ']'

class ListIntrospector (Introspector):
    """Object that can iterate over the contents of a list"""
    # types that respond to __iter__
    def __init__(self, list, exclude=None):
        self.list = list
        self.iter = self.list.__iter__()
        self.i = 0

    def next(self):
        # return tuple of obj, name, access_name
        self.i += 1
        return self.iter.next(), None, '[' + str(self.i-1) + ']'

class InstanceIntrospector (Introspector):
    """Object that can iterate over the contents of a instance"""
    # classes that respond to dir and getattr
    def __init__(self, inst, exclude=None):
        self.inst = inst
        self.iter = dir(self.inst).__iter__()
        self.exclude = exclude

    def next(self):
        # return tuple of obj, name, access_name

        # IPython structs allow non-string attributes.  Filter them
        # out because they cause problems.  That is, you have to
        # access them via obj[1], not getattr(obj, 1) or
        # getattr(obj, '1').  
        # TODO -- could handle the above w/ use of eval
        # TODO -- filter out non-string things that appear in dir()

        name = self.iter.next()
        while type(name) is not types.StringType \
              or (self.exclude and name.startswith(self.exclude)):
            name = self.iter.next()
        return getattr(self.inst, name), name, "." + name

class NullIntrospector (Introspector):
    """Object for the case where it's not known how to iterate over the
    given object.

    """
    def __init__(self, **kw):
        pass

    def next(self):
        raise StopIteration

## End of apropos implementation guts.
##################################################
