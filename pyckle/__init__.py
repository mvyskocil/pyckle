# Copyright (c) 2013 Michal Vyskocil
#
# pyckle module for python, released under MIT license
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""module pyckle: native serialization format for python

   pyckle aims to be for Python, what is JSON for Javascript
   native serialization format. 
   
   As Python is much fancier than JS, pyckle does support
   more than JSON. And is batterry-included so all
   interesting classes from Python standard library, like
   collections.dequeue or decimal.Decimal are supported by
   default via ``Pyckler`` instances.

Classes:

   Pyckler

Functions:

   dump(object, file)
   dumps(object) -> string
   load(file) -> object
   loads(string) -> object

Misc variables:

    __version__
    __author__

"""

__author__ = 'Michal Vyskocil'
__version__ = '1.0'

__all__ = [
    'dump', 'dumps', 'load', 'loads',
    'Pyckler'
    ]

from pprint import _safe_repr

from .cache import CacheMismatchError, read_cache, write_cache
from .pyckler import Pyckler
from .utils import _split_lines

#json-like API

def loads(string, cls=Pyckler, globals=dict()):
    """Deserialize and evaluate string with a valid
    pyckle document to Python object
    
    :param string: The (unicode) string or string list with a document
    :param cls: The visitor class used for evaluation, defaults to Pyckler_
    :param globals: An aditional namespace concatenated with a
        ``cls``'s default list
    """

    if isinstance(string, str):
        slist = _split_lines(string)
    elif isinstance(string, (list, tuple)):
        slist = string
    else:
        raise TypeError("str, list, tuple expected for `string', `{}' found".format(type(string)))
    
    return cls(slist, "<string>", globals).eval()

def load(fp, cls=Pyckler, globals=dict(), use_cache=False, cfilename=None):
    """Deserialize and evaluate file-like object
    containing a valid pyckle document to Python object
    
    :param fp: The file-like object with ``.readlines()`` method
    :param cls: The visitor class used for evaluation, defaults to ``Pyckler``
    :param globals: An aditional namespace concatenated with a
        ``cls``'s default list
    """

    if use_cache and hasattr(fp, "name"):
        try:
            return read_cache(fp.name, cfilename)
        except CacheMismatchError:
            pass

    return cls(
        fp.readlines(),
        fp.name if hasattr(fp, "name") else "<unknown>",
        globals).eval()

def dumps(obj):
    """Return serialized python object as a string

    :param obj: The python object to be serialized

    :return: serialized object as a string
    
    WARNING/TODO: ``dumps`` just checks the object is not
    recursive via ``pprint.isreadable``, but does not
    impose any other limits"""

    repr_string, isreadable, isrecursive = \
        _safe_repr(obj, {}, None, 0)

    if not isreadable:
        raise TypeError("'{}' is not readable".format(obj))

    return repr_string

def dump(obj, fp, use_cache=False, cfilename=None):
    """Serialize python object to a file stream
    
    :param obj: The python object to be serialized
    :param fp: The file-like object with ``.write()`` method
    
    :return: what underlying ``.write()`` method returns,
    mostly number of written bytes
    """

    ret = fp.write(dumps(obj))
    fp.flush()
    if use_cache and hasattr(fp, "name"):
        write_cache(obj, fp.name, cfilename)
    return ret
