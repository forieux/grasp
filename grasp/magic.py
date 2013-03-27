import IPython
import grasp

##############################
## Provide IPython magic commands
@IPython.core.magic.magics_class
class AproposMagics(IPython.core.magic.Magics):
    """Magic functions for all of the various apropos possibilities."""
    def parse_apropos_args(self, line):
        """Parse arguments for all of the apropos* functions"""
        # Possible args I'm ignoring for now:
        # haystack_name, name
        opts, arg = self.parse_options(line, 'd:s:', mode='list')
        kw = {}
        if 'd' in opts: 
            kw['max_depth'] = int(opts['d'])

        # It's only legel to provide a search function to apropos(),
        # but parse the option here to keep things centralized.  The
        # possibility isn't mentioned in the docstrings where it's not
        # allowed, and the code will fail, complaining that the search
        # keyword arg was provided twice if the user gives a search
        # function anyway.
        if 's' in opts:
            # search is either the name of a function in the user's
            # namespace, the name of a function in this module's
            # namepsace, or else an anonymous function.
            in_user_ns = (opts['s'] in self.shell.user_ns 
                          and callable(self.shell.user_ns[opts['s']]))
            in_module_ns = (opts['s'] in globals()
                            and callable(globals()[opts['s']]))
            if in_user_ns and in_module_ns:
                print """Found search functions in user namespace and module namespace.
Using the one from the user's namespace."""
            if in_user_ns:
                kw['search'] = self.shell.user_ns[opts['s']]
            elif in_module_ns:
                kw['search'] = globals()[opts['s']]
            else:
                kw['search'] = eval(opts['s'])
            
        # this is the thing in which to search.  Look for an object in
        # the user's namespace, if not, assume it's a literal object
        # and evaluate it.
        if len(arg) == 2:
            if arg[1] in self.shell.user_ns:
                arg[1] = self.shell.user_ns[arg[1]]
            else:
                arg[1] = eval(arg[1])
        return arg, kw
    
    @IPython.core.magic.line_magic
    def apropos(self, line):
        """%apname [-d <max_depth>] [-s <search_function>] <needle> [haystack]

Search for things related to "needle."  Return a list of matching names.

haystack is an optional argument giving the object in which to search.
It can be the name of an object in the user's namespace or a literal
object that is passed to eval

-s <search_function> : Give the name of a function that takes
   areguments f(needle, name, obj) where needle is the string we're
   looking for, name is the name of the present object, and obj is the
   present object.  The function returns True if the object should be
   considered a match, False otherwise.  The argument to the magic
   function can be the name of a function in the user's namespace, the
   name of a function in the grasp module's namespace
   (e.g. search_name or search_value, but there are already other
   magic functions defined for those possibilities) or an expression
   that is evaluated (i.e. a lambda expression)

-d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        return grasp.apropos(*aa, **kw)

    @IPython.core.magic.line_magic
    def apname(self, line):
        """%apname [-d <max_depth>] <needle> [haystack]

Search for objects with the string "needle" in their name.  Return a
list of matching names.

haystack is an optional argument giving the object in which to search.
It can be the name of an object in the user's namespace or a literal
object that is passed to eval

-d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        return grasp.apropos_name(*aa, **kw)

    @IPython.core.magic.line_magic
    def apname_regex(line):
        """%apname_regex [-d <max_depth>] <needle> [haystack]

Search for objects whose name matches regex "needle".  Return a list
of matching names.

haystack is an optional argument giving the object in which to search.
It can be the name of an object in the user's namespace or a literal
object that is passed to eval

-d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        grasp.apropos_name_regexp(*aa, **kw)

    @IPython.core.magic.line_magic
    def apvalue(line):
        """%apvalue [-d <max_depth>] <needle> [haystack]

Search for objects whose string representation contains "needle".
Return a list of matching names.

haystack is an optional argument giving the object in which to search.
It can be the name of an object in the user's namespace or a literal
object that is passed to eval

-d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        grasp.apropos_value(*aa, **kw)

    @IPython.core.magic.line_magic
    def apvalue_regex(line):
        """%apvalue_regex [-d <max_depth>] <needle> [haystack]

Search for objects whose value matches regex "needle".  Return a list
of matching names.

haystack is an optional argument giving the object in which to search.
It can be the name of an object in the user's namespace or a literal
object that is passed to eval

-d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        grasp.apropos_value_regexp(*aa, **kw)

    @IPython.core.magic.line_magic
    def apdoc(line):
        """%apdoc [-d <max_depth>] <needle> [haystack]

