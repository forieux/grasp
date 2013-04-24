import sys
from distutils.core import setup

args = dict(name='grasp',
            version='0.3.1',
            license='Creative Commons CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
            author='Greg Novak',
            author_email='greg.novak@gmail.com',
            packages=['grasp', 'grasp.test'],
            # http://launchpad.net/grasp
            url='http://pypi.python.org/pypi/grasp/',
            description='Useful introspection tools.',
            long_description=open('README').read(),
            )

# On Python 3, we need distribute (new setuptools) to do the 2to3 conversion
if sys.version_info >= (3,):
    from setuptools import setup
    args['use_2to3'] = True

setup(**args)
