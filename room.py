# -*- coding: utf-8 -*-
import numpy as np


class Room(object):
    
    def __init__(self, room, dx=1/3, omega=0.8, iters=100, wall_temp=15, heater_temp=40, window_temp=5):
        ''' Initalizes the room object for the corresponding room number
        
        '''
        self.room = room
        self.wall_temp = wall_temp 
        self.heater_temp = heater_temp 
        self.window_temp = window_temp 
        self.dx = dx
        self.omega = omega
        self.iters = iters
        self.u = None
        self.u_km1 = None #used for relaxation.

        assert (room < 4),'The rank is too high, you might be trying to initiate too many instances'
        if room == 1:
            self.room_omega_1()
        elif room == 2:
            self.room_omega_2()
        else:
            self.room_omega_3()

"""
    Since A and b are partly constant throughout the
    solving of the problem, we calculate the bulk of these matrices right away,
    in their respective room_omega_n() functions.
    A and b are then updated in every iteration, as the vectors gamma1 and gamma2 change.
    This is done in the solve() function.
"""
    def room_omega_1(self):
        self.A = 'hej'
        
        # A=
        # B =
        # U = uvektorn för rum 1
        return A,b
    def room_omega_2(self):
        self.A = 'hej'
        # A=
        # B =

        return A,b,U
    def room_omega_3(self):
        self.A = 'hej'
        # A=
        # B =
        return A,b,U

"""        
    Note that the vectors gamma1 and gamma2 store different things at
    different times. When a room2-object returns gamma1 and gamma2, they contain
    the derivatives of the temperature at these two boundaries. When room1-
    and room3-objects return these vectors, they store temperature values.
    generates room 1 aka omega_1
"""
    def solve(self):

 
 '''       
                      cool wall
                 ____________________
                |                    >
                |                    >
                |       u[i-N]       >
                |          |         >
       hot wall | u[i-1]-u[i]-u[i+1] > gamma 1
                |          |         >
                |       u[i+N]       >
                |                    >
                |____________________>
                       cool wall        
        '''


''' generates room 2 aka omega_2
        
                      hot wall
                 ____________________
                |                    >
                |                    >
                |                    >
                |                    >
      cool wall |                    > gamma 2
                |                    >
                |       u[i-N]       >
                |          |         >
                | u[i-1]-u[i]-u[i+1] >
                <          |         |
                <       u[i+N]       |
                <                    |
                <                    |
        gamma 1 <                    |  cool wall
                <                    |
                <                    |
                <                    |
                <____________________|
                         window
        '''

        ''' generates room 3 aka omega_3
                
                      cool wall
                 ____________________
                <                    |
                <                    |
                <       u[i-N]       |
                <          |         |  
       gamma 2  < u[i-1]-u[i]-u[i+1] |  hot wall
                <          |         |
                <       u[i+N]       |
                <                    |
                <____________________|
                         window
        '''