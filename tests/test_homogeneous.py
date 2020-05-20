import os
import sys
import shutil
import tempfile
import subprocess
from numpy import *

def test_homogeneous():
    testPath = os.path.dirname(os.path.abspath(__file__))
    simPath = os.path.join(testPath, 'models',
                           'kuramoto_sivashinsky', 'simulate.py')
    binPath = os.path.join(testPath, '..', 'dynakit', 'bin')
    homoPath = os.path.join(binPath, 'homogeneous.py')
    qrPath = os.path.join(binPath, 'qr.py')

    with tempfile.TemporaryDirectory() as tmpdir:
        for iSeg in range(5):
            segPath = os.path.join(tmpdir, 'segment_{:04d}'.format(iSeg))
            print(segPath)
            os.makedirs(os.path.join(segPath, 'unperturbed'))
            cmd = [homoPath, '-m', '5', '-c', simPath, '-r', '99']
            if iSeg == 0:
                dataPath = os.path.join(testPath, 'segment',
                                        'kuramoto_sivashinsky', 'unperturbed')
                shutil.copy(os.path.join(dataPath, 'init.dat'),
                            os.path.join(segPath, 'unperturbed'))
                shutil.copy(os.path.join(dataPath, 'config.json'),
                            os.path.join(segPath, 'unperturbed'))
            else:
                prevPath = os.path.join(tmpdir, 'segment_{:04d}'.format(iSeg-1))
                shutil.copy(os.path.join(prevPath, 'unperturbed', 'final.dat'),
                            os.path.join(segPath, 'unperturbed', 'init.dat'))
                shutil.copy(os.path.join(prevPath, 'unperturbed', 'config.json'),
                            os.path.join(segPath, 'unperturbed'))
                cmd += ['-p', os.path.join(prevPath, 'qr_0005', 'output_%d.dat')]
            subprocess.check_call(cmd, cwd=segPath)
            subprocess.check_call(qrPath, cwd=os.path.join(segPath, 'qr_0005'))

if __name__ == '__main__':
    test_homogeneous()
