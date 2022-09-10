from typing import Iterator, Optional, cast
from typing_extensions import assert_never
from parsival import parse
from eqn import AndExpr, Equation, Expr, GroupedExpr, NotExpr, OrExpr, Value, Variable

def eval_expr(expr: Expr, values: dict[str, bool]) -> bool:
    """Evaluate the expression with the given variable values."""
    if isinstance(expr, Value):
        return expr.value
    if isinstance(expr, Variable):
        return values[expr.name]
    if isinstance(expr, GroupedExpr):
        return eval_expr(expr.expr, values)
    if isinstance(expr, NotExpr):
        return not eval_expr(expr.atom, values)
    if isinstance(expr, AndExpr):
        return all(eval_expr(operand, values) for operand in expr.operands)
    if isinstance(expr, OrExpr):
        return any(eval_expr(operand, values) for operand in expr.operands)
    assert_never(expr)

def get_variables(expr: Expr) -> Iterator[str]:
    """Yield all variables present in the expression."""
    if isinstance(expr, Value):
        return
    elif isinstance(expr, Variable):
        yield expr.name
    elif isinstance(expr, GroupedExpr):
        yield from get_variables(expr.expr)
    elif isinstance(expr, NotExpr):
        yield from get_variables(expr.atom)
    elif isinstance(expr, (AndExpr, OrExpr)):
        for operand in expr.operands:
            yield from get_variables(operand)
    else:
        assert_never(expr)

def verify(eqn: Equation, verbose: bool = True) -> Optional[dict[str, bool]]:
    """Return the values that falsify the identity, or None if verified.

    Verification is done by perfect induction (i.e. brute force).
    """
    variables = list(set(get_variables(eqn.lhs)) | set(get_variables(eqn.rhs)))
    variables.sort()
    max_len = max(map(len, variables))
    for bitset in range(1 << len(variables)):
        values = {
            var: bool(bitset & (1 << i))
            for i, var in enumerate(variables)
        }
        if verbose:
            print('Trying:')
            print('\n'.join(f'{var.rjust(max_len)} = {value}'
                            for var, value in values.items()))
        lhs = eval_expr(eqn.lhs, values)
        rhs = eval_expr(eqn.rhs, values)
        if verbose:
            print(f'-----------\nLHS = {lhs}\nRHS = {rhs}')
        if lhs == rhs:
            if verbose:
                print('Success.\n')
            continue
        if verbose:
            print('Failure!')
        return values
    if verbose:
        print('The equation is an identity.')
    return None

if __name__ == '__main__':
    verify(cast(Equation, parse(input(), Equation)))
