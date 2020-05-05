import os
import sys
import tempfile
import subprocess
from numpy import *

def test_evaluate():
    testPath = os.path.dirname(os.path.abspath(__file__))
    binPath = os.path.join(testPath, '..', 'dynakit', 'bin')
    evalPath = os.path.join(binPath, 'evaluate.py')

    N = 1024 * 200
    m = 3
    A = random.rand(N, m)

    expressions = [
        'a0 + a1',
        '(a0 - a1) / 1E-8',
        '1.01 * a0 - a1 * 1E-2 + a2 * 5E-3'
    ]

    results = [
        dot(A, [1, 1, 0]),
        dot(A, [1, -1, 0]) / 1E-8,
        dot(A, [1.01, -1E-2, 5E-3])
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [sys.executable, evalPath, '-o', 'output.dat']
        for i in range(m):
            fname = 'input_{}.dat'.format(i)
            cmd += ['-i', 'a{}'.format(i), fname]
            with open(os.path.join(tmpdir, fname), 'wb') as f:
                f.write(A[:,i].tobytes())

        for expr, ref in zip(expressions, results):
            subprocess.check_call(cmd + ['-e', expr], cwd=tmpdir)
            with open(os.path.join(tmpdir, 'output.dat'.format(i)), 'rb') as f:
                res = frombuffer(f.read())
                assert(abs(res - ref).max() < 1E-12)

if __name__ == '__main__':
    test_evaluate()
