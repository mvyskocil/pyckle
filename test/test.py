import unittest
import time
import random
import timeit

import os
from copy import copy
from tempfile import NamedTemporaryFile

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from pyckle import Pyckler, loads, load, dumps, dump
from pyckle.cache import CacheMismatchError, write_cache, read_cache

VALID_TEST_CASES = (
    '42',
    '-6',
    '0x42',
    '0o42',
    '0.42',
    '3+0j',
    '3.2+0.5j',
    '3.2-6.5j',
    '6.5j-4',
    '-1-.42j',
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
    
UNSUPPORTED_TEST_CASES =  (
    ('not True',
        ("Unsupported unary operator, only negative numbers are allowed",
         "<string>", 1, 1, "not True")),
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

class TestLoad(unittest.TestCase):

    def setUp(self):

        self._globals = Pyckler('', '').globals


    def testValidLoad(self):

        for string in VALID_TEST_CASES:

            ret = loads(string)
            exp = eval(string, copy(self._globals))

            self.assertEqual(ret, exp)

            fp = StringIO(string)
            self.assertEqual(ret, load(fp))

    def testUnsupportedLoad(self):
        
        for string, (msg, filename, lineno, offset, text) in UNSUPPORTED_TEST_CASES:

            try:
                ret = loads(string)
            except SyntaxError as se:
                self.assertTupleEqual(
                (se.msg, se.filename, se.lineno, se.offset, se.text),
                (msg,    filename,    lineno,    offset,    text))
            else:
                self.fail("``{}'' is expected to raise an exception".format(string))
            
            try:
                ret = load(StringIO(string))
            except SyntaxError as se:
                self.assertTupleEqual(
                (se.msg, se.filename, se.lineno, se.offset, se.text),
                (msg,    "<unknown>",    lineno,    offset,    text))
            else:
                self.fail("``{}'' is expected to raise an exception".format(string))

    def testInvalidSyntax(self):

        se1, se2, se3 = None, None, None

        source="{foo:42"

        try:
            ret = loads(source)
        except SyntaxError as se:
            se1 = se
        else:
            self.fail("SyntaxError expected for ``{}''".format(source))
        
        try:
            ret = eval(source)
        except SyntaxError as se:
            se2 = se
        else:
            self.fail("SyntaxError expected for ``{}''".format(source))
        
        try:
            ret = load(StringIO(source))
        except SyntaxError as se:
            se3 = se
        else:
            self.fail("SyntaxError expected for ``{}''".format(source))

class TestDump(unittest.TestCase):

    def testDump(self):

        for string in VALID_TEST_CASES:

            if 'fractions' in string:
                continue

            obj = loads(string)
            string2 = dumps(obj)
            io = StringIO()
            dump(obj, io)
            io.seek(0)
            string3 = io.read()
            del io

            # XXX: have no idea how to test that without explicitly mention results
            # so lets evaluate that again and compare string -> load1 -> dump -> load2
            self.assertEqual(obj, loads(string2))
            self.assertEqual(obj, loads(string3))

class TestCache(unittest.TestCase):

    def setUp(self):
        mod = __import__("fractions")
        klass = getattr(mod, "Fraction")
        self.obj = {(1, 2) : klass(1, 2)}

    def testWriteLoadCache(self):

        pyckle = NamedTemporaryFile(mode='w+t')
        dump(self.obj, pyckle.file)
        pyckle.file.flush()

        cache = NamedTemporaryFile()
        write_cache(self.obj, pyckle.name, cache.name)

        self.assertNotEqual(0, os.fstat(cache.file.fileno()).st_size)

        obj2 = read_cache(pyckle.name, cache.name)

        self.assertIsNotNone(obj2)
        self.assertEqual(self.obj, obj2)

    def testWriteCacheWithNoFilename(self):
        
        with self.assertRaises(FileNotFoundError):
            write_cache(None, '')
    
    def testWriteCacheWithNotReadableFile(self):
        
        with self.assertRaises(PermissionError):
            write_cache(None, '/root/.bashrc')
    
    def testWriteCacheWithCustomCFile(self):
        
        foo = NamedTemporaryFile(mode='w+t')
        dump(self.obj, foo)

        cache = NamedTemporaryFile(mode='w+b')
        
        write_cache(self.obj, foo.name, cfilename=cache.name)

        obj2 = read_cache(foo.name, cache.name)
        self.assertIsNotNone(obj2)
        self.assertEqual(self.obj, obj2)
    
    def testWriteCacheWithInaccessbileCFile(self):
        
        foo = NamedTemporaryFile(mode='w+t')
        dump(self.obj, foo)

        cache = NamedTemporaryFile(mode='w+b')
        os.chmod(cache.name, 0o000)
        
        with self.assertRaises(PermissionError):
            write_cache(self.obj, foo.name, cfilename=cache.name)

        with self.assertRaisesRegex(PermissionError, "Permission denied"):
            obj2 = read_cache(foo.name, cache.name)
            self.assertIsNone(obj2)
    
    def testWriteCacheWithInaccessbileFile(self):
        
        foo = NamedTemporaryFile(mode='w+t')
        dump(self.obj, foo)

        cache = NamedTemporaryFile(mode='w+b')
        os.chmod(foo.name, 0o000)
        
        with self.assertRaises(PermissionError):
            write_cache(self.obj, foo.name, cfilename=cache.name)

        obj2 = None
        with self.assertRaises(PermissionError):
            obj2 = read_cache(foo.name, cache.name)
        
        os.chmod(foo.name, 0o644)
        foo.close()

        self.assertIsNone(obj2)

    def testWriteOnDiskFull(self):

        foo = NamedTemporaryFile(mode='w+t')
        dump(self.obj, foo)

        #FIXME: there is a ResourceWarning on unclosed '/dev/full'
        # have no idea why as I do use with open: every time
        # BTW: it does not happen when running the same code
        #      outside unittest
        # probably related to CPython, see my old issue about /dev/full
        # http://bugs.python.org/issue10815
        with self.assertRaises(OSError):
            write_cache(self.obj, foo.name, '/dev/full')

    def testReadOutdattedCacheFile(self):

        preobj = complex(1, 2)
        pstobj = complex(2, 1)
        foo = NamedTemporaryFile(mode='wt')
        dump(preobj, foo)
        #FIXME: this shall be called by dump
        foo.flush()
        foo.seek(0, 0)

        st1 = os.fstat(foo.fileno())
        cache = NamedTemporaryFile(mode='wb')
        write_cache(preobj, foo.name, cache.name)

        time.sleep(1.01)

        dump(pstobj, foo)
        #FIXME: likewise
        foo.flush()
        st2 = os.fstat(foo.fileno())

        with self.assertRaisesRegex(CacheMismatchError, "timestamp mismatch"):
            ret = read_cache(foo.name, cache.name)
            self.assertIsNone(ret)

    def testReadDifferentCacheFileSize(self):

        preobj = complex(1, 2)
        pstobj = complex(42, 1)
        foo = NamedTemporaryFile(mode='wt')
        dump(preobj, foo)
        #FIXME: this shall be called by dump
        foo.flush()
        foo.seek(0, 0)

        st1 = os.fstat(foo.fileno())
        cache = NamedTemporaryFile(mode='wb')
        write_cache(preobj, foo.name, cache.name)

        dump(pstobj, foo)
        #FIXME: likewise
        foo.flush()
        st2 = os.fstat(foo.fileno())

        with self.assertRaisesRegex(CacheMismatchError, "size mismatch"):
            ret = read_cache(foo.name, cache.name)
            self.assertIsNone(ret)

class TestCacheWithNiceAPI(unittest.TestCase):
    
    def setUp(self):
        mod = __import__("fractions")
        klass = getattr(mod, "Fraction")
        self.obj = {(1, 2) : klass(1, 2)}
    
    def testWriteLoadCache(self):

        pyckle = NamedTemporaryFile(mode='w+t')
        cache = NamedTemporaryFile()
        dump(self.obj, pyckle, use_cache=True, cfilename=cache.name)

        self.assertNotEqual(0, os.fstat(cache.file.fileno()).st_size)

        obj2 = load(pyckle, use_cache=True, cfilename=cache.name)

        self.assertIsNotNone(obj2)
        self.assertEqual(self.obj, obj2)

    #skipped the rest of tests as they are done in TestCache

    def testCacheSpeed(self):
        """
        This is very indirect way how to test cache,
        however quite logical

        Code measure the speed of calling uncached load
        versus cached one. The speedub should be factor 50
        at least, but it'll be bigger for larger objects

        """
        
        # number of attempts
        N = 40
        # how much faster is to use cache
        SPEEDUP_FACTOR = 50

        bigobj = {k:v for k, v in enumerate(random.randrange(1024) for i in range(32*1024))}

        uncached = NamedTemporaryFile(mode='w+t')
        dump(bigobj, uncached, use_cache=False)

        cached = NamedTemporaryFile(mode='w+t')
        cachee = NamedTemporaryFile(mode='wb')
        dump(bigobj, cached, use_cache=True, cfilename=cachee.name)

        #uncached.seek(0,0)
        #cached.seek(0,0)
        #cachee.seek(0,0)


        def luc():
            uncached.seek(0,0)
            load(uncached)
        ret1 = timeit.timeit(luc, "gc.enable()", number=N)
        def lca():
            cachee.seek(0,0)
            load(cached, "gc.enable()", use_cache=True, cfilename=cachee.name)
        ret2 = timeit.timeit(lca, number=N)

        self.assertGreater(ret1, ret2)
        self.assertGreater(ret1 // ret2, SPEEDUP_FACTOR)


if __name__ == '__main__':
    unittest.main()
