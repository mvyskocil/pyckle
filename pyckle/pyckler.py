##
##  Copyright (c) 2013 Michal Vyskocil
##
##  released under MIT License, see LICENSE
##

import ast
import _ast

from copy import copy
from io import StringIO
from itertools import chain
from collections import defaultdict
from pprint import pprint, isreadable

from .utils import _fix_imports, _make_globals

class PycklerBase():

    __GLOBALS__ = {}

    def __init__(self, source, filename, globals=dict(), fix_imports=True):

        assert source is not isinstance(source, str), "ERROR: source must be a list or tuple of strings"

        self._source = source
        self._filename = filename
        self._globals = copy(self.__GLOBALS__)
        self._globals.update(globals)
        if fix_imports:
            self._globals = _fix_imports(self._globals)

    @property
    def globals(self):
        return copy(self._globals)

    def visit(self, node):

        def visitor(node):
            method = 'visit_' + node.__class__.__name__
            visitor_f = getattr(self, method, self.generic_visit)
            return visitor_f(node)

        visitor(node)
        for n in ast.walk(node):
            visitor(n)

    def parse(self):
        
        node = ast.parse(''.join(self._source), self._filename, mode="eval")
        self.visit(node)
        return node

    def eval(self):

        node = self.parse()
        code = compile(node, self._filename, mode="eval")
        return eval(code, self.globals)

    ### visit meths
    def visit_Expression(self, node):
        #self.visit(node.body)
        return

    def visit_Num(self, node):
        return

    def visit_Str(self, node):
        return

    def visit_Bytes(self, node):
        return

    def visit_BinOp(self, node):
        if  isinstance(node.left, _ast.Num) and \
            isinstance(node.op, (_ast.Add, _ast.Sub)) and \
            isinstance(node.right, _ast.Num) and \
            (isinstance(node.left.n, complex) or isinstance(node.right.n, complex)):
                return

        raise SyntaxError(
            "Illegal expression, only complex numbers are allowed",
            self._seargs(node)
            )

    def visit_Name(self, node):
        if node.id in self._globals:
            return
        raise SyntaxError(
            "'{}' is not allowed name".format(node.id),
            self._seargs(node)
            )

    def visit_Tuple(self, node):
        return

    def visit_List(self, node):
        return
    
    def visit_Set(self, node):
        return

    def visit_Dict(self, node):
        return

    def visit_Call(self, node):
        if  node.starargs is not None or \
            node.kwargs is not None:
            raise NotImplementedError("starargs or kwargs support is not implemented in visit_Call")

        return

    def visit_Attribute(self, node):
        n = node
        l = list()
        while isinstance(n, _ast.Attribute):

            if not isinstance(n.value, _ast.Name):
                raise SyntaxError(
                    "Only names are supported in attributes, found '{}'".format(n.value.__class__.__name__),
                    self._seargs(node)
                    )

            l.append(n.value.id)
            n = n.attr
        l.append(n)

        s = '.'.join(l)

        if s in self._globals:
            return

        raise SyntaxError(
            "'{}' is not allowed name".format(s),
            self._seargs(node)
            )

    #XXX: for ctx=Load() - no idea, what's this about
    def visit_Load(self, node):
        return

    # handled in visit_BinOp
    def visit_Add(self, node):
        return
    def visit_Sub(self, node):
        return

    # foo(bar=42)
    def visit_keyword(self, node):
        return

    def generic_visit(self, node):
        raise SyntaxError(
            "Unsupported type of node: '{}'".format(node.__class__.__name__),
            self._seargs(node)
            )

    ### private methods

    # prepare arguments for SyntaxError in a safe way
    def _seargs(self, node):

        #assert hasattr(node, "lineno"), "node.lineno is expected for node {}".format(node)
        if not hasattr(node, "lineno"):
            import pdb; pdb.set_trace()

        offset = node.col_offset + 1 if hasattr(node, "col_offset") else 0
        try:
            line = self._source[node.lineno-1]
        except IndexError:
            line = "<N/A>"

        return  self._filename, \
                node.lineno,    \
                offset,         \
                line


class Pyckler(PycklerBase):

    __GLOBALS__ = _make_globals()
