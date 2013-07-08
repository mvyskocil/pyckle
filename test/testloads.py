import unittest
import collections

from pyckle import PyckleVisitor, loads

class TestLoads(unittest.TestCase):

    def setUp(self):

        self._valid_test_cases = (
    '42',
    '0x42',
    '0o42',
    '0.42',
    '3+0j',
    '3.2+0.5j',
    '3.2-6.5j',
    '6.5j-4',
    '"some-string"',
    'b"some-bytes"',
    'r"some-raw-string"',
    'True',
    'False',
    'None',
    '("the", "tuple")',
    '["the", "list"]',
    '{"the" : "dict"}',
    '{"the", "set"}',
    'set(("the", "set"))',
    'frozenset(("the", "frozenset"))',
    'dict(a=11, b=12)',
    'complex(2, 2)',)
    
        self._invalid_test_cases = (
    '1 + 2 (without j)',
    "'a' + 'b'",
    '(1, 2) + (3, 4)',
    '''foo bar'.split(" ")''',
    'Counter("abcdefghaa")',
    'foo = 42',
    'x = lambda x',
    'sorted((1, 2, 3), key=lambda x: x)',
    'def foo(): return 42',
    'class Foo(): pass',
    '(i for i in range(11))',
    '[i for i in range(11)]',
    '{i:i+1 for i in range(11)}')

#   'collections.Counter("abcdefghaa")')
    def testLoads(self):

        gl = PyckleVisitor.__GLOBALS__
        
        for string in self._valid_test_cases:

            ret = loads(string)
            exp = eval(string, gl)

            self.assertEqual(ret, exp)

    def testLoads2(self):

        gl = PyckleVisitor.__GLOBALS__

        for string in self._invalid_test_cases:
    
            try:
                ret = loads(string)
            except SyntaxError as se:
                #TODO: we should check the message
                pass
            else:
                self.fail("``{}'' should raise SyntaxError")

if __name__ == '__main__':
    unittest.main()
