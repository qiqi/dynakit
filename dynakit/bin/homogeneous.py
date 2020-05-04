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

    pool = multiprocessing.Pool(args.simultaneous_runs)
    pool.apply_async(run, ('unperturbed',))

    for iMode in range(args.modes):
        path = 'init_perturb_{:04d}'.format(iMode)
        pool.apply_async(run, (path,))

    pool.close()
    pool.join()
