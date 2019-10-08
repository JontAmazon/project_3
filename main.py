# -*- coding: utf-8 -*-
"""
    NOTE: to run a python program with 3 processes:
        mpirun -np 3 python filename.py
"""
import numpy as np
import scipy.linalg as sl
from mpi4py import MPI


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nproc = comm.Get_size()




