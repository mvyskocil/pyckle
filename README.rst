******
Pyckle
******

``pyckle`` aims to be for Python, what is JSON for Javascript - a
**serialization format**.

As Python is much fancier than JS, pyckle does
support more than JSON. And is batterry-included so all types likes ``sets``,
``lists``, ``tuples``, or ``complex`` numbers as well as interesting classes
from Python standard library, like ``collections.dequeue`` or
``decimal.Decimal`` are supported by default

====
FAQ
====

**Q**: Why to define a new format and not to use any of existing ones?

**A**: This is not a new format. This is Python!

**Q**: What 'This is Python!' answer means?

**A**:

1. It is not new format, just subset of Python
2. It aims to be safe(r) for evaluation than Python eval
3. as well as more flexible/extensible then `ast.literal_eval`
4. And it is powerfull like Python itself

**Q**: Why to not use JSON

**A**: JSON is very limited, where pyckle supports about most of Python's fancy
types like sets, or even Decimals. Or does support more powerfull dictionaries,
with any "pyckealbe" type, and not just strings. So if portability between
languages is not an issue, pyckle is definitelly superior format.

   see `<https://github.com/jsonpickle/jsonpickle/issues/5#issuecomment-1393109>`_

**Q**: Talk is cheap, just show me your code

**A**: np

 .. code-block:: python

>>> import pyckle
>>> string = '{(1, "2") : [1+2j, set((1, 2, 3))]}'
>>> obj = pyckle.loads(string)
>>> print(obj)
{(1, '2'): [(1+2j), {1, 2, 3}]}

**Q**: Well, can't I just use eval?

**A**: You can - in fact pyckle does use eval too, It just checks the AST tree

 .. code-block:: python

>>> import pyckle
>>> string = '[i for i in range(4294967296)]'
>>> obj = eval(string)
# now you have 4G of integers
>>> obj = pyckle.loads(string)
File "<string>", line 1
  [i for i in range(4294967296)]
   ^
SyntaxError: Unsupported type of node: 'ListComp'

====
TODO
====

 * use better serialization than ``pprint``
   - provide full names by default (``mod.submod.Class``)
   - with an ability to limit the types using globals
 * add caching
 * support comments inside documents - for writting (?)
