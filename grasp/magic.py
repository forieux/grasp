import types
import IPython
import grasp

# deepreloads of IPython cause a crash, so add it to the list of
# excludes for deep reloads
dreload_excludes = ['sys', 'os.path', '__builtin__', '__main__', 'IPython']

##############################
## Provide IPython magic commands
@IPython.core.magic.magics_class
class AproposMagics(IPython.core.magic.Magics):
    """Magic functions for all of the various apropos possibilities."""
    def fetch_or_eval(self, str, nss=tuple()):
        """Try to fetch a name from a namespace.  If that fails, evaluate the
        object.  The order of precedence is: 1) name in the user
        namespace, 2) name in the namespaces given in nss, a list of
        namespaces, searched in order, 3) eval in the user's
        namespace.

        """
        # This is completely equivalent to just calling eval in the
        # appropriate namespace.  If the arg is a name, it will be
        # fetched from the namespace.  However, it makes me feel funny
        # to use eval that way when there's a perfectly good way to
        # just fetch the object by name.
        if str in self.shell.user_ns:
            return self.shell.user_ns[str]
        else:
            for ns in nss:
                # Ugh, allow nss to be a module
                if type(ns) is types.ModuleType:
                    if hasattr(ns, str):
                        return getattr(ns, str)
                else:
                    if str in ns:
                        return ns[str]
        return eval(str, self.shell.user_ns)

    def parse_apropos_args(self, line):
        """Parse arguments for all of the apropos* functions"""
        # Possible args I'm ignoring for now:
        # haystack_name, name
        # 
        # Using mode='list' here makes it easier to be independent of
        # extraneous whitespace.
        opts, arg_strings = self.parse_options(line, 'd:s:e', mode='list')
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
            kw['search'] = self.fetch_or_eval(opts['s'], [grasp])

        # Would like to allow evaluation of the first arg (the needle)
        # as well as the second arg (the haystack).  However, it's
        # hard to see how to do this in a general way with nice
        # syntax.  The possibilities I see are: 
        # 
        # 1) require quoting so that getopt can split it.  This breaks
        # the illusion that you're just typing at a normal python
        # prompt.  
        #
        # 2) Require the whole string to evaluate to a tuple that's
        # passed as args to apropos.  This is ok, commas come between
        # args anyway. However, the metaphor with magic commands is
        # more like the unix shell, where args are separated by
        # spaces, not commas.  
        # 
        # 3) Specify that the first arg be a string and do not allow
        # evaluation of it.  Since the code implementing the search
        # (grasp.apropos) expects it to be a string, this is "honest"
        # to the underlying implmentation.  
        #
        # 4) Specify a keyword separator between them, like 'in', so
        # that calls look like the following: 
        # %apropos name
        # %apropos name in IPython
        # %apvalue 1.1 in IPython
        # %apropos name in [IPython, matplotlib]
        # %apvalue 1.1 in [IPython, matplotlib]
        # 
        # The problem with #4 this is that in could concievably appear
        # in the code to evaluate, being as it is a reserved word in
        # Python.  However, this seems unlikely, and if it does I can
        # either a) ask the user to disambiguate with quotes (then I
        # have to pass it to getopts?) or b) try evaling all
        # possibilities, catching syntax exceptions.  The latter seems
        # a bit reckless.
        # 
        # Actually, it's a bit of an advantage that in is a reserved
        # word, because then the user can't have variables named in
        # that would lead to ambiguous statements like "%apropos name
        # in in" 
        #
        # So, go with #4, asking the user to disambiguate if
        # necessary.  find index of keyword separating needle from
        # haystack
        #
        # However, after implementing this, I find that I have an
        # ambiguity if needle is just a literal string.  Do I evaluate
        # it or not?  I could try to evaluate it and catch exceptions,
        # just giving it as a literal string there are exceptions.
        # That seems clumsy, too.
        #
        # So now I'm leaning toward: 
        #
        # 5) Force it to be a string.  Force it to be quoted if it has
        # spaces.  Allow it to be evaluated with a switch.  I think
        # this is fully unambiguous, and doens't need the 'in'
        # keyword.
        # 
        # arg will hold the positional args of apropos
        arg = [None, None]
        if 'e' in opts:
            arg[0] = self.fetch_or_eval(arg_strings[0])
        else:
            arg[0] = arg_strings[0]

        if len(arg_strings)==1: 
            # The user didn't provide something to search.  Calling
            # globals() here or in grasp.py doesn't make sense, so
            # send in the user's namespace for haystack            
            arg[1] = self.shell.user_ns                
        else:
            # User provided both needle and haystack
            # This may be an expression and therefore may have spaces
            # in it, so join them up into one string before evaling.
            arg[1] = self.fetch_or_eval(' '.join(arg_strings[1:]))

        return arg, kw
    
    @IPython.core.magic.line_magic
    def apropos(self, line):
        """%apropos [-d <max_depth>] [-s <search_function>] <needle> [haystack]

        Search for things related to "needle."  Return a list of
        matching names.

        haystack is an optional argument giving the object in which to
        search.  It can be the name of an object in the user's
        namespace or a literal object that is passed to eval

        -s <search_function> : Give the name of a function that takes
        areguments f(needle, name, obj) where needle is the string
        we're looking for, name is the name of the present object, and
        obj is the present object.  The function returns True if the
        object should be considered a match, False otherwise.  The
        argument to the magic function can be the name of a function
        in the user's namespace, the name of a function in the grasp
        module's namespace (e.g. search_name or search_value, but
        there are already other magic functions defined for those
        possibilities) or an expression that is evaluated (i.e. a
        lambda expression)

        -d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        return grasp.apropos(*aa, **kw)

    @IPython.core.magic.line_magic
    def apname(self, line):
        """%apname [-d <max_depth>] <needle> [haystack]

        Search for objects with the string "needle" in their name.
        Return a list of matching names.

        haystack is an optional argument giving the object in which to
        search.  It can be the name of an object in the user's
        namespace or a literal object that is passed to eval

        -d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        return grasp.apropos_name(*aa, **kw)

    @IPython.core.magic.line_magic
    def apname_regex(self, line):
        """%apname_regex [-d <max_depth>] <needle> [haystack]

        Search for objects whose name matches regex "needle".  Return
        a list of matching names.

        haystack is an optional argument giving the object in which to
        search.  It can be the name of an object in the user's
        namespace or a literal object that is passed to eval

        -d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        return grasp.apropos_name_regexp(*aa, **kw)

    @IPython.core.magic.line_magic
    def apvalue(self, line):
        """%apvalue [-d <max_depth>] <needle> [haystack]

        Search for objects whose string representation contains
        "needle".  Return a list of matching names.

        haystack is an optional argument giving the object in which to
        search.  It can be the name of an object in the user's
        namespace or a literal object that is passed to eval

        -d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        return grasp.apropos_value(*aa, **kw)

    @IPython.core.magic.line_magic
    def apvalue_regex(self, line):
        """%apvalue_regex [-d <max_depth>] <needle> [haystack]

        Search for objects whose value matches regex "needle".  Return
        a list of matching names.

        haystack is an optional argument giving the object in which to
        search.  It can be the name of an object in the user's
        namespace or a literal object that is passed to eval

        -d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        return grasp.apropos_value_regexp(*aa, **kw)

    @IPython.core.magic.line_magic
    def apdoc(self, line):
        """%apdoc [-d <max_depth>] <needle> [haystack]

        Search for objects whose docstring contains "needle".  Return
        a list of matching names.

        haystack is an optional argument giving the object in which to
        search.  It can be the name of an object in the user's
        namespace or a literal object that is passed to eval

        -d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        return grasp.apropos_doc(*aa, **kw)

    @IPython.core.magic.line_magic
    def apdoc_regex(self, line):
        """%apdoc_regex [-d <max_depth>] <needle> [haystack]

        Search for objects whose docstring matches regex "needle".
        Return a list of matching names.

        haystack is an optional argument giving the object in which to
        search.  It can be the name of an object in the user's
        namespace or a literal object that is passed to eval

        -d <max_depth> : search at most max_depth levels

        """
        aa, kw = self.parse_apropos_args(line)
        return grasp.apropos_doc_regexp(*aa, **kw)

