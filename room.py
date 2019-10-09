# -*- coding: utf-8 -*-
import numpy as np


class Room(object):
    
    def __init__(self, room, d_x = 1/3, omega=0.8, iters=100):
        ''' initalizes the room object for the corresponding 
        '''
        self.room = room

        # Is Kelvin really necessary? Laplace is linear and since
        # only the difference between the nodal temperatures are
        # of relevance for the dynamics (and thus constants are removed)
        # , it's all interchangable right?
        self.wall_temp = 15 #deg Celsius
        self.heater_temp = 40 #deg Celsius
        self.window_temp = 5 #deg Celsius
        self.d_x = d_x
        self.omega = omega
        self.iters = iters

        assert (room < 4),'The rank is too high, you might be trying to initiate too many instances'
        if room == 1:
            self.A,self.b,self.U = self.room_omega_1()
        elif room == 2:
            self.A,self.b,self.U = self.room_omega_2()
        else:
            self.A,self.b,self.U = self.room_omega_3()

    def room_omega_1(self):
        
        # A=
        # B =
        # U = uvektorn för rum 1
        return A,b,U
    def room_omega_2(self):
        
        # A=
        # B =

        return A,b,U
    def room_omega_3(self):
        
        # A=
        # B =
        return A,b,U

''' generates room 1 aka omega_1
        
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