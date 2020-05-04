import sys
import json
import pylab
from numpy import *
import scipy.linalg

class Stepper:
    def __init__(self, Nx, dx, dt, nu):
        self.ab = zeros([3, Nx])
        self.ab[1] = 2 * nu / dx**2 * dt + 1
        self.ab[0] = -nu / dx**2 * dt
        self.ab[2] = -nu / dx**2 * dt
        self.ab[1,0] = nu / dx**2 * dt + 1
        self.ab[1,-1] = nu / dx**2 * dt + 1
        self.dt = dt

    def __call__(self, u, sigma, rho, beta):
        x, y, z = u.T
        dxdt = sigma * (y - x)
        dydt = x * (rho - z) - y
        dzdt = x * y - beta * z
        dudt = transpose([dxdt, dydt, dzdt])
        u[:] = scipy.linalg.solve_banded((1,1), self.ab, u + dudt * self.dt)

def animate():
    config = json.load(open('config.json'))
    Nx = config['Nx']
    xGrid = linspace(config['xMin'], config['xMax'], Nx)
    dx = xGrid[1] - xGrid[0]
    dt = config['Dt']
    nu = 1 / config['Re']
    rho = config['Ra'] * ones(Nx)
    u = (ones([Nx, 3]) + random.rand(Nx, 3) * 0.00001) * config['init']
    step = Stepper(Nx, dx, dt, nu)
    sigma, beta = 10, 8./3
    for i in range(100000):
        step(u, sigma, rho, beta)
    print('run up complete')
    for j in range(1001):
        for i in range(10):
            step(u, sigma, rho, beta)
        pylab.cla()
        pylab.plot(xGrid, u[:,2])
        pylab.ylim([0, 75])
        pylab.pause(0.001)

if __name__ == '__main__':
    config = json.load(open('config.json'))
    Nx = config['Nx']
    xGrid = linspace(config['xMin'], config['xMax'], Nx)
    dx = xGrid[1] - xGrid[0]
    dt = config['Dt']
    U = 0
    nu = 1 / config['Re']
    rho = config['Ra'] * ones(Nx)
    if 'init' in config:
        u = (ones([Nx, 3]) + random.rand(Nx, 3) * 0.00001) * config['init']
    else:
        u = frombuffer(open('init.dat', 'rb').read(), float64)
        u = u.reshape([-1,3])
        assert u.shape[0] == Nx

    sigma, beta = 10, 8./3
    step = Stepper(Nx, dx, dt, nu)
    for i in range(config['Nt']):
        step(u, sigma, rho, beta)

    open('final.dat', 'wb').write(u.tobytes())
