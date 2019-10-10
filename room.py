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
        assert (dx < 1/2), 'The mesh width, dx, should be smaller than 1/2.'
        self.dx = dx
        self.omega = omega
        assert (type(iters)==int), 'The number of iterations, iters, should be an integer.'
        self.iters = iters
        self.u = None
        self.u_km1 = None #used for relaxation.

        #Initializes A and b for room 1, 2 or 3:
        if room == 1:
            self.init_A_and_b_room1()
        elif room == 2:
            self.init_A_and_b_room2()
        else:
            self.init_A_and_b_room3()

    """
        Since A and b are partly constant throughout the
        solving of the problem, we calculate the bulk of these matrices right away,
        in their respective room_omega_n() functions.
        A and b are then updated in every iteration, as the vectors gamma1 and gamma2 change.
        This is done in the solve() function.
    """
    def init_A_and_b_room1(self):
        N = int(round(1/self.dx)) - 1   #Number of columns and rows of nodes
        
        A = np.zeros(N)
        size = N*N
        
        #Fill the diagonal and second super/subdiagonals of A
        diagonals = np.zeros(size)
        diagonals[0] = -4
        diagonals[N] = 1
        A = sl.toeplitz(diagonals, diagonals)
        
        #Change the diagonal elements of all right boundary elements to -3 and fill the 
        #subdiagonal entry with 1 (corresponding to the node on the left hand side 
        #of the right boundary element element).
        for i in range(1, N+1):
            A[i*N - 1, i*N - 1] = -3
            A[i*N - 1, i*N - 2] = 1
    
        #Change the subdiagonal entries for all left boundary values to 1
        #(corresponding to the node on the right hand side of the left boundary element)
        for i in range(0, N):
            A[i*N, i*N + 1] = 1
    
        #Check if our grid contains elements inbetween the corner elements and
        #in that case fill the super and subdiagonal elements on the same row with 
        #1, corresponding to the left and right nodes with respect to these elements
        if N > 2:
            for i in range(0, N):
                for j in range(i*N + 1, i*N + N - 1):
                    A[j, j - 1] = 1
                    A[j, j + 1] = 1

        
    def init_A_and_b_room2(self):
        """ Initializes the matrices A and b for room 2. 
            For room 2, b will change in every iteration, while A is CONSTANT """
        height = 2                          #heigth of room 2
        width = 1                           #width  of room 2
        M = int(round(height/self.dx)) - 1  #number of rows of nodes
        N = int(round(width/self.dx)) - 1   #number of cols of nodes
        self.N = N  #used later
        size = M*N
        
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
        
        # Upper bounndary:
        self.b[:N] = -self.heater_temp
        
        # Lower boundary:
        self.b[-N:] = -self.window_temp
        
        # Upper left boundary:
        # Every N nodes are effected by the upper left boundary, and in total 
        # N+1 nodes are effected. The first effected node is the 0:th node.
        index = 0
        for i in range(N+1):
            self.b[index] = -self.wall_temp
            index += N
        
        # Lower right boundary:
        # Every N nodes are effected by the upper left boundary, and in total 
        # N+1 nodes are effected. The first effected node is the (N^2+(N-1)):th node.
        index = N**2 + (N-1)
        for i in range(N+1):
            self.b[index] = -self.wall_temp
            index += N
        

    def init_A_and_b_room3(self):
        self.A = 'hej'
    
    def update_A_and_b_room1(self, gamma1):
        pass

    def update_A_and_b_room2(self, gamma1, gamma2):
        """ Updates the b-matrix for room 2, according to values in gamma1 and
            gamma2. Note that for room 2, the A-matrix is constant.
        """
        N = self.N
        
        # Upper right boundary:
        # Every N nodes are effected by the upper right boundary, and in total 
        # N nodes are effected. The first effected node is the (N-1):th node.
        index = N-1
        for i in range(N):
            self.b[index] = -gamma2[i]
            index += N

        # Lower left boundary:
        # Every N nodes are effected by the lower left boundary, and in total 
        # N nodes are effected. The first effected node is the (N^2+N):th node.
        index = N**2 + N
        for i in range(N):
            self.b[index] = -gamma1[i]
            index += N


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
        room = self.room
        dx = self.dx
        com = self.com
        if room == 1:
            gamma1 = np.ones(1/dx - 1)*(40+15+15+15)/4
            self.com.send(gamma1,dest=2)
            for i in range(self.iters):
                gamma1 = self.com.recv(source=2)
                
                self.update_A_and_b_room1(gamma1=gamma1)
                u = sl.solve(self.A,self.b)

                gamma1_temp = u[int(1/dx-2)::int(1/dx-1)]
                gamma1 = gamma1_temp - gamma1
                com.send(gamma1,dest=2)
                u = self.omega*u + (1-self.omega)*self.u_km1
                self.u_km1=u
            self.u = u
        if room == 2:
            for i in range(self.iters):
                gamma1 = self.com.recv(source=1)
                gamma2 = self.com.recv(source=3)

                self.update_A_and_b_room2(gamma1=gamma1,gamma2=gamma2)
                U = sl.solve(self.A,self.b)


                # Send gamma_1 and gamma_2 to their respective rooms. 
                # If we have an even amount of internal points in the x
                # dimension, we have to skip one row that lies on the same
                # y-value as room 1's 'northern' wall & room 2's southern wall
                #  since these don't contribute to gamma
                if (1/dx-1) % 2 == 0:
                    gamma1_temp = U[int((1/dx -1)**2+(1/dx-1))::int(1/dx-1)]
                    gamma2_temp = U[int(1/dx-2)::int(1/dx-1)].copy()
                    gamma2_temp = gamma2_temp[:-int(1/dx-2)]
                else: 
                    gamma1_temp = U[int(1/dx -1)**2::int(1/dx-1)]
                    gamma2_temp = U[int(1/dx-2)::int(1/dx-1)].copy()
                    gamma2_temp = gamma2_temp[:-int(1/dx-1)]

                gamma1 = gamma1 - gamma1_temp
                gamma2 = gamma2 - gamma2_temp
                com.send(gamma1,dest=1)
                com.send(gamma2,dest=3)
                U = self.omega*U + (1-self.omega)*self.u_km1
                self.u_km1 = U
            self.u = U

        if room == 3:
            gamma2 = np.ones(1/dx - 1)*(40+15+15+15)/4
            self.com.send(gamma2,dest=2)
            for i in range(self.iters):
                gamma2 = self.com.recv(source=2)

                self.update_A_and_b_room3(gamma2=gamma2)
                u = sl.solve(self.A,self.b)
                
                
                gamma2_temp = u[0::int(1/dx-1)]
                gamma2 =  gamma2_temp - gamma2
                com.send(gamma2,dest=2)
                u = self.omega*u + (1-self.omega)*self.u_km1
                self.u_km1=u
            self.u = u

"""
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
"""