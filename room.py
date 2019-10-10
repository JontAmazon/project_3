# -*- coding: utf-8 -*-
import numpy as np
import scipy.linalg as sl


class Room(object):
    
    def __init__(self, com,room, dx=1/3, omega=0.8, iters=100, wall_temp=15, heater_temp=40, window_temp=5):
        ''' Initalizes the room object for the corresponding room number.
        '''
        self.com = com
        self.room = room
        assert (room < 4),'The rank is too high, you might be trying to initiate too many instances'
        self.wall_temp = wall_temp 
        self.heater_temp = heater_temp 
        self.window_temp = window_temp 
        self.dx = dx
        self.omega = omega
        self.iters = iters
        self.u = None
        self.u_km1 = None #used for relaxation.

        #Initializes A and b for room 1, 2 or 3:
        if room == 1:
            self.init_room1()
        elif room == 2:
            self.init_room2()
        else:
            self.init_room3()

"""
    Since A and b are partly constant throughout the
    solving of the problem, we calculate the bulk of these matrices right away,
    in their respective room_omega_n() functions.
    A and b are then updated in every iteration, as the vectors gamma1 and gamma2 change.
    This is done in the solve() function.
"""
    def init_A_and_b_room1(self):
        self.A = 'hej'

        
    def init_A_and_b_room2(self):
        """ Initializes the matrices A and b for room 2. 
            For room 2, b will change in every iteration, while A is CONSTANT """
        height = 2                          #heigth of the room
        width = 1                           #width om the room
        M = int(round(height/self.dx)) - 1  #number of rows of nodes
        N = int(round(width/self.dx)) - 1   #number of cols of nodes
        size = M*N
        
        self.M, self.N, self.size = M, N, size
        
        # [Building A].
        # The bulk of A is very close to a toeplitz matrix with 5 diagonals.
        first_row = np.zeros(size)
        first_row[0] = -4
        first_row[1] = 1
        first_row[N] = 1
        self.A = sl.toeplitz(first_row, first_row)
        
        # The two inner super- and subdiagonals of this toeplitz matrix need to
        # be modified. Specifically, every N:th element should be set to zero,
        # for a total of (M-1) times, since our grid has M rows, and only the
        # first element to be set to zero goes "outside" of the matrix A.
        #
        # SUB: first zero goes in row N.
        row = N
        for i in range(M-1):
            self.A[row, row-1] = 0
            row += N
        
        #SUPER: first zero goes in row N-1.
        row = N-1
        for i in range(M-1):
            self.A[row, row+1] = 0
            row += N
        
        
        # [Building b].
        # Room 2 has 6 different (Dirichlet) boundary conditions. Of these, 2
        # change in every iteration, while 4 are constant. Here we initialize
        # b, considering only the 4 constant boundary conditions, while the
        # other 2 are uppdated in every iteration in solve().
        self.b = np.zeros(size)
        
        
        

    def init_A_and_b_room3(self):
        self.A = 'hej'




    def update_A_and_b_room1(self, gamma1):
        pass

    def update_A_and_b_room2(self, gamma1, gamma2):
        pass

    def update_A_and_b_room3(self, gamma2):
        pass


"""        
    In solve(), note that the vectors gamma1 and gamma2 store different things at
    different times. When a room2-object returns gamma1 and gamma2, they contain
    the derivatives of the temperature at these two boundaries. When room1-
    and room3-objects return these vectors, they store temperature values.
    generates room 1 aka omega_1
"""
    def solve(self):
        if room == 1:
            gamma_1 = np.ones(1/dx - 1)*(40+15+15+15)/4
            self.com.send(gamma_1,dest=2)
            for i in range(self.iters):
                gamma_1 = self.com.recv(source=2)

        if room == 2:
            gamma_1 = self.com.recv(source=1)
            gamma_2 = self.com.recv(source=3)
            
            
            U = sl.solve(self.A,self.b)
            

            # Send gamma_1 and gamma_2 to their respective rooms. 
            # If we have an even amount of internal points in the x
            # dimension, we have to skip one row that lies on the same
            # y-value as room 1's 'northern' wall & room 2's southern wall
            #  since these don't contribute to gamma
            if (1/dx-1) % 2 == 0:
                gamma_1_temp = U[int((1/dx -1)**2+(1/dx-1))::int(1/dx-1)]
                gamma_2_temp = U[int(1/dx-2)::int(1/dx-1)].copy()
                gamma_2_temp = gamma_2_temp[:-int(1/dx-2)]
            else: 
                gamma_1_temp = U[int(1/dx -1)**2::int(1/dx-1)]
                gamma_2_temp = U[int(1/dx-2)::int(1/dx-1)].copy()
                gamma_2_temp = gamma_2_temp[:-int(1/dx-1)]
            
            gamma_1 = gamma_1 - gamma_1_temp
            gamma_2 = gamma_2 - gamma_2_temp
            com.send(gamma_1,dest=1)
            com.send(gamma_2,dest=3)


        if room == 3:
            gamma_2 = np.ones(1/dx - 1)*(40+15+15+15)/4
            self.com.send(gamma_2,dest=2)
            for i in range(self.iters):
                gamma_2 = self.com.redoescv(source=2)


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