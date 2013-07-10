# Pyckle

pyckle aims to be for Python, what is JSON for Javascript
serialization format. but as Python is much fancier than JS,
pyckle does support more than JSON. And is batterry-included
so all interesting classes from Python standard library, like
collections.dequeue or decimal.Decimal are supported by default

## mini-FAQ
Q: Why to define a new format and not to use existing?
A: This is Python!

Q: What 'This is Python!' answer means?
A: 1.) It is not new format, just subset of Python
   2.) It aims to be safe(r) for evaluation than Python eval
   3.) as well as more flexible then `ast.literal_eval`
   3.) And it is powerfull like Python itself

Q: Why to not use JSON
A: JSON is very limited, where pyckle supports about most of Python's fancy
   types like sets, or even Decimals. Or does support more powerfull dictionaries,
   with any "pyckealbe" type, and not just strings. So if portability between
   languages is not an issue, pyckle is definitelly superior format.

   https://github.com/jsonpickle/jsonpickle/issues/5#issuecomment-1393109

## TODO
* support modules properly
* remove the recursive calls of self.visit and use ast.walk instead
* enhance tests - catch tokenize exceptions on invalid string syntax
* add caching
* use better serialization than pprint
* support comments inside documents - for writting (?)

### SyntaxError.__init__

SyntaxError(
    msg,
    (   filename,
        lineno,
        offset,
        line
    ))

