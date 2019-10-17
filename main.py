# -*- coding: utf-8 -*-
"""
    NOTE: to run a python program with 3 processes:
        mpirun -np 3 python filename.py
"""
import sys
import time

import numpy as np
import scipy.linalg as sl
from mpi4py import MPI
import argparse

import room

def parse_input_arguments():

    argparser = argparse.ArgumentParser(description='Solve a heat distribution problem for an apartment')
    optional_group = argparser.add_argument_group('Optional')
    mandatory_group = argparser.add_argument_group('Mandatory') # dx ska nog vara här!
    mandatory_group.add_argument('--dx', '-d',
                        dest='dx',
                        type=str,
                        help='Distance between grid points. Needs to be specified in the form of a fraction 1/x.')
    optional_group.add_argument('--omega', '-o',
                        dest='omega',
                        type = float,
                        help='Relaxation parameters')
    optional_group.add_argument('--max_iters', '-i',
                        dest='max_iters',
                        type = int,
                        help='Maximum number of iterations')
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
    optional_group.add_argument('--debug',
                        dest='debug',
                        type = bool,
                        help='If the user wants to debug the solution progress')
    optional_group.add_argument('--tol',
                        dest='tol',
                        type = float,
                        help='Stopping condition based on ||u-u_km1||_2 < tol')
    args = argparser.parse_args()

    kwargs = dict()
    debug = False
    
    if args.dx:
        frac = args.dx.split('/')
        assert(len(frac)==2), 'dx needs to be of the format "1/x"'
        kwargs['dx'] = float(int(frac[0])/int(frac[1]))
    else:
        argparser.print_help()
        sys.stdout.flush()
    if args.omega:
        kwargs['omega'] = args.omega
    if args.max_iters:
        kwargs['max_iters'] = args.max_iters
    if args.wall_temp:
        kwargs['wall_temp'] = args.wall_temp
    if args.heater_temp:
        kwargs['heater_temp'] = args.heater_temp
    if args.win_temp:
        kwargs['win_temp'] = args.win_temp
    if args.debug:
        kwargs['debug'] = args.debug
        debug = args.debug
    if args.tol:
        kwargs['tol'] = args.tol

    return kwargs

if __name__=='__main__':
    
    kwargs = parse_input_arguments() # parses_input_arguments

    # Initiate the communication object that the different rooms use.
    com = MPI.COMM_WORLD

    # Define the room number by obtaining the rank of this process.
    room_nr = com.Get_rank() + 1
    room_object = room.Room(**kwargs,room=room_nr,com=com)
    
    time1 = time.time()*1000
    U, gamma = room_object.solve()
    time2 = time.time()*1000
    
    # Room 2 gathers all the data from the rooms and plots the
    # temperature distribution throughout the apartment.
    if room_nr==2:
        print('Time taken = ' + str(int(time2-time1))+' [ms]')
        sys.stdout.flush()
        U1 = com.recv(source=0,tag=1)
        com.send('ping',dest=0)
        gamma1 = com.recv(source=0,tag=2)
        
        U3 = com.recv(source=2,tag=3)
        com.send('ping',dest=2)
        gamma2 = com.recv(source=2,tag=4)
        room_object.plot_apartment(U1=U1,U2=U,U3=U3,gamma1=gamma1,gamma2=gamma2)       
    else:
        com.send(U,dest=1,tag=room_nr)
        # If there wasn't a ping recv here, both gamma and u would be sent to 
        # room 2 at such a close interval such that room 2 could mix them up.
        ping = com.recv(source=1)
        com.send(gamma,dest=1,tag=room_nr+1)


'''
HXCHV



A[x][y] är mycket långsammare än A[x,y].

assert för tester, men raise exception för fel. Bör använda
raise för att notifiera användaren för felhantering.

Kan vara bättre att ha "hela" A-matrisen då strukturen blir mer komprimerbar/glesare.

'''




