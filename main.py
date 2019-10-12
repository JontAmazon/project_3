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
                        type=str,
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
        frac = args.dx.split('/')
        kwargs['dx'] = float(int(frac[0])/int(frac[1]))
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
    debug = True
    room_object = room.Room(**kwargs,room=room_nr,com=com,debug = debug)
    U, gamma = room_object.solve()     
    print('done with solve')
    
    if room_nr==2:
        #print(U)
        U1 = com.recv(source=0,tag=1)
        com.send('ping',dest=0)
        gamma1 = com.recv(source=0,tag=2)
        
        U3 = com.recv(source=2,tag=3)
        com.send('ping',dest=2)
        gamma2 = com.recv(source=2,tag=4)
        if debug:
            print('gamma1' + str(gamma1))
            print('u1 ' + str(U1))
            print('u2 ' + str(U.astype(int)))
            print('gamma2' + str(gamma2))
            print('u3 ' + str(U3))
        room_object.plot_apartment(U1=U1,U2=U,U3=U3,gamma1=gamma1,gamma2=gamma2)       
    else:
        com.send(U,dest=1,tag=room_nr)
        ping = com.recv(source=1)
        com.send(gamma,dest=1,tag=room_nr+1)
    #print(U)





