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
   default via ``PyckleVisitor`` instances.
"""

__version__ = '0.1'
__all__ = [
    'dump', 'dumps', 'load', 'loads',
    'Pyckler'
    ]

__author__ = 'Michal Vyskocil'

import ast
import pprint

from .pyckler import Pyckler
from .utils import _split_lines

#json-like API

def loads(string, cls=Pyckler, globals=dict()):
    """Deserialize and evaluate string with a valid
    pyckle document to Python object
    
    Arguments:
    ``string`` - the (unicode) string or string list with a document
    
    Keywords:
    ``cls`` - the visitor class used for evaluation,
    defaults to ``Pyckler``
    
    ``globals`` - an aditional namespace concatenated with a
    ``cls``'s default list """

    if isinstance(string, str):
        slist = _split_lines(string)
    elif isinstance(string, (list, tuple)):
        slist = string
    else:
        raise TypeError("str, list, tuple expected for `string', `{}' found".format(type(string)))
    
    return cls(slist, "<string>", globals).eval()

def load(fp, cls=Pyckler, globals=dict()):
    """Deserialize and evaluate file-like object ``fp``
    with a valid pyckle document to Python object
    
    Arguments:
    ``fp`` - file-like object with ``.readlines()`` method
    
    Keywords:
    ``cls`` - the visitor class used for evaluation,
    defaults to ``Pyckler``
    
    ``globals`` - an aditional namespace concatenated with a
    ``cls``'s default list. """
    return cls(
        fp.readlines(),
        fp.name if hasattr(fp, "name") else "<unknown>",
        globals).eval()

def dumps(obj):
    """Serialize python object ``obj`` to a string and return it
    
    WARNING/TODO: ``dumps`` just checks the object is not
    recursive via ``pprint.isreadable``, but does not
    impose any other limits"""

    if not isreadable(obj):
        raise TypeError("'{}' is not readable".format(obj))

    ret  = StringIO()
    pprint(obj, stream=ret)
    ret.seek(0)
    return ret.read()

def dump(obj, fp):
    """Serialize python object ``obj`` to a file-like
    object ``fp``"""
    return fp.write(dumps(obj))
