# various private helper functions for pyckle

# for a proper error reporting, one needs to print a line
# and line number - therefor string input is tokenizes
# in order to produce such information
def _split_lines_impl(src):

    import tokenize

    try:
        from StringIO import StringIO
        tokenize_f = lambda src: tokenize.generate_tokens(StringIO(src).readline)
    except ImportError:
        from io import BytesIO
        tokenize_f = lambda src: tokenize.tokenize(BytesIO(src.encode('utf-8')).readline)
    
    lastline = 0

    ret = list()


    for toktype, tokstring, (srow, scol), (erow, ecol), line in tokenize_f(src):

        if srow != erow:
            raise SyntaxError("srow({}) != erow({}), on line `{}'!, which is not supported".format(srow, erow, line))

        # ignore ENCODING(56) and ENDMARKER(0) tokens
        if toktype in (56, 0):
            continue

        if erow != lastline:
            ret.append(line)
            lastline = erow

    return ret

# adds an error handling on top of _split_lines_impl
def _split_lines(src):


    import tokenize

    try:
        return _split_lines_impl(src)
    except tokenize.TokenError as te:
        raise SyntaxError(
            te.args[0],
            ("<string>",
            te.args[1][0]-1,
            te.args[1][1],
            src)) #from None

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
        pass

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

    BUILTINS = (
        'bytearray',
        'complex',
        'dict',
        'float',
        'frozenset',
        'list',
        'memoryview',
        'set',
        )

    if 'builtins' in locals():
        getattr_f = lambda x : getattr(builtins, x, None)
    elif '__builtins__' in globals():
        getattr_f = lambda x : __builtins__.get(x, None)
    else:
        raise RuntimeError("Cannot locate builtins in your Python implementation")

    # simply update ret by all 'name' : name mappings, which exists in current
    # python implementation
    ret.update({bltn : getattr_f(bltn) for bltn in BUILTINS if getattr_f(bltn) is not None})
        
    OTHERS = (
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

    for mod, attr in (x.split('.') for x in OTHERS):
        if not mod in lc:
            continue
        foo = getattr(lc[mod], attr, None)
        if foo is None:
            continue
        ret['.'.join((mod, attr))] = foo

    return ret
