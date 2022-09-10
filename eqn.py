from __future__ import annotations
from typing import Literal, Annotated, Union, Optional
from dataclasses import dataclass, InitVar
from parsival import Commit
from parsival.helper_rules import *

class Value:
    num: Regex[str, r"""[01]"""]

    def __init__(self, num: str) -> None:
        self.value: bool = bool(int(num))

@dataclass
class Variable:
    name: Regex[str, r"""[a-z](_?[0-9]+|'*)"""]

@dataclass
class GroupedExpr:
    _item_1: InitVar[Literal['(']]
    _item_2: InitVar[Commit]
    expr: Expr
    _item_4: InitVar[Literal[')']]

Atom = Union[GroupedExpr, Variable, Value]

@dataclass
class NotExpr:
    _item_1: InitVar[Regex[str, r"""[~!]"""]]
    _item_2: InitVar[Commit]
    atom: Atom

MaybeNot = Union[NotExpr, Atom]

@dataclass
class AndExpr:
    operands: Annotated[list[MaybeNot], "+", Regex[str, r"""[*&]?"""]]

@dataclass
class OrExpr:
    operands: Annotated[list[AndExpr], "+", Regex[str, r"""[+|]"""]]

Expr = Union[OrExpr, AndExpr, MaybeNot]

@dataclass
class Equation:
    lhs: Expr
    _item_2: InitVar[Literal['=']]
    rhs: Expr

if __name__ == '__main__':
    import sys
    import parsival

    text = sys.stdin.read()

    try:
        from prettyprinter import pprint, install_extras
    except ImportError:
        from pprint import pprint
    else:
        install_extras(include=frozenset({'dataclasses'}))

    try:
        parsival.DEBUG = '--debug' in sys.argv
        pprint(parsival.parse(text, Equation))
    except (SyntaxError, parsival.Failed) as exc:
        print('Failed:', str(exc)[:50], file=sys.stderr)
