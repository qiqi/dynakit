#!/usr/bin/python3

import argparse
import subprocess
from numpy import *

'''
evaluates an operation and stores the result in output

Example: compute difference between two similar states:
evaluate.py -e "(a1 - a0) / 1E-8" \
            -i a1 init_perturb_0000/final.dat \
            -i a0 unperturbed/final.dat \
            -o qr/diff_0000.dat
'''

import ast
import operator as op

# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}

def eval_expr(expr, variables):
    """
    >>> eval_expr('2^6')
    4
    >>> eval_expr('2**6')
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
    -5.0
    """
    return eval_(ast.parse(expr, mode='eval').body, variables)

def eval_(node, variables):
    if isinstance(node, ast.Num): # <number>
        return node.n
    elif isinstance(node, ast.Name): # <variable>
        return variables[node.id]
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        return operators[type(node.op)](eval_(node.left, variables),
                                        eval_(node.right, variables))
    elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_(node.operand, variables))
    else:
        raise TypeError(node)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expression', '-e', type=str, required=True,
                        help='''Expression to evaluate''')
    parser.add_argument('--input', '-i', type=str, required=True, nargs=2,
                        action='append',
                        help='''Output state, a binary file of doubles''')
    parser.add_argument('--output', '-o', type=str, required=True,
                        help='''Output state, a binary file of doubles''')
    parser.add_argument('--bufferMB', '-b', type=int, default=8,
                        help='''Buffer size for each input/output in MB''')
    args = parser.parse_args()

    bufSize = args.bufferMB * 1024 * 128
    inputs = dict(args.input)
    fpInputs = {}
    for varname, fname in inputs.items():
        fpInputs[varname] = open(fname, 'rb')

    fpOutput = open(args.output, 'wb')

    while True:
        variables = {}
        for varname, fpIn in fpInputs.items():
            variables[varname] = frombuffer(fpIn.read(bufSize), double)

        varSize = set()
        for v in variables.values():
            varSize.add(v.size)
        assert(len(varSize) == 1)
        if min(varSize) > 0:
            result = eval_expr(args.expression, variables)
            fpOutput.write(result.tobytes())
        else:
            break
