# Version history
# v0.2 14 Jan 2007
# v0.1 19 Dec 2006
# Code released public domain.  Do whatever you want with it.

import types, re
import numpy

__version__ = 0.2
__author__ = "Greg Novak <greg.novak@gmail.com>"

# For rtypes
rtype_simple_types = [bool, complex, float, int, long, str, unicode,
               types.NoneType,
               numpy.bool8,
               numpy.complex64, numpy.complex128,
               numpy.float32, numpy.float64,
               numpy.int0, numpy.int8, numpy.int16, numpy.int32, numpy.int64,
               numpy.uint0, numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64]

if hasattr(numpy, 'float128') and hasattr(numpy, 'complex256'):
    rtype_simple_types += [numpy.float128, numpy.complex256]
        
rtype_composite_types = [list, tuple, dict, set, frozenset, numpy.ndarray,]

# For apropos searches.
#
# You can add your own types to these lists if you want apropos to
# descend into them.  If you have a container that you want apropos to
# search, but it doesn't respond appropriately to the methods listed
# below, you can give it a function called __apropos__.  This function
# takes no arguments and should return an iterator.  The iterator
# should return the contents of the object, as tuples of
# (element_object, name_string, access_string)

# Must respond to __iter__ and [string].  Designed for things you
# access via [string]
dict_types = [types.DictType]
# Must respond to __iter__().  Designed for things you access via
# [int]
# TODO -- bytearray and memoryview, not sure why they're not showing
# up in types module.  They look like python builtins
list_types = [types.ListType, types.TupleType]
# Must give sensible results to dir(), getattr().  Designed for things
# you access via .
instance_types = [types.InstanceType, types.ModuleType]
# Not sure what to do with memoryview.  Looks like an array but doens't have iter
# memoryview

class sstr(object):
    """Simple String.  Used for pretty output in IPython (no quotes)."""
    def __init__(self, name): self._name = name        
    def __repr__(self): return str(self._name)
    def __str__(self): return str(self._name)

def every(args): 
    return reduce(lambda x,y: x and y, args, True)

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
        names = [string(name) for name, the_type in info if the_type is t]        
        result[string(t.__name__)] = names
        #result.append((t.__name__, names))
    return result

def rtype(obj, max=50):
    """Recursive type() function.  Try to give a concise description
    of the type of an object and all objects it contains."""
    def rtypes_equal(els):
        first_type = rtype(els[0])
        return every([ rtype(el) == first_type for el in els])
    def types_equal(els):
        first_type = type(els[0])
        return every([ type(el) is first_type for el in els])
    def types_simple(els):
        return every([ type(el) in rtype_simple_types for el in els])
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
    
    if type(obj) in rtype_composite_types:
        if types_equal(contents(obj)) and types_simple(contents(obj)):
            return '%s of %s %s' % (name(obj), shape(obj), name(contents(obj)[0]))
        elif rtypes_equal(contents(obj)):
            return ['%s of %s' % (name(obj), shape(obj)), rtype(contents(obj)[0])]
        elif len(contents(obj)) > max:
            return ['%s of' % name(obj)] \
                   + [rtype(el) for el in contents(obj) [:max] ] \
                   + ['........']
        else: 
            return ['%s of' % name(obj)] \
                   + [rtype(el) for el in contents(obj)]         
    return name(obj)

##################################################
## Interface

## Common Usage
def apropos_name(needle, haystack=None, **kw):
    """Recursively search for attributes with where needle is a
    substring of the name.  See apropos() for addtional keyword
    arguments.  Typical usage is apropos_name('string', module).

    Return a list of strings showing the path to reach the matching
    object"""
    return apropos(needle, haystack, search=search_name, **kw)

def apropos_value(needle, haystack=None, **kw):
    """Recursively search for attributes with where needle is a
    substring the string representation of the object.  See apropos()
    for addtional keyword arguments.  Typical usage is
    apropos_value('string', module).

    Return a list of strings showing the path to reach the matching
    object"""
    return apropos(needle, haystack, search=search_value, **kw)

def apropos_doc(needle, haystack=None, **kw):
    """Recursively search for attributes with where needle is a
    substring of the documentation string of the object.  See
    apropos() for addtional keyword arguments.  Typical usage is
    apropos_doc('string', module).

    Return a list of strings showing the path to reach the matching
    object"""
    return apropos(needle, haystack, search=search_doc, **kw)

def apropos_name_regexp (needle, haystack=None, **kw):
    """Recursively search for attributes with where needle is a regexp
    matching the name.  See apropos() for addtional keyword arguments.
    Typical usage is apropos_name_regexp('string', module).

    Return a list of strings showing the path to reach the matching
    object"""
    return apropos(needle, haystack, search=search_name_regexp, **kw)

