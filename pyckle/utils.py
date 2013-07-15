# various private helper functions for pyckle

# for a proper error reporting, one needs to print a line
# and line number - therefor string input is tokenizes
# in order to produce such information
def _split_lines(src):

    import tokenize
    from io import BytesIO
    
    lastline = 0

    ret = list()


    for toktype, tokstring, (srow, scol), (erow, ecol), line in tokenize.tokenize(BytesIO(src.encode('utf-8')).readline):

        if srow != erow:
            raise SyntaxError("srow({}) != erow({}), on line `{}'!, which is not supported".format(srow, erow, line))

        # ignore ENCODING(56) and ENDMARKER(0) tokens
        if toktype in (56, 0):
            continue

        if erow != lastline:
            ret.append(line)
            lastline = erow

    return ret

# split modules and return the tuple
# >>> _split_modules('foo.bar.Baz')
# ('foo.bar', 'foo')
def _split_modules(mod):

    ret = list()
    
    while '.' in mod:
        mod = mod[:mod.rfind('.')]
        ret.append(mod)

    return tuple(ret)


# fix imports - iow adds all undelying modules to globals
# _fix_imports({'foo.Bar' : ...'})
# {'foo.Bar' : ..., 'foo' : ...}
def _fix_imports(globals):

    from importlib import import_module

    keys = list(globals.keys())

    for key in (k for k in keys if '.' in k):
        for mod in _split_modules(key):
            globals[mod] = import_module(mod)

    return globals

# prepare GLOBALS - this differs from python version
def _make_globals():
    
    try:
        #py3
        import builtins
    except ImportError:
        builtins = __builtins__

    import array
    import collections
    import datetime
    import decimal
    import fractions


    ret = { 
        'None'      : None,
        'True'      : True,
        'False'     : False,
    }

    LST = (
        'builtins.bytearray',
        'builtins.complex',
        'builtins.dict',
        'builtins.float',
        'builtins.frozenset',
        'builtins.list',
        'builtins.memoryview',
        'builtins.set',
        'array.array',
        'collections.deque',
        'collections.Counter',
        'collections.ChainMap',
        'collections.OrderedDict',
        'collections.defaultdict',
        'datetime.date',
        'datetime.time',
        'datetime.datetime',
        'datetime.timedelta',
        'datetime.tzinfo',
        'datetime.timezone',
        'decimal.Decimal',
        'fractions.Fraction',
        )

    lc = locals()

    for mod, attr in (x.split('.') for x in LST):
        if not mod in lc:
            continue
        foo = getattr(lc[mod], attr)
        if not foo:
            continue
        if mod == "builtins":
            ret[attr] = foo
        else:
            ret['.'.join((mod, attr))] = foo

    return ret
