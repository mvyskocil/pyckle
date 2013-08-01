# caching support for pyckle
#
# ... based on pickle
#

import os
import errno
import pickle
import tokenize

# python2 compatibility
if hasattr(tokenize, "open"):
    _open = lambda filename: tokenize.open(filename)
else:
    _open = lambda filename: open(filename, 'U')

# python2 compatibility
try:
    from _pickle import UnpicklingError
except ImportError:
    from pickle import UnpicklingError

from pyckle.utils import _cache_path, _wr_llong, _rd_llong, _stat

MAGIC=b'pyckle\x00\x00'

# long long mask
LL_MASK = 0xFFFFFFFFFFFFFFFF

"""
Cache support for pyckle

Those functions are intended to manipulate with a cache. Note that they do have
an ugly API intentionally as they shall be called from main load/dump functions
only.
"""

class CacheMismatchError(IOError):
    pass

def write_cache(obj, filename, cfilename=None):
    """Write cache of pyckle file

    :param obj: The object to write.
    :param filename: The source file name, where obj has been serialized.
    :param cfilename: Target cache-file, default to PEP 3147 location

    :return:  Path to resulting cache file or None if not written

    **WARNING**: note that caller is responsible to use the same ``obj`` than the
                 one serialized in ``file``, otherwise bad things will happen. The
                 content of cfilename is used as is and not checked, so it can contain
                 any arbitrary python code.
    """

    with _open(filename) as fp:
        timestamp, size = _stat(filename, fp)
        size &= LL_MASK

    if cfilename is None:
        cfilename = _cache_path(filename)

    try:
        dirname = os.path.dirname(cfilename)
        if dirname:
            os.makedirs(dirname)
    except OSError as error:
        if error.errno != errno.EEXIST:
            return None
    
    with open(cfilename, 'wb') as fp:
        fp.write(b'\0\0\0\0\0\0\0\0')
        _wr_llong(fp, timestamp)
        _wr_llong(fp, size)
        pickle.dump(obj, fp, protocol=pickle.HIGHEST_PROTOCOL)
        fp.flush()
        fp.seek(0, 0)
        fp.write(MAGIC)
        return cfilename

    return None

def read_cache(filename, cfilename=None):
    """Read a cache of pyckle file

    :param filename: The source file name, where obj has been serialized.
    :param cfilename: Target cache-file, default to PEP 3147 location

    :return: The unpickled object or raises CacheMismatchError if cache
             does not match with a filename

    """

    if cfilename is None:
        cfilename = _cache_path(file)

    with _open(filename) as fp:
        timestamp, size = _stat(filename, fp)
        size &= LL_MASK

    with open(cfilename, 'rb') as fp:
        if fp.read(8) != MAGIC:
            raise CacheMismatchError("unexpected magic")
        ctimestamp = int(_rd_llong(fp))
        csize = _rd_llong(fp)
        if size != csize:
            raise CacheMismatchError("size mismatch")
        if timestamp > ctimestamp:
            raise CacheMismatchError("timestamp mismatch")
        try:
            return pickle.load(fp)
        except UnpicklingError:
            pass
        raise CacheMismatchError("unpickling error")
    raise CacheMismatchError("IOError")
