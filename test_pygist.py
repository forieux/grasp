## Find appropriate unittest module
import unittest
if not hasattr(unittest, 'skipIf'):
    try: 
        import unittest2 as unittest        
    except ImportError:
        raise NotImplementedError, \
            """Tests require either the Python 2.7 or later version of unittest or
            the unittest2 module."""

import tempfile
from pygist import *

## Make it easy to skip long-running tests.  
## 0 = tests instantaneous
## 1 = test takes longer than 10 sec
## 2 = test takes longer than 1 min
## 3 = test takes longer than I'm willing to wait
patience = 1

class SyntaxTest(unittest.TestCase):

    def testSstr(self):
        s = sstr("one")
        self.assertEqual(s.__str__(), "one")
        self.assertEqual(s.__repr__(), "one")
        
class IntrospectionTest(unittest.TestCase):
    def setUp(self):
        self.tf = tempfile.TemporaryFile()

        def func(x): return x
        class testNewObj (object):
            def method(self): pass
        class testOldObj: 
            def method(self): pass

        # self.objs is a list of an example of each type of object
        # that I'm interested in handling in my introspection
        # routines.  self.excludes is a list of types that I don't
        # handle, so that I can detect when new types are added to
        # Python
        
        self.excludes = [types.BufferType, types.CodeType,
                         types.DictProxyType, types.EllipsisType,
                         types.FrameType, types.GeneratorType,
                         types.GetSetDescriptorType,
                         types.MemberDescriptorType,
                         types.NotImplementedType,
                         types.TracebackType,
                         # Not sure why this isn't showing up under exceptions

                         GeneratorExit,
                         # TODO -- do these belong here?
                         bytearray, memoryview]

        # These are the ones in types module
        self.objs = [True, # Boolean,
                     repr, # built-in function
                     1j, # Complex
                     types.ClassType('foo', (object,), {}), # Class
                     dict(a=1), # Dictionary
                     self.tf,    # File
                     1.1,  # Float
                     func, # function
                     testNewObj(), # New style instance
                     testOldObj(), # Old style instance
                     1, # Int
                     lambda x: x, # Lambda 
                     [1, 2], # List
                     1L, # Long 
                     testNewObj().method, # Method
                     testOldObj().method,                
                     unittest, # Module
                     None, # None
                     object(), # Object
                     types.SliceType(1),  # Slice
                     'blah', # String
                     (1,2),  # Tuple
                     int, # type
                     testNewObj.method,   # Unbound Method -- unbound and bound
                     testOldObj.method,   # methods actually the same type w/
                                          # different names in types module
                     u'blah', # unicode
                     xrange(3), # xrange
                     ]

        # These I found in __builtins__
        self.objs += [super(testNewObj),  # Super
                      staticmethod(func), # staticmethod                
                      classmethod(func), # classmethod
                      property(),
                      set([1,2,3]),    # set
                      frozenset([1,2,3]), # frozenset
                      reversed([1,2,3]), # reversed
                      enumerate([1,2,3]), # enumerate
                      Exception(),  # Exception                 
                      KeyboardInterrupt(),  
                      SystemExit(),  
                      BaseException(),  
                      ]

        # These I found in __builtins__ but can't be instantiated
        self.excludes += [basestring]

    def tearDown(self):
        self.tf.close()
        
    def testRtype(self):
        rtype(self.objs)

        # These should not be strings
        self.assertTrue(type( rtype((1,2,3.0))) is list)
        self.assertTrue(type( rtype([1,2,3.0])) is list)
        self.assertTrue(type( rtype(dict(a=1, b=2, c=3.0))) is list)
        self.assertTrue(type( rtype(set((1,2,3.0)))) is list)
        self.assertTrue(type( rtype(frozenset((1,2,3.0)))) is list)

        # These should be strings
        self.assertTrue(type( rtype((1,2,3))) is str)
        self.assertTrue(type( rtype([1,2,3])) is str)
        self.assertTrue(type( rtype(dict(a=1, b=2, c=3))) is str)
        self.assertTrue(type( rtype(set((1,2,3)))) is str)
        self.assertTrue(type( rtype(frozenset((1,2,3)))) is str)

        # If the regular substructure is recognized, these should have
        # length 2
        self.assertEqual(len( rtype(((1,2), (3,4))) ), 2)
        self.assertEqual(len( rtype([(1,2), (3,4)]) ), 2)
        self.assertEqual(len( rtype(dict(a=(1,2), b=(3,4))) ), 2)
        self.assertEqual(len( rtype(set(((1,2),(3,4)))) ), 2)
        self.assertEqual(len( rtype(frozenset(((1,2),(3,4)))) ), 2)

        # If the regular substructure is recognized, these should have
        # length 2
        self.assertEqual(len( rtype([[1,2], [3,4]]) ), 2)
        self.assertEqual(len( rtype([dict(a=1,b=2), dict(c=3,d=4)]) ), 2)
        self.assertEqual(len( rtype([set((1,2)), set((3,4))]) ), 2)
        self.assertEqual(len( rtype([frozenset((1,2)), frozenset((3,4))]) ), 2)

    def testRtypeArrays(self):
        self.assertTrue(type( rtype(numpy.array([1,2]))) is str)
        self.assertTrue(type( rtype([numpy.array([1,2]), numpy.array([1,2])])) is list)
        
        a = numpy.zeros(2, dtype=object)
        a[:] = (1,2), (3,4)
        # recognized substructure => length 2, not 3
        self.assertEqual(len(rtype(a)), 2)
    
    def testTypeCoverage(self):        
        # Check to see if any types aren't covered        
        coveredTypes = self.excludes + [type(obj) for obj in self.objs]
        els = __builtins__.values() \
              + [getattr(types, name) for name in dir(types)] 
        allTypes = [el for el in els if type(el) is type]

        isCovered = [t in coveredTypes
                     # don't bother explicitly listing all exceptions
                     or issubclass(t, Exception)
                     # TODO -- something weird is going on with class types
                     or t is types.ClassType
                     # TODO -- strange -- reversed is in the list of objects
                     or t is reversed
                     for t in allTypes]
        self.assertTrue(every(isCovered))

    def testGist(self):
        for el in self.objs:
            gist(el, verbose=True)

