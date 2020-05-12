#!/usr/bin/python3

import matplotlib
matplotlib.use('Agg')
import json
import pylab
from numpy import *
import scipy.linalg
import scipy.sparse
import scipy.sparse.linalg

import simulate

class Stepper(simulate.Stepper):
    def __call__(self, u, uTan):
        ux = self.M_grad * u
        uxTan = (self.M_grad * uTan.T).T
        rhs = u - self.M_linear * u / 4 - dt / 2 * ux * u
        rhsTan = uTan - (self.M_linear * uTan.T).T / 4 \
               - dt / 2 * (ux * uTan + uxTan * u)
        uMid = scipy.sparse.linalg.spsolve(self.M_quarter, rhs)
        uMidTan = scipy.sparse.linalg.spsolve(self.M_quarter, rhsTan)
        ux = self.M_grad * uMid
        uxTan = (self.M_grad * uMidTan.T).T
        rhs = u - self.M_linear * (u + uMid) / 3 - dt * ux * uMid
        rhsTan = uTan - (self.M_linear * (uTan + uMidTan).T).T / 3 \
               - dt * (uxTan * uMid + ux * uMidTan)
        return scipy.sparse.linalg.spsolve(self.M_third, rhs), \
               scipy.sparse.linalg.spsolve(self.M_third, rhsTan.T).T

if __name__ == '__main__':
    config = json.load(open('config.json'))
    Nx = config['Nx']
    dx = config['dx']
    dt = config['dt']
    Nt = config['Nt']
    u = frombuffer(open('init.dat', 'rb').read(), float64)
    uTan = [frombuffer(open('init_{}.dat'.format(suf), 'rb').read(), float64)
            for suf in config['tangent_suffixes']]
    assert u.size == Nx
    assert all([ut.size == Nx for ut in uTan])

    if 'savefig' in config:
        history = [u]

    step = Stepper(Nx, dx, dt)
    for i in range(Nt):
        u, uTan = step(u, uTan)
        if 'savefig' in config:
            history.append(u)

    open('final.dat', 'wb').write(u.tobytes())
    for suf, ut in zip(config['tangent_suffixes'], uTan):
        open('final_{}.dat'.format(suf), 'wb').write(ut.tobytes())

    if 'savefig' in config:
        pylab.contourf(arange(1, Nx+1) * dx, arange(Nt+1) * dt, history, 100)
        pylab.colorbar()
        pylab.savefig(config['savefig'])
