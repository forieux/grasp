from distutils.core import setup

setup(
    name='grasp',
    version='0.3.0dev',
    license='LICENSE',
    author='Greg Novak',
    author_email='greg.novak@gmail.com',
    packages=['grasp', 'grasp.test'],
    # url='http://pypi.python.org/pypi/grasp/',
    description='Useful introspection tools.',
    long_description=open('README').read(),
)
