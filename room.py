# -*- coding: utf-8 -*-
import numpy as np


class Room(object):
    def __init__(self, room, N=1/3, omega=0.8, heater_temp=40, window_temp=5, wall_temp=15):
        self.room = room
        self.N = N
        self.omega = omega
        self.heater_temp = heater_temp
        self.window_temp = window_temp
        self.wall_temp = wall_temp
        
        self.u = None
        self.u_km1 = None #used for relaxation.

    def __call__(self,parameters):
        test = 2
        test = 1


"""
    Notes for Room1, Room2 and Room3:
    
    1. Since the A-matrix is CONSTANT, and b is partly constant throughout the
    solving of the problem, we calculate the bulk of these matrices right away,
    in their __init__() functions.
    b is then updated in every iteration, as the vectors gamma1 and gamma2 change.
    This is done in their respective solve() functions.
    
    2. Note that the vectors gamma1 and gamma2 store different things at
    different times. When a room2-object returns gamma1 and gamma2, they contain
    the derivatives of the temperature at these two boundaries. When room1-
    and room3-objects return these vectors, they store temperature values.
"""

'''
    TEMPORARY NOTE TO SELF:    Nog Spara vektorerna som håller index för de platser där b måste uppdateras.
'''


class Room1(Room):
    def __init__(self, room, N=1/3, omega=0.8, heater_temp=40, window_temp=5, wall_temp=15):
        super(room, N, omega, heater_temp, window_temp, wall_temp)
        
        """ TODO: implementera A och b """
        self.A = 42
        self.b = 42
        
    def solve(self, gamma1):
        """ Solves the heating equation in room 1 with Neumann conditions,
            with temperature derivatives given by the vector gamma1. """
            
        #returns gamma1, e.g. the temperature at gamma1, to be used by room 2
        #                     in the next iteration.
        pass
        
class Room2(Room):
    def __init__(self, room, gamma1_guess, gamma2_guess, N=1/3, omega=0.8, \
                 heater_temp=40, window_temp=5, wall_temp=15):
        super(room, N, omega, heater_temp, window_temp, wall_temp)
        self.gamma1 = gamma1_guess #gissar att dessa är bra att ha som inparametrar, inte säker.
        self.gamma2 = gamma2_guess #gissar att dessa är bra att ha som inparametrar, inte säker.
        
        """NOTE: Detta (A och b) kommer jag Jonte att implementera STRAX:"""
        self.A = 42
        self.b = 42
        
    def solve(self, gamma1, gamma2):
        """ Solves the heating equation in room 2 with Dirichlet conditions,
            with temperatures given by the vectors gamma1 and gamma2. """

        #returns gamma1 and gamma2, e.g. the temperature derivatives
        #                                at gamma1 and gamma2.
        pass

class Room3(Room):
    def __init__(self, room, N=1/3, omega=0.8, heater_temp=40, window_temp=5, gammaN=15):
        super(room, N, omega, heater_temp, window_temp, gammaN)
        
        """ TODO: implementera A och b """
        self.A = 42
        self.b = 42
        
    def solve(self, gamma2):
        """ Solves the heating equation in room 3 with Neumann conditions,
            with temperature derivatives given by the vector gamma2. """

        #returns gamma2, e.g. the temperature at gamma2, to be used by room 2
        #                     in the next iteration.
        pass
    




    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    