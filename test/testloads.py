import unittest

from copy import copy

from pyckle import Pyckler, loads

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
    'complex(2, 2)',
    'fractions.Fraction(22,7)',)
    
        self._unsupported_test_cases = (
    ('1 + 2',
        ("Illegal expression, only complex numbers are allowed",
         "<string>", 1, 1, "1 + 2")),
    ("'a' + 'b'",
        ("Illegal expression, only complex numbers are allowed",
         "<string>", 1, 1, "'a' + 'b'")),
    ("(1, 2) + (3, 4)",
        ("Illegal expression, only complex numbers are allowed",
         "<string>", 1, 1, "(1, 2) + (3, 4)")),
    ('''"foo bar".split(" ")''',
        ("Only names are supported in attributes, found 'Str'",
         "<string>", 1, 1, '''"foo bar".split(" ")''')),
    ('Counter("abcdefghaa")',
        ("'Counter' is not allowed name",
         "<string>", 1, 1, 'Counter("abcdefghaa")')),
    ('set((lambda x:42, ))',
        ("Unsupported type of node: 'Lambda'",
         "<string>", 1, 6, "set((lambda x:42, ))")),
    ('foo = 42',
        ("invalid syntax",
         "<string>", 1, 5, 'foo = 42')),
    ('def foo(): return 42',
        ("invalid syntax",
         "<string>", 1, 3, 'def foo(): return 42')),
    ('class Foo(): pass',
        ("invalid syntax",
         "<string>", 1, 5, 'class Foo(): pass')),
    ('(i for i in range(11))',
        ("Unsupported type of node: 'GeneratorExp'",
         "<string>", 1, 2, '(i for i in range(11))')),
    ('[i for i in range(11)]',
        ("Unsupported type of node: 'ListComp'",
         "<string>", 1, 2, '[i for i in range(11)]')),
    ('{i:i+1 for i in range(11)}',
        ("Unsupported type of node: 'DictComp'",
         "<string>", 1, 2, '{i:i+1 for i in range(11)}')),
    ('{i for i in range(11)}',
        ("Unsupported type of node: 'SetComp'",
         "<string>", 1, 2, '{i for i in range(11)}')),
    ('fractions.gcd(1, 2)',
        ("'fractions.gcd' is not allowed name",
         "<string>", 1, 1, 'fractions.gcd(1, 2)')),
        )

        self._globals = Pyckler('', '').globals


    def testValidLoads(self):

        for string in self._valid_test_cases:

            ret = loads(string)
            exp = eval(string, copy(self._globals))

            self.assertEqual(ret, exp)

    def testUnsupportedLoads(self):
        
        for string, (msg, filename, lineno, offset, text) in self._unsupported_test_cases:

            try:
                ret = loads(string)
            except SyntaxError as se:
                self.assertTupleEqual(
                (se.msg, se.filename, se.lineno, se.offset, se.text),
                (msg,    filename,    lineno,    offset,    text))
            else:
                self.fail("``{}'' is expected to raise an exception".format(string))

    def testInvalidSyntax(self):

        se1, se2 = None, None

        source="{foo:42"

        try:
            ret = loads(source)
        except SyntaxError as se:
            se1 = se
        else:
            self.fail("SyntaxError expected")
        
        try:
            ret = eval(source)
        except SyntaxError as se:
            se2 = se
        else:
            self.fail("SyntaxError expected")


if __name__ == '__main__':
    unittest.main()