@IPython.core.magic.magics_class
class IntrospectionMagics(IPython.core.magic.Magics):
    """Magic functions related to object introspection"""

    @IPython.core.magic.line_magic
    def gist(self, line):
        """%gist object

        Get the 'gist' (overview) of the given object.  Object can be
        the name of an object in the user's namespace or a literal
        object to be passed to eval().

        Return a dictionary where the keys are names of types and the
        values are lists of objects of that type in the object.

        -v : Verbose output.  Include attributes with a leading underscore.

        In [1]: %gist (1,2,3)
        Out[1]: {builtin_function_or_method: [count, index]}

        In [2]: %gist numpy.array([1,2,3])
        Out[2]: {buffer: [data],
                    int: [itemsize, nbytes, ndim, size],
                    builtin_function_or_method: [all, any, argmax]
                    tuple: [shape, strides],
                    ndarray: [T, imag, real]}

        """
        # Also recognize this argument, but don't see why people will
        # want it for the magic command, so don't advertise it:
        # -u : 'ugly' output with standard strings (lots of extra quotes)
        opts, arg = self.parse_options(line, 'vu')
        if arg in self.shell.user_ns:
            obj = self.shell.user_ns[arg]
        else:
            obj = eval(arg, self.shell.user_ns)
        return grasp.gist(obj, 
                          verbose='v' in opts, 
                          pretty='u' not in opts)

    @IPython.core.magic.line_magic
    def rtype(self, line):
        """%rtype object 

        Recursive type of object.  Return a list of strings concisely
        describing the object.

        The most interesting thing about this is that when all the
        objects in a container class have the same rtype, rtype will
        concisely summarize this face.  So instead of telling you that
        (1,2,3) is a 'tuple of int, int, int', it will tell you it's a
        'tuple of 3 int'.  This criterion is applied recursively, so
        if an object is a list of 10 tuples of 3 dicts, rtype will
        tell you as much.

        -m <int> : Maximum size of container objects break apart for inspection.

        In [1]: %rtype 1
        Out[1]: 'int'

        In [2]: %rtype (1, 1.1, 2)
        Out[2]: ['tuple of', 'int', 'float', 'int']

        In [3]: %rtype (1, 2, 3)
        Out[3]: 'tuple of 3 int'

        In [4]: %rtype ([1,2], [3,4], [5,6])
        Out[4]: ['tuple of 3', 'list of 2 int']

        In [5]: %rtype (numpy.array([1,2]), numpy.array([3,4]), numpy.array([5,6]))
        Out[5]: ['tuple of 3', 'ndarray of (2,) int64']

        """
        opts, arg = self.parse_options(line, 'm:')
        kw = {}
        if 'm' in opts: 
            kw['max'] = int(opts['m'])
        # if it's not in the user namespace, assume it's a literal object
        if arg in self.shell.user_ns:
            obj = self.shell.user_ns[arg]
        else:
            obj = eval(arg, self.shell.user_ns)
        return grasp.recursive_type(obj, **kw)

@IPython.core.magic.magics_class
class ReloadMagics(IPython.core.magic.Magics):
    @IPython.core.magic.line_magic
    def dreload(self, line):
        """%dreload module"

        Deep reload of module.  The main utility of this is to add
        IPython to the list of excludes for deepreloading, since it
        crashes for me when that happens.  A second advantage of using
        this magic function is that it checks to see if the name
        exists in the user's namespace, and, if not, imports the
        module before dreloading it.  Thus one doesn't type dreload
        module, get a traceback because it's not loading in the
        present namespace, import module, then dreload module
        again.

        """
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
