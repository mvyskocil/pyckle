#
#   setup file for pyckle
#

from distutils.core import setup

setup(name=b'pyckle',
    version=b'1.0',
    description=b'Native serialization for Python',
    url=b'https://github.com/mvyskocil/pyckle',
    author=b'Michal Vyskocil',
    author_email=b'michal.vyskocil@gmail.com',
    license=b'MIT',
    packages=[b'pyckle',],
    long_description=b'''Pyckle is for Python the same as JSON for Javascript,
    the serialization format. It aims to bypass the JSON's limitations, like
    the poor set of builtin objects. So it does support all fancy python
    builtin datatypes like sets or complex numbers as well as few usefull types
    from standard library like fractions.Fraction.'''
    )

