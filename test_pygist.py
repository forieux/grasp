import unittest, tempfile
import local

from pygist import *

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
                         types.TracebackType,]

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
            
def suite():
    suites = [unittest.TestLoader().loadTestsFromTestCase(test)
              for test in (SyntaxTest, IntrospectionTest)]
    return unittest.TestSuite(suites)

def test():
    unittest.TextTestRunner().run(suite())

def itest():
    suite().debug()
