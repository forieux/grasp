import IPython
import grasp

##############################
## Provide IPython magic commands
@IPython.core.magic.magics_class
class AproposMagics(IPython.core.magic.Magics):

    def parse_apropos_args(self, line):
        # Args I'm ignoring for now:
        # haystack_name
        # name
        opts, arg = self.parse_options(line, 'd:s:', mode='list')
        kw = {}
        if 'd' in opts: 
            kw['max_depth'] = int(opts['d'])

        # It's only legel to provide a search function to apropos(),
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
        aa, kw = self.parse_apropos_args(line)
        return grasp.apropos(*aa, **kw)

    @IPython.core.magic.line_magic
    def apname(self, line):
        aa, kw = self.parse_apropos_args(line)
        return grasp.apropos_name(*aa, **kw)

    @IPython.core.magic.line_magic
    def apname_regex(line):
        aa, kw = self.parse_apropos_args(line)
        grasp.apropos_name_regexp(*aa, **kw)

    @IPython.core.magic.line_magic
    def apvalue(line):
        aa, kw = self.parse_apropos_args(line)
        grasp.apropos_value(*aa, **kw)

    @IPython.core.magic.line_magic
    def apvalue_regex(line):
        aa, kw = self.parse_apropos_args(line)
        grasp.apropos_value_regexp(*aa, **kw)

    @IPython.core.magic.line_magic
    def apdoc(line):
        aa, kw = self.parse_apropos_args(line)
        grasp.apropos_doc(*aa, **kw)

    @IPython.core.magic.line_magic
    def apdoc_regex(line):
        aa, kw = self.parse_apropos_args(line)
        grasp.apropos_doc_regexp(*aa, **kw)

@IPython.core.magic.magics_class
class IntrospectionMagics(IPython.core.magic.Magics):
    @IPython.core.magic.line_magic
    def gist(self, line):
        """Get the gist of the given object.  -v => include attributes with a
leading underscore.  -u => 'ugly' output with standard strings (lots
of extra quotes)"""
        opts, arg = self.parse_options(line, 'vu')
        return grasp.gist(self.shell.user_ns[arg], 
                          verbose='v' in opts, 
                          pretty='u' not in opts)

    @IPython.core.magic.line_magic
    def rtype(self, line):
        """Recursive type of object.  -m <int> => max length of
array/tuple/list to inspect."""
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
