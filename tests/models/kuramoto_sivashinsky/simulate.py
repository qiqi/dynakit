#!/usr/bin/python3

import matplotlib
matplotlib.use('Agg')
import json
import pylab
from numpy import *
import scipy.linalg
import scipy.sparse
import scipy.sparse.linalg

class Stepper:
    '''
    Semi-implicit RK2 time integration.
    Stage 1: Time dt/2; Explicit FE; Implicit Trapezoidal
    Stage 2: Time dt; Explicit Midpoint; Implicit 1/3 weights on 0, 1/2, 1
    '''
    @staticmethod
    def identity(Nx):
        data = ones([1, Nx])
        offsets = [0]
        return scipy.sparse.dia_matrix((data, offsets), shape=(Nx, Nx))

    @staticmethod
    def laplacian_matrix(Nx, dx):
        stencil = array([1, -2, 1]) / (dx*dx)
        data = ones(Nx) * stencil[:,newaxis]
        offsets = [-1,0,1]
        L = scipy.sparse.dia_matrix((data, offsets), shape=(Nx, Nx))
        return L

    @staticmethod
    def grad_matrix(Nx, dx):
        stencil = array([1, -1]) / (2*dx)
        data = ones(Nx) * stencil[:,newaxis]
        offsets = [-1,1]
        return scipy.sparse.dia_matrix((data, offsets), shape=(Nx, Nx))

    def __init__(self, Nx, dx, dt):
        I = self.identity(Nx)
        lapl = self.laplacian_matrix(Nx, dx)
        lapl2 = lapl * lapl
        self.M_linear = (lapl + lapl2) * dt
        self.M_quarter = I + self.M_linear / 4
        self.M_third = I + self.M_linear / 3
        self.M_grad = self.grad_matrix(Nx, dx)
        self.dt = dt

    def __call__(self, u):
        ux = self.M_grad * u
        rhs = u - self.M_linear * u / 4 - dt / 2 * ux * u
        uMid = scipy.sparse.linalg.spsolve(self.M_quarter, rhs)
        ux = self.M_grad * uMid
        rhs = u - self.M_linear * (u + uMid) / 3 - dt * ux * uMid
        return scipy.sparse.linalg.spsolve(self.M_third, rhs)

if __name__ == '__main__':
    config = json.load(open('config.json'))
    Nx = config['Nx']
    dx = config['dx']
    dt = config['dt']
    Nt = config['Nt']
    u = frombuffer(open('init.dat', 'rb').read(), float64)
    assert u.size == Nx

    if 'savefig' in config:
        history = [u]

    step = Stepper(Nx, dx, dt)
    for i in range(Nt):
        u = step(u)
        if 'savefig' in config:
            history.append(u)

    open('final.dat', 'wb').write(u.tobytes())
    if 'savefig' in config:
        pylab.contourf(arange(1, Nx+1) * dx, arange(Nt+1) * dt, history, 100)
        pylab.colorbar()
        pylab.savefig(config['savefig'])