class AproposTest(unittest.TestCase):
    # Untested functions, but I think it's ok that way:
    # _apropos  apropos

    # @unittest.skipIf(test_cfg.patience < 1, "Not patient enough.")
    def testAproposName(self):
        
        class Composite:
            def __init__(self):
                self.a = 1
                self.foo = 'bar'
                self.b = 3
        self.assertEqual(aproposName('foo', [1,'foo',2]),
                         [])
        self.assertEqual(aproposName('foo', (1,'foo',3)),
                         [])
        self.assertEqual(aproposName('foo', dict(a=1,foo='bar',b=3)),
                         ['arg[foo]'])
        self.assertEqual(aproposName('foo', Composite()),
                         ['arg.foo'])

        lst = aproposName('aproposName', aproposModule, exclude='_')
        self.assertTrue('apropos.aproposName' in lst)
        self.assertTrue('apropos.aproposNameRegexp' in lst)
        self.assertFalse('apropos.__builtins__[_ip].user_ns[aproposName]'
                         in lst)

        self.assertEqual(aproposName('foo', Composite(), name='name'),
                         ['name.foo'])

    def testMaxDepth(self):
        lst = aproposName('foo', dict(foo=dict(foo=1, bar=2), b=3),
                          maxDepth=0)
        self.assertFalse('arg][foo][foo]' in lst)
        self.assertFalse('arg][foo]' in lst)

        lst = aproposName('foo', dict(foo=dict(foo=1, bar=2), b=3),
                          maxDepth=1)
        self.assertFalse('arg[foo][foo]' in lst)
        self.assertTrue('arg[foo]' in lst)

        lst = aproposName('foo', dict(foo=dict(foo=1, bar=2), b=3),
                          maxDepth=2)
        self.assertTrue('arg[foo][foo]' in lst)
        self.assertTrue('arg[foo]' in lst)

        lst = aproposName('foo', dict(foo=dict(foo=1, bar=2), b=3))
        self.assertTrue('arg[foo][foo]' in lst)
        self.assertTrue('arg[foo]' in lst)

    # Sometimes causes bus error?
    # @unittest.skipIf(test_cfg.patience < 1, "Not patient enough.")
    def testModuleSearch(self):
        # Sequester the long-running test.
        lst = aproposName('aproposName', aproposModule)
        self.assertTrue('apropos.aproposName' in lst)
        self.assertTrue('apropos.aproposNameRegexp' in lst)
        self.assertTrue('apropos.__builtins__[_ip].user_ns[aproposName]'
                        in lst)

    def testSyntax(self):
        """Functionality has been tested... just make sure that these
        functions can be called"""
        class Composite:
            def __init__(self, str):
                self.__doc__ = str

        self.assertEqual(aproposValue('foo', dict(a=1, bar='foo')),
                         ['arg[bar]'])
        self.assertEqual(aproposDoc('foo', Composite('foo')),
                         ['arg'])
        self.assertEqual(aproposNameRegexp ('^foo', dict(foo=1, barfoo=2)),
                         ['arg[foo]'])
        self.assertEqual(aproposValueRegexp ('^foo', dict(bar='foo',
                                                          the='afoo')),
                         ['arg[bar]'])
        self.assertEqual(aproposDocRegexp ('^foo', Composite('foo')),
                         ['arg'])
        self.assertEqual(aproposDocRegexp ('^foo', Composite('theFoo')),
                         [])
            
    def testNullIntrospector(self):
        i = NullIntrospector()
        # I think this is how this is supposed to work
        self.assertEqual(id(i), id(i.__iter__()))
        self.assertRaises(StopIteration, i.next)

        # make sure code doens't freak out
        i = NullIntrospector(exclude='_')

    def testListIntrospector(self):
        i = ListIntrospector([1,2])
        self.assertEqual(id(i), id(i.__iter__()))
        self.assertEqual(i.next(), (1, None, '[0]'))
        self.assertEqual(i.next(), (2, None, '[1]'))
        self.assertRaises(StopIteration, i.next)

        # make sure code doens't freak out
        i = ListIntrospector([1,2], exclude='_')

    def testInstanceIntrospector(self):
        class Composite:
            pass

        c = Composite()
        c.a = 1
        c.b = 2

        lst = [el for el in InstanceIntrospector(c)]
        # depending on how I'm running the test, one or the other of
        # these should be in the list
        self.assertTrue(('test_apropos', '__module__', '.__module__') in lst
                        or ('__builtin__', '__module__', '.__module__') in lst)
        self.assertTrue((None, '__doc__', '.__doc__') in lst)
        self.assertTrue((1, 'a', '.a') in lst)
        self.assertTrue((2, 'b', '.b') in lst)
        self.assertEqual(len(lst), 4)

        lst = [el for el in InstanceIntrospector(c, exclude='_')]
        self.assertFalse(() in lst)
        self.assertFalse((None, None, '.__doc__') in lst)
        self.assertEqual(len(lst), 2)

    def testDictIntrospector(self):
        lst = [el for el in DictIntrospector(dict(a=1,_b=2))]

        self.assertEqual(len(lst), 2)
        self.assertTrue((1, 'a', '[a]') in lst)
        self.assertTrue((2, '_b', '[_b]') in lst)

        lst = [el for el in DictIntrospector(dict(a=1,_b=2), exclude='_')]
        self.assertEqual(len(lst), 1)
        self.assertTrue((1, 'a', '[a]') in lst)
        self.assertFalse((2, '_b', '[_b]') in lst)            

    def testSearchName(self):
        self.assertTrue(searchName('needle', 'the needle', None))
        self.assertTrue(searchName('needle', 'needle more', None))
        self.assertTrue(searchName('needle', 'the needle more', None))

        # Make sure function doesn't freak out for no name
        self.assertFalse(searchName('needle', None, None))
        
    def testSearchValue(self):
        class Composite:
            def __init__(self, str):
                self._str = str
            def __repr__(self):
                return self._str
            def __str__(self):
                return self._str
            
        self.assertTrue(searchValue('needle', None,
                                    Composite('the needle')))
        self.assertTrue(searchValue('needle', None,
                                    Composite('needle more')))
        self.assertTrue(searchValue('needle', None,
                                    Composite('the needle more')))
        # These are not true because searchValue doens't split
        # apart built-in containers
        self.assertFalse(searchValue('needle', None,
                                    ['needle', 2, 3]))
        self.assertFalse(searchValue('needle', None,
                                    ('needle', 2, 3)))
        self.assertFalse(searchValue('needle', None,
                                    dict(a='needle', b=2, c=3)))

        
    def testSearchDoc(self):   
        class Composite:
            def __init__(self, str):
                self.__doc__ = str

        self.assertTrue(searchDoc('needle', None,
                                  Composite('the needle')))
        self.assertTrue(searchDoc('needle', None,
                                  Composite('needle more')))
        self.assertTrue(searchDoc('needle', None,
                                  Composite('the needle more')))

        # Make sure search fn doesn't freak out
        self.assertFalse(searchDoc('needle', None,
                                   Composite(None)))

        
    def testSearchNameRegexp(self):  
        self.assertFalse(searchNameRegexp('^needle', 'the needle', None))
        self.assertTrue(searchNameRegexp('^needle', 'needle more', None))
        self.assertFalse(searchNameRegexp('^needle', 'the needle more', None))

        # Make sure function doesn't freak out for no name
        self.assertFalse(searchName('^needle', None, None))

    def testSearchValueRegexp(self): 
        class Composite:
            def __init__(self, str):
                self._str = str
            def __repr__(self):
                return self._str
            def __str__(self):
                return self._str
            
        self.assertFalse(searchValueRegexp('^needle', None,
                                           Composite('the needle')))
        self.assertTrue(searchValueRegexp('^needle', None,
                                          Composite('needle more')))
        self.assertFalse(searchValueRegexp('^needle', None,
                                           Composite('the needle more')))

        # Make sure we don't search inside containers
        self.assertFalse(searchValueRegexp('needle', None,
                                           ['needle', 2, 3]))
        self.assertFalse(searchValueRegexp('needle', None,
                                           ('needle', 2, 3)))
        self.assertFalse(searchValueRegexp('needle', None,
                                           dict(a='needle', b=2, c=3)))

    def testSearchDocRegexp(self):   
        class Composite:
            def __init__(self, str):
                self.__doc__ = str

        self.assertFalse(searchDocRegexp('^needle', None,
                                         Composite('the needle')))
        self.assertTrue(searchDocRegexp('^needle', None,
                                        Composite('needle more')))
        self.assertFalse(searchDocRegexp('^needle', None,
                                         Composite('the needle more')))

        # Make sure function doesn't freak out if no doc
        self.assertFalse(searchDocRegexp('^needle', None,
                                         Composite(None)))

def test():
    suite = unittest.defaultTestLoader.loadTestsFromName(__file__[:-3])
    unittest.TextTestRunner().run(suite)

if type(__builtins__) is type({}):
    names = __builtins__.keys()
else:
    names = dir(__builtins__)

if __name__ == '__main__' and '__IPYTHON__' not in names:
    test()
            
