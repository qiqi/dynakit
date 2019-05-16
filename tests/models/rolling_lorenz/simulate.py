import sys
import json
from numpy import *

def step(u, dx, dt, U, nu, sigma, rho, beta):
    um = vstack([zeros([1,3]), u[:-1]])
    up = vstack([u[1:], zeros([1,3])])
    dudx = (u - um) / dx
    d2udx2 = (up + um - 2 * u) / dx**2
    x, y, z = u.T
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    dudt = transpose([dxdt, dydt, dzdt]) - U * dudx + nu * d2udx2
    u += dudt * dt

def animate():
    config = json.load(open('config.json'))
    Nx = config['Nx']
    xGrid = linspace(config['xMin'], config['xMax'], Nx)
    dx = xGrid[1] - xGrid[0]
    dt = config['Dt']
    U = 0
    nu = 1 / config['Re']
    rho = config['Ra'] * exp(-xGrid**2 / 2)
    u = ones([Nx, 3]) * config['init']
    sigma, beta = 10, 8./3
    for j in range(100):
        for i in range(10):
            step(u, dx, dt, U, nu, sigma, rho, beta)
        cla()
        plot(xGrid, u[:,2])
        ylim([0, 50])
        savefig('figs/{:03d}.png'.format(j))

if __name__ == '__main__':
    config = json.load(open('config.json'))
    Nx = config['Nx']
    xGrid = linspace(config['xMin'], config['xMax'], Nx)
    dx = xGrid[1] - xGrid[0]
    dt = config['Dt']
    U = 0
    nu = 1 / config['Re']
    rho = config['Ra'] * exp(-xGrid**2 / 2)
    if 'init' in config:
        u = ones([Nx, 3]) * config['init']
    else:
        u = frombuffer(open('init.dat', 'rb').read(), float64)
        u = u.reshape([-1,3])
        assert u.shape[0] == Nx

    sigma, beta = 10, 8./3
    for i in range(config['Nt']):
        step(u, dx, dt, U, nu, sigma, rho, beta)

    open('final.dat', 'wb').write(u.tobytes())
