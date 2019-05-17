import os
import sys
import tempfile
import subprocess
from numpy import *

testPath = os.path.dirname(os.path.abspath(__file__))
binPath = os.path.join(testPath, '..', 'dynakit', 'bin')
qrPath = os.path.join(binPath, 'qr.py')

mpi = ['/usr/bin/mpirun', '-np', '8']

N = 10000
m = 10
A = rand(N, m)

with tempfile.TemporaryDirectory() as tmpdir:
    for i in range(m):
        with open(os.path.join(tmpdir, 'input_{}.dat'.format(i)), 'wb') as f:
            f.write(A[:,i].tobytes())
    subprocess.check_call(mpi + [sys.executable, qrPath], cwd=tmpdir)
    Q = []
    for i in range(m):
        with open(os.path.join(tmpdir, 'output_{}.dat'.format(i)), 'rb') as f:
            Q.append(frombuffer(f.read()))
    with open(os.path.join(tmpdir, 'output_R.dat'), 'rb') as f:
        R = frombuffer(f.read()).reshape([m, m])

Q = transpose(Q)
assert abs(dot(Q.T, Q) - eye(m)).max() < 1E-12
assert abs(dot(Q, R) - A).max() < 1E-12