Search for objects whose docstring contains "needle".  Return a list
of matching names.

haystack is an optional argument giving the object in which to search.
It can be the name of an object in the user's namespace or a literal
object that is passed to eval

-d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        grasp.apropos_doc(*aa, **kw)

    @IPython.core.magic.line_magic
    def apdoc_regex(line):
        """%apdoc_regex [-d <max_depth>] <needle> [haystack]

Search for objects whose docstring matches regex "needle".  Return a
list of matching names.

haystack is an optional argument giving the object in which to search.
It can be the name of an object in the user's namespace or a literal
object that is passed to eval

-d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        grasp.apropos_doc_regexp(*aa, **kw)

@IPython.core.magic.magics_class
class IntrospectionMagics(IPython.core.magic.Magics):
    """Magic functions related to object introspection"""

    @IPython.core.magic.line_magic
    def gist(self, line):
        """%gist object

Get the 'gist' (overview) of the given object.  Object can be the name
of an object in the user's namespace or a literal object to be passed
to eval().

Return a dictionary where the keys are names of types and the values
are lists of objects of that type in the object.  

-v : Verbose output.  Include attributes with a leading underscore.

%gist (1,2,3)
Out: {builtin_function_or_method: [count, index]}

%gist numpy.array([1,2,3])
Out: {buffer: [data],
      int: [itemsize, nbytes, ndim, size],
      builtin_function_or_method: [all, any, argmax]
      tuple: [shape, strides],
      ndarray: [T, imag, real]}
        """
        # Also recognize this argument, but don't see why people will
        # want it for the magic command, so don't advertise it:
        # -u : 'ugly' output with standard strings (lots of extra quotes)
        opts, arg = self.parse_options(line, 'vu')
        return grasp.gist(self.shell.user_ns[arg], 
                          verbose='v' in opts, 
                          pretty='u' not in opts)

    @IPython.core.magic.line_magic
    def rtype(self, line):
        """%rtype object 

Recursive type of object.  Return a list of strings concisely
describing the object.  

The most interesting thing about this is that when all the objects in
a container class have the same rtype, rtype will concisely summarize
this face.  So instead of telling you that (1,2,3) is a 'tuple of int,
int, int', it will tell you it's a 'tuple of 3 int'.  This criterion
is applied recursively, so if an object is a list of 10 tuples of 3
dicts, rtype will tell you as much.

-m <int> : Maximum size of container objects break apart for inspection.

%rtype 1
Out: 'int'

%rtype (1, 1.1, 2)
Out: ['tuple of', 'int', 'float', 'int']

%rtype (1, 2, 3)
Out: 'tuple of 3 int'

%rtype ([1,2], [3,4], [5,6])
Out: ['tuple of 3', 'list of 2 int']

%rtype (numpy.array([1,2]), numpy.array([3,4]), numpy.array([5,6]))
Out: ['tuple of 3', 'ndarray of (2,) int64']
        """
        opts, arg = self.parse_options(line, 'm:')
        kw = {}
        if 'm' in opts: 
            kw['max'] = int(opts['m'])
        # if it's not in the user namespace, assume it's a literal object
        if arg in self.shell.user_ns:
            obj = self.shell.user_ns[arg]
        else:
            obj = eval(line)            
        return grasp.recursive_type(obj, **kw)

# deepreloads of IPython cause a crash, so add it to the list of
# excludes for deep reloads
dreload_excludes = ['sys', 'os.path', '__builtin__', '__main__', 'IPython']

@IPython.core.magic.magics_class
class ReloadMagics(IPython.core.magic.Magics):
    @IPython.core.magic.line_magic
    def dreload(self, line):
        """%dreload module"

Deep reload of module.  The main utility of this is to add IPython to
the list of excludes for deepreloading, since it crashes for me when
that happens.  A second advantage of using this magic function is that
it checks to see if the name exists in the user's namespace, and, if
not, imports the module before dreloading it.  Thus one doesn't type
dreload module, get a traceback because it's not loading in the
present namespace, import module, then dreload module again."""
        # If the given name doesn't exist in the user namespace, try
        # importing it.
        if not line in self.shell.user_ns:
            mod = __import__(line)
            self.shell.user_ns[line] = mod
        # this is now known to be in the user ns, so reload away.
        dreload(self.shell.user_ns[line], dreload_excludes)

# Load the magic commands into ipython            
ip = get_ipython()
ip.register_magics(IntrospectionMagics)
ip.register_magics(AproposMagics)
ip.register_magics(ReloadMagics)
