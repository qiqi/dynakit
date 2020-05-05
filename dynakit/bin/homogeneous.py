#!/usr/bin/python3

import os
import argparse
import multiprocessing
from numpy import *

'''
This tool perturbs a state
'''

def run(path):
    path = os.path.join(rootPath, path)
    if not os.path.isdir(path):
        os.mkdir(path)
        perturb = os.path.join(binPath, 'perturb.py')
        os.chdir(rootPath)
        os.system('{} -i unperturbed/init.dat -o {}/init.dat'.format(
                  perturb, path))
        os.system('cp unperturbed/config.json {}'.format(path))

    os.chdir(path)
    if not os.path.exists('final.dat'):
        os.system(args.command)

def run_simulations():
    pool = multiprocessing.Pool(args.simultaneous_runs)
    pool.apply_async(run, ('unperturbed',))
    for iMode in range(args.modes):
        path = 'init_perturb_{:04d}'.format(iMode)
        pool.apply_async(run, (path,))
    pool.close()
    pool.join()

def diff(path):
    path = os.path.join(rootPath, path)
    if not os.path.exists(os.path.join(path, 'diff.dat')):
        evalPath = os.path.join(binPath, 'evaluate.py')
        os.chdir(path)
        a = 'final.dat'
        a0 = '../unperturbed/final.dat'
        os.system("{} -e '(a-a0)/{}' -o diff.dat -i a {} -i a0 {}".format(
                  evalPath, args.epsilon, a, a0))

def compute_perturbations():
    pool = multiprocessing.Pool(args.simultaneous_runs)
    for iMode in range(args.modes):
        path = 'init_perturb_{:04d}'.format(iMode)
        pool.apply_async(diff, (path,))
    pool.close()
    pool.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modes', '-m', type=int, required=True,
                        help='''Number of modes to run''')
    parser.add_argument('--command', '-c', type=str, required=True,
                        help='''Command to run for simulation''')
    parser.add_argument('--epsilon', '-e', type=double, default=1E-8,
                        help='''Magnitude of perturbation for more modes''')
    parser.add_argument('--simultaneous_runs', '-r', type=int, default=1,
                        help='''Number of simultaneous runs''')
    args = parser.parse_args()

    assert os.path.isdir('unperturbed')
    assert os.path.exists('unperturbed/init.dat')
    assert os.path.exists('unperturbed/config.json')

    binPath = os.path.abspath(os.path.dirname(__file__))
    rootPath = os.path.abspath(os.getcwd())
    qrPath = os.path.join(rootPath, 'qr_{:04d}'.format(args.modes))

    run_simulations()
    compute_perturbations()
    os.makedirs(qrPath, exist_ok=True)
    os.chdir(qrPath)
    for i in range(args.modes):
        fname = 'input_{}.dat'.format(i)
        if os.path.lexists(fname):
            os.remove(fname)
        os.symlink('../init_perturb_{:04d}/diff.dat'.format(i), fname)
