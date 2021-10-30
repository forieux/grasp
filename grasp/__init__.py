from .grasp import *

# Fail gracefully if IPython not installed or if old version.
try:
    from .magic import load_ipython_extension, unload_ipython_extension
except (ImportError, SyntaxError):
    pass
