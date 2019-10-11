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


if __name__=='__main__':
    argparser = argparse.ArgumentParser(description='Solve a heat distribution problem for an apartment')
    optional_group = argparser.add_argument_group('Optional')
    optional_group.add_argument('--dx', '-d',
                        dest='dx',
                        type=float,
                        help='Distance between grid points')
    optional_group.add_argument('--omega', '-o',
                        dest='omega',
                        type = float,
                        help='Relaxation parameters')
    optional_group.add_argument('--iters', '-i',
                        dest='iters',
                        type = int,
                        help='Number of iterations')
    optional_group.add_argument('--wall_temp',
                        dest='wall_temp',
                        type = float,
                        help='Temperature of normal wall')
    optional_group.add_argument('--heater_temp',
                        dest='heater_temp',
                        type = float,
                        help='Temperature of heater')
    optional_group.add_argument('--win_temp',
                        dest='win_temp',
                        type = float,
                        help='Temperature of window')
    args = argparser.parse_args()

    kwargs = dict()

    
    if args.dx:
        kwargs['dx'] = args.dx
    if args.omega:
        kwargs['omega'] = args.omega
    if args.iters:
        kwargs['iters'] = args.iters
    if args.wall_temp:
        kwargs['wall_temp'] = args.wall_temp
    if args.heater_temp:
        kwargs['heater_temp'] = args.heater_temp
    if args.win_temp:
        kwargs['win_temp'] = args.win_temp


    com = MPI.COMM_WORLD
    room_nr = com.Get_rank() + 1
    nproc = com.Get_size()

    room_object = room.Room(**kwargs,room=room_nr,com=com)
    U, gamma = room_object.solve()     
    if room==2:
        U1 = com.recv(source=0)
        U3 = com.recv(source=2)
        room_object.plot_apartment(U1=U1,U2=U,U3=U3)       
    else:
        com.send(U,dest=1)





