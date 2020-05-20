import os
import sys
import json
import tempfile
import subprocess
from numpy import *

def run_tangent(ksPath, dirTangent, u0, du, dx, dt, Nt):
    nTangent = du.shape[1]
    json.dump({
        'Nx': u0.size, 'dx': dx, 'dt': dt, 'Nt': Nt,
        'tangent_suffixes': [str(i) for i in range(nTangent)]
        }, open(os.path.join(dirTangent, 'config.json'), 'w'))
    open(os.path.join(dirTangent, 'init.dat'), 'wb').write(u0.tobytes())
    for i in range(nTangent):
        fname = os.path.join(dirTangent, 'init_{}.dat'.format(i))
        open(fname, 'wb').write(du[:,i].tobytes())

    tangent = os.path.join(ksPath, 'simulate_tangent.py')
    subprocess.check_call([sys.executable, tangent], cwd=dirTangent)

    fname = os.path.join(dirTangent, 'final.dat')
    u0 = frombuffer(open(fname, 'rb').read(), double)
    du = []
    for i in range(nTangent):
        fname = os.path.join(dirTangent, 'final_{}.dat'.format(i))
        du.append(frombuffer(open(fname, 'rb').read(), double))
    return u0, transpose(du)

def run_sim(ksPath, dirSim, u0, dx, dt, Nt):
    json.dump({
        'Nx': u0.size, 'dx': dx, 'dt': dt, 'Nt': Nt
        }, open(os.path.join(dirSim, 'config.json'), 'w'))
    open(os.path.join(dirSim, 'init.dat'), 'wb').write(u0.tobytes())

    tangent = os.path.join(ksPath, 'simulate.py')
    subprocess.check_call([sys.executable, tangent], cwd=dirSim)

    fname = os.path.join(dirSim, 'final.dat')
    u0 = frombuffer(open(fname, 'rb').read(), double)
    return u0

def test_tangent_kuramoto_sivashinsky():
    testPath = os.path.dirname(os.path.abspath(__file__))
    ksPath = os.path.join(testPath, 'models', 'kuramoto_sivashinsky')
    primal = os.path.join(ksPath, 'simulate.py')

    Nx = random.randint(128, 1024)
    dx = random.rand()
    dt = random.rand() * dx
    Nt = random.randint(2, 16)
    u0 = random.rand(Nx) - 0.5

    nTangent = random.randint(2,5)
    du0 = random.random([Nx, nTangent]) - 0.5
    EPS = 1E-8

    with tempfile.TemporaryDirectory() as tmpdir:
        u1, du1 = run_tangent(ksPath, tmpdir, u0, du0, dx, dt, Nt)
        u2 = run_sim(ksPath, tmpdir, u0, dx, dt, Nt)
        du2 = []
        for iTan in range(nTangent):
            u3 = run_sim(ksPath, tmpdir, u0 + EPS * du0[:,iTan], dx, dt, Nt)
            du2.append((u3 - u2) / EPS)
        du2 = transpose(du2)
    assert(abs(u1-u2).max() == 0)
    assert(abs(du1-du2).max() <= 1E-5)
    return u1, u2, du1, du2

if __name__ == '__main__':
    u1, u2, du1, du2 = test_tangent_kuramoto_sivashinsky()