def apropos_value_regexp(needle, haystack=None, **kw):
    """Recursively search for attributes with where needle is a regexp
    matching the string representation of the object.  See apropos()
    for addtional keyword arguments.  Typical usage is
    apropos_value_regexp('string', module).

    Return a list of strings showing the path to reach the matching
    object"""
    return apropos(needle, haystack, search=search_value_regexp, **kw)

def apropos_doc_regexp(needle, haystack=None, **kw):
    """Recursively search for attributes with where needle is a regexp
    matching the docstring of the object.  See apropos() for addtional
    keyword arguments.  Typical usage is apropos_doc_regexp('string',
    module).

    Return a list of strings showing the path to reach the matching
    object"""
    return apropos(needle, haystack, search=search_doc_regexp, **kw)

## Handles default values of arguments
def apropos(needle, haystack=None, name=None,
            search=None, **kw):
    """Recursively search through haystack looking for needle.
    Typical usage is apropos('string', module).
    
    haystack can be any python object.  Typically it's a module.  If
    it's not given, it's the dict returned by globals() (ie, watch
    out, it's going to take a while).

    name is the name of the top level object.  It's first bit of the
    'accessor' strings that are returned.  If not specified, defaults
    to 'arg'.
    
    Matches determined by search.  search(needle, name, obj)
    returns true if the object should be considered a match.  By
    default, search matches if needle is a substring of the name of
    the object.

    Return a list of strings showing the path to reach the matching
    object"""
    if haystack is None:
        haystack = globals()
        name = ''
    elif name is None:
        if hasattr(haystack, "__name__"):
            name = haystack.__name__
        else:
            name = 'arg'
    
    if search is None: search = search_name

    return _apropos(needle, haystack, name, search, **kw)

##################################################
## Common search functions

def search_name(needle, name, obj):
    return name and needle in name    

def search_value(needle, name, obj):
    # String representation of dicts, lists, and tuples includes the
    # objects within them, so don't consider that to be a match on the
    # desired value.  Wait to get inside the container class...
    #
    # TODO What I really want to do is match the container if none of
    # its contents matched.
    if type(obj) not in (types.TupleType, types.ListType,
                         types.DictType):
        return needle in str(obj)
# NOTE -- should be repr()?

def search_doc(needle, name, obj):
    return hasattr(obj, '__doc__') and obj.__doc__ \
           and needle in obj.__doc__
    
def search_name_regexp(needle, name, obj):
    return name and re.search(needle, name)

def search_value_regexp(needle, name, obj):
    if type(obj) not in (types.TupleType, types.ListType,
                         types.DictType):
        return re.search(needle, str(obj))

def search_doc_regexp(needle, name, obj):
    return hasattr(obj, '__doc__') \
           and obj.__doc__ \
           and re.search(needle, obj.__doc__)

##################################################
## The guts

def _apropos(needle, haystack, haystack_name,
             search, max_depth=None, **kw):
    """Recursively search through haystack looking for needle.

    haystack can be any python object.  Typically it's a module.  If
    it's not given, it's the dict returned by globals() (ie, watch
    out, it's going to take a while).
    
    Matches determined by search.  search(needle, name, obj)
    returns true if the object should be considered a match.  By
    default, search matches if needle is a substring of the name of
    the object.  

    name is the name of the top level object.  It's first bit of the
    'accessor' strings that are returned.  If not specified, defaults
    to 'arg'.

    Return a list of strings showing the path to reach the matching
    object."""
    def search_internal(haystack, haystack_name, full_name, depth):
        '''Free variable: needle, search_types'''
        # print "Searched", len(searched_ids), "Searching", depth, full_name
        if search(needle, haystack_name, haystack):
            found.append(full_name)

        # break apart if obj is not already searched
        if type(haystack) in search_types \
                and (not max_depth or depth < max_depth) \
                and id(haystack) not in searched_ids:
            # Prevent loops with circular references by setting this
            # _before_ descending into sub-objects
            searched_ids.append(id(haystack))

            for hay, hay_name, hay_access in introspect(haystack, **kw):
                search_internal(hay, hay_name, full_name + hay_access, depth+1)

    searched_ids = []
    found = []
    search_types = dict_types + list_types + instance_types

    search_internal(haystack, haystack_name, haystack_name, 0)
    return found

def introspect(obj, **kw):
    if type(obj) in dict_types:
        return DictIntrospector(obj, **kw)
    if type(obj) in list_types:
        return ListIntrospector(obj, **kw)
    if type(obj) in instance_types:
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
    def __iter__(self):
        return self

    def next(self):
        pass

class NullIntrospector (Introspector):
    def __init__(self, **kw):
        pass

    def next(self):
        raise StopIteration

class DictIntrospector (Introspector):
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
        # getattr(obj, '1')    
        # TODO -- 11filter out non-string things that appear in dir()

        name = self.iter.next()
        while type(name) is not types.StringType \
              or (self.exclude and name.startswith(self.exclude)):
            name = self.iter.next()
        return getattr(self.inst, name), name, "." + name

