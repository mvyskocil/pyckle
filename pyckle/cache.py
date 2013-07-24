# caching support for pyckle
#
# ... based on pickle
#

import errno
import imp
import os
import pickle
import tokenize

from py_compile import wr_long

from . import load

MAGIC=b'pyckle\x00\x00'

def cache_path(filename):

    if hasattr(imp, "cache_from_source"):
        return imp.cache_from_source(filename) + "kle.cache"
    else:
        return fullname + ".cache"

def write_cache(file, cfile=None, _obj=None):
    """Write cache of pyckle file

    :param file: The source file name.
    :param cfile: Target cache-file, default to PEP 3147 location
    :param _obj: The object to write, default None

    :return:  Path to resulting cache file
    """

    with tokenize.open(file) as f:
        try:
            st = os.fstat(f.fileno())
        except AttributeError:
            st = os.stat(file)
        timestamp = int(st.st_mtime)
        size = st.st_size & 0xFFFFFFFF
        if _obj is None:
            _obj = load(f)

    if cfile is None:
        cfile = cache_path(filename)

    try:
        dirname = os.path.dirname(cfile)
        if dirname:
            os.makedirs(dirname)
    except OSError as error:
        if error.errno != errno.EEXIST:
            return None
    
    with open(cfile, 'wb') as fp:
        fp.write(b'\0\0\0\0\0\0\0\0')
        wr_long(fp, timestamp)
        wr_long(fp, size)
        pickle.dump(_obj, fp, protocol=pickle.HIGHEST_PROTOCOL)
        fp.flush()
        fp.seek(0, 0)
        fp.write(MAGIC)
        return cfile

    return None

