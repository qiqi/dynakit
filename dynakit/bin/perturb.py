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
    parser.add_argument('--bufferMB', '-b', type=int, default=8,
                        help='''Buffer size in mega-bytes''')
    args = parser.parse_args()

    fpIn = open(args.input, 'rb')
    fpOut = open(args.output, 'wb')

    while True:
        state = frombuffer(fpIn.read(args.bufferMB * 1024 * 128), double)
        if state.size:
            state = state + (random.rand(state.size) * 2 - 1) * args.epsilon
            fpOut.write(state.tobytes())
        else:
            break
