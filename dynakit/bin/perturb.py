#!/usr/bin/python3

import argparse
import subprocess
from numpy import *

'''
This tool perturbs a state
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', '-i', type=str, required=True,
                        help='''Input state, a binary file of doubles''')
    parser.add_argument('--output', '-o', type=str, required=True,
                        help='''Output state, a binary file of doubles''')
    parser.add_argument('--epsilon', '-e', type=double, default=1E-8,
                        help='''Magnitude of random perturbations''')
    args = parser.parse_args()

    state = frombuffer(open(args.input, 'rb').read(), double)
    state = state + (random.rand(state.size) * 2 - 1) * args.epsilon
    open(args.output, 'wb').write(state.tobytes())
