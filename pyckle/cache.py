# caching support for pyckle
#
# ... based on pickle
#

import os
import errno
import pickle
import tokenize

from _pickle import UnpicklingError

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

def write_cache(obj, filename, cfilename=None):
    """Write cache of pyckle file

    :param obj: The object to write.
    :param file: The source file name, where obj has been serialized.
    :param cfile: Target cache-file, default to PEP 3147 location

    :return:  Path to resulting cache file or None if not written

    **WARNING**: note that caller is responsible to use the same ``obj`` than the
                 one serialized in ``file``, otherwise bad things will happen. The
                 content of cfile is used as is and not checked, so it can contain
                 any arbitrary python code.
    """

    with tokenize.open(filename) as fp:
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

def load_cache(filename, cfilename=None):

    if cfilename is None:
        cfilename = _cache_path(file)

    with tokenize.open(filename) as fp:
        timestamp, size = _stat(filename, fp)
        size &= LL_MASK

    try:
        with open(cfilename, 'rb') as fp:
            if fp.read(8) != MAGIC:
                return None
            ctimestamp = int(rd_llong(fp))
            csize = rd_llong(fp)
            if size != csize or timestamp > ctimestamp:
                return None
            try:
                return pickle.load(fp)
            except UnpicklingError:
                return None
    except IOError:
        return None

    assert False, "Can't get here!"
