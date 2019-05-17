import os
import sys
import glob
from mpi4py import MPI
from numpy import *

def probe_Nm(comm):
    rank = comm.Get_rank()
    if rank == 0:
        with open('input_0.dat', 'rb') as f:
            f.seek(0, 2)
            nBytes = f.tell()
            assert nBytes % 8 == 0
            N = nBytes // 8
        inputs = glob.glob('input_*.dat')
        m = len(inputs)
        for i in range(m):
            assert os.path.exists('input_{}.dat'.format(i))
    else:
        N, m = None, None
    N = comm.bcast(N, root=0)
    m = comm.bcast(m, root=0)
    return N, m

def read_matrix(comm, N, m):
    size = comm.Get_size()
    rank = comm.Get_rank()
    iSep = array(around(linspace(0, N, size+1)), int)
    A = []
    for turn in range(size + m - 1):
        comm.Barrier()
        for col in range(m):
            if turn == rank + col:
                with open('input_{}.dat'.format(col), 'rb') as f:
                    f.seek(iSep[rank] * 8)
                    buf = f.read((iSep[rank + 1] - iSep[rank]) * 8)
                    A.append(frombuffer(buf))
    A = transpose(A)
    assert A.shape == (iSep[rank + 1] - iSep[rank], m)
    return A

def stacked_qr(comm, myR):
    size = comm.Get_size()
    rank = comm.Get_rank()
    m = myR.shape[0]
    assert myR.shape == (m,m)
    if rank == 0:
        stackedR = empty([m*size, m])
        stackedR[:m] = myR
        for i in range(1, size):
            comm.Recv([stackedR[i*m:(i+1)*m], MPI.DOUBLE], source=i)
        QR, RR = linalg.qr(stackedR)
        for i in range(1, size):
            comm.Send([QR[i*m:(i+1)*m], MPI.DOUBLE], dest=i)
        QR = QR[:m]
    else:
        comm.Send([myR, MPI.DOUBLE], dest=0)
        QR = empty([m,m])
        comm.Recv([QR, MPI.DOUBLE], source=0)
        RR = None
    return QR, RR

def write_Q_matrix(comm, myQ):
    size = comm.Get_size()
    rank = comm.Get_rank()
    for turn in range(size + m - 1):
        comm.Barrier()
        for col in range(m):
            if turn == rank + col:
                mode = 'wb' if rank == 0 else 'ab'
                with open('output_{}.dat'.format(col), mode) as f:
                    f.write(myQ[:,col].tobytes())

def write_R_matrix(comm, R):
    rank = comm.Get_rank()
    if rank == 0:
        with open('output_R.dat', 'wb') as f:
            f.write(R.tobytes())

N, m = probe_Nm(MPI.COMM_WORLD)
myA = read_matrix(MPI.COMM_WORLD, N, m)
myQ, myR = linalg.qr(myA)
QR, RR = stacked_qr(MPI.COMM_WORLD, myR)
myQ = dot(myQ, QR)
write_Q_matrix(MPI.COMM_WORLD, myQ)
write_R_matrix(MPI.COMM_WORLD, RR)
