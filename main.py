# -*- coding: utf-8 -*-
"""
    NOTE: to run a python program with 3 processes:
        mpirun -np 3 python filename.py
"""
import numpy as np
import scipy.linalg as sl
from mpi4py import MPI
import argparse

import room

class Room(object):
    def __init__(self, dx=1/20, omega=0.8,):
        test = 2


    def __call__(self,parameters):
        test = 2
        test = 1



if __name__=='__main__':
    argparser = argparse.ArgumentParser(description='Solve a heat distribution problem for an apartment')
    optional_group = argparser.add_argument_group('Optional')
    optional_group.add_argument('--d_x', '-d',
                        dest='d_x',
                        type=float,
                        help='Distance between grid points')
    optional_group.add_argument('--omega', '-o',
                        dest='omega',
                        type = float,
                        help='Relaxation parameters')
        args = argparser.parse_args()
    optional_group.add_argument('--iters', '-i'
                        dest='iters',
                        type = int,
                        help='Number of iterations')
    args = argparser.parse_args()

    kwargs = dict()

    
    if args.delta:
        kwargs['delta'] = args.delta
    if args.omega:
        kwargs['omega'] = args.omega
        print(args.omega)
    if args.iters:
        kwargs['iters'] = args.iters

    comm = MPI.COMM_WORLD
    room = comm.Get_rank() + 1
    nproc = comm.Get_size()
    room_object = Room(**kwargs,room=room)                


    if room == 0:
        print('my rank is ' + str(room) +'\n')
        comm.send('blebleble',dest=1,tag=11)
    elif room == 1:
        
        data = comm.recv(source=0,tag=11)
        print('my rank is ' + str(room) +'and i just received the string ' + str(data) + '\n')




