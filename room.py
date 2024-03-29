# -*- coding: utf-8 -*-
import numpy as np
import scipy.linalg as sl
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
import time
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


class Room(object):
    
    def __init__(self, com,room, dx, omega=0.9, max_iters=1000, wall_temp=15, heater_temp=40, win_temp=5, tol=1e-6, debug=False):
        ''' Initalizes the room object for the corresponding room number.
        '''
        self.com = com
        self.room = room
        self.wall_temp = wall_temp 
        self.heater_temp = heater_temp 
        self.window_temp = win_temp 
        self.dx = dx
        self.N = int(round(1/self.dx)) - 1 
        self.omega = omega
        self.max_iters = max_iters
        self.debug = debug
        self.tol = tol

        assert (room < 4),'The rank is too high, you might be trying to initiate too many instances'
        assert (dx < 1/2), 'The mesh width, dx, should be smaller than 1/2.'
        assert (type(self.max_iters)==int), 'The number of iterations, max_iters, should be an integer.'
        
        self.u = None
        self.u_km1 = None

        
        # Create A (which is constant!) for room 1, 2 or 3.
        if room == 2:
            self.create_A_and_b_room2()
        else:
            self.create_A_and_b_room1_room3()
       


    def create_A_and_b_room1_room3(self):
        """ Creates the A- and b-matrix for room 1, the A-matrix being
            constant and the second one being mostly constant.
        """
        N = self.N    # Number of columns and rows of nodes
        size = N*N    # Number of unknown nodes.
                
        """ Create A """
        # Fill the diagonal and Nth super/subdiagonals of A
        diagonals = np.zeros(size)
        diagonals[0] = -4
        diagonals[N] = 1
        A = sl.toeplitz(diagonals, diagonals)
        
        # Change the diagonal elements of all right boundary elements to -3 and fill the 
        # subdiagonal entry with 1 (corresponding to the node on the left hand side 
        # of the right boundary element element).
        for i in range(1, N+1):
            A[i*N - 1, i*N - 1] = -3
            A[i*N - 1, i*N - 2] = 1
    
        # Change the subdiagonal entries for all left boundary values to 1
        # (corresponding to the node on the right hand side of the left boundary element)
        for i in range(0, N):
            A[i*N, i*N + 1] = 1
    
        # Check if our grid contains elements inbetween the corner elements and
        # in that case fill the super and subdiagonal elements on the same row with 
        # 1, corresponding to the left and right nodes with respect to these elements
        if N > 2:
            for i in range(0, N):
                for j in range(i*N + 1, i*N + N - 1):
                    A[j, j - 1] = 1
                    A[j, j + 1] = 1


        """ Create b (without the values from the Neumann conditions given by
            room 2)
        """
        b = np.zeros(size)

        # Subtract the top boundary nodes with self.wall_temp
        for i in range(0, N):
            b[i] = b[i] - self.wall_temp
        
        # Subtract the bottom boundary nodes with self.wall_temp
        for i in range(size-N,size):
            b[i] = b[i] - self.wall_temp
        
            
        # Subtract the most-left (near the left boundary elements) with self.heater_temp
        for i in range(0, N):
            b[i*N] = b[i*N] - self.heater_temp
        
        self.A = sp.csc_matrix(A,dtype=float).todense()
        self.b = b
    
    
    def update_b_room1_room3(self, gamma):
        """ 
        [Updating b]
        Updates the matrix b by subtracting the right border elements with the
        new Neumann-condition values in every iteration.
        """
        N = self.N
        
        # Subtract the most-right (near the right boundary) nodes with the 
        # corresponding value given for the node by Neumann-conditions
        for i in range(1, N+1):
            self.b[i*N - 1] =  -gamma[i-1]
            
        # For the corner elements, subtract the self.wall_temp as well
        self.b[N-1] -= self.wall_temp 
        self.b[-1] -= self.wall_temp       
            
        
    
    def create_A_and_b_room2(self):
        """ Initializes the matrices A and b for room 2. 
            For room 2, b will change in every iteration, while A is CONSTANT """
        height = 2                          # heigth of room 2
        M = int(round(height/self.dx)) - 1  # number of rows of nodes
        N = self.N                          # number of cols of nodes
        size = M*N                          # number of unknown nodes
                
        """ Create A """
        # The bulk of A is very close to a toeplitz matrix with 5 diagonals.
        first_row = np.zeros(size)
        first_row[0] = -4
        first_row[1] = 1
        first_row[N] = 1
        A = sl.toeplitz(first_row, first_row)
        
        # The two inner super- and subdiagonals of this toeplitz matrix need to
        # be modified. Specifically, every N:th element should be set to zero,
        # for a total of (M-1) times, since our grid has M rows, and only the
        # first element to be set to zero goes "outside" of the matrix A.
        #
        # SUB: first zero goes in row N.
        row = N
        for i in range(M-1):
            A[row, row-1] = 0
            row += N
        
        # SUPER: first zero goes in row N-1.
        row = N-1
        for i in range(M-1):
            A[row, row+1] = 0
            row += N
        
        
        # [Building b].
        # Room 2 has 6 different (Dirichlet) boundaries. Of these, 2 change in every
        # iteration, while 4 are constant. Here we initialize b,considering only the 
        # 4 constant boundary conditions, while the other 2 are considered in 
        # update_b_room2(), called in every iteration in solve().
        b = np.zeros(size)
        
        # Upper bounndary:
        b[:N] = -self.heater_temp
        
        # Lower boundary:
        b[-N:] = -self.window_temp
        
        # Upper left boundary:
        # Every N nodes are effected by the upper left boundary, and in total 
        # N+1 nodes are effected. The first effected node is the 0:th node.
        index = 0
        for i in range(N+1):
            b[index] -= self.wall_temp
            index += N
        
        # Lower right boundary:
        # Every N nodes are effected by the upper left boundary, and in total 
        # N+1 nodes are effected. The first effected node is the (N^2+(N-1)):th node.
        index = N**2 + (N-1)
        for i in range(N+1):
            b[index] -= self.wall_temp
            index += N
        self.A = sp.csc_matrix(A,dtype=float).todense()
        self.b = b        


    def update_b_room2(self, gamma1, gamma2):
        """ Updates the b-matrix for room 2, according to values in gamma1 and
            gamma2. Note that for room 2, the A-matrix is constant.
        """        
        # Upper right boundary:
        # Every N nodes are effected by the upper right boundary, and in total 
        # N nodes are effected. The first effected node is the (N-1):th node.
        N = self.N
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
            
        # Two corners:
        # The above code has overwritten the b-values at two corners. There, the b-vector 
        # should only have contributions from the outer wall:
        self.b[N-1] -= self.heater_temp
        self.b[-N] -= self.window_temp



    """   
        _______________________________________MAYBE_README___________________________________________     
        In solve(), note that the vectors gamma1 and gamma2 store different things depending on      
        what room uses it. When a room2-object returns gamma1 and gamma2 to room 1 and 3 respectively, 
        they contain the difference of the temperature at these two boundaries. When room1-
        and room3-objects return these vectors, they store temperature values.
        generates room 1 aka omega_1
    """
    def solve(self):
        room = self.room
        N = self.N

        if room == 1:
            # gamma1 is here (and in room 3) initialized arbitrarily as a first guess.
            # We chose the average of all the wall temperatures of the room.
            gamma1 = np.ones(N)*(self.heater_temp + 2*self.wall_temp)/3
            gamma1_km1 = gamma1
            self.com.send(gamma1,dest=1)
            if self.debug:
                time_1 = time.time()*1000
            for i in range(self.max_iters):
                if self.debug:
                    print('Time since last iteration = ' + str(time.time()*1000-time_1)+'ms')
                    print('Omega 1 iteration : ' + str(i)+'\n')
                    time_1 = time.time()*1000
                    sys.stdout.flush()
                gamma1 = self.com.recv(source=1)
                
                if gamma1 is False: # We are done with our iteration.
                    gamma1 = gamma1_km1
                    break
                

                self.update_b_room1_room3(gamma=gamma1)

                u  = sl.solve(self.A,self.b)                

                # We want to update gamma1 to only contain the temperature values of the boundary nodes
                # that lie between room 1 and 2, since this will be used for the Dirichlet conditions
                # in room 2 in the next iteration. This is done by utilizing the Neumann condition and 
                # gamma1 that was supplied by room 2. 
                gamma1_temp = u[N-1::N]
                if i != 0:
                    gamma1 = self.omega*(gamma1_temp + gamma1) + (1-self.omega)*gamma1_km1                                
                    self.com.send(gamma1,dest=1)
                    u = self.omega*u + (1-self.omega)*self.u_km1
                else:
                    gamma1 = gamma1_temp + gamma1
                    self.com.send(gamma1,dest=1)
                    
                gamma1_km1 = gamma1
                self.u_km1=u
                
            return u, gamma1
        
        if room == 2:
            for j in range(self.max_iters):
                gamma1 = self.com.recv(source=0)
                gamma2 = self.com.recv(source=2)
                
                self.update_b_room2(gamma1=gamma1, gamma2=gamma2)
                
                U  = sl.solve(self.A,self.b)

                gamma1_temp = U[N**2+N::N]
                gamma2_temp = U[N-1::N]
                gamma2_temp = gamma2_temp[:N]

                # the Neumann conditions, since we do the same for 
                # our A matrices.
                gamma1 = gamma1_temp - gamma1 
                gamma2 = gamma2_temp - gamma2

                # Send these gammas to room 1 and 3 -- unless we are done,
                # in which case we send "False" to communicate this.
                if j == 0:
                    self.com.send(gamma1,dest=0)
                    self.com.send(gamma2,dest=2)
                else:                    
                    if sl.norm(U - self.u_km1, 2) < self.tol:
                        self.max_iters = j+1
                        print('Algorithm finished after ' + str(j+1) + ' iterations.')
                        self.com.send(False, dest=0)
                        self.com.send(False, dest=2)
                        break
                    else:
                        self.com.send(gamma1,dest=0)
                        self.com.send(gamma2,dest=2)
                        
                # Relaxation:                        
                if j != 0:
                    U = self.omega*U + (1-self.omega)*self.u_km1
                
                self.u_km1 = U
                
                if self.debug:
                    print('Omega 2 iteration : ' + str(j)+'\n')
                    sys.stdout.flush()
            return U, None

        if room == 3:
            gamma2 = np.ones(N)*(self.heater_temp + 2*self.wall_temp)/3
            gamma2_km1 = gamma2
            self.com.send(gamma2,dest=1)
            
            for k in range(self.max_iters):
                gamma2 = self.com.recv(source=1)
                if gamma2 is False: # We are done with our iteration.
                    gamma2 = gamma2_km1
                    break
                
                self.update_b_room1_room3(gamma=gamma2)
                u = sl.solve(self.A,self.b)
                  

                gamma2_temp = u[N-1::N]
                
                if k != 0:
                    u = self.omega*u + (1-self.omega)*self.u_km1
                    gamma2 = self.omega*(gamma2_temp + gamma2) + (1-self.omega)*gamma2_km1
                    self.com.send(gamma2,dest=1)
                else:
                    gamma2 = gamma2_temp +gamma2
                    self.com.send(gamma2,dest=1)
                    
                if self.debug:
                    print('Omega 3 iteration : ' + str(k)+'\n')
                    sys.stdout.flush()
                
                self.u_km1=u
                gamma2_km1 = gamma2
            return u, gamma2
        
    def plot_apartment(self,U1,U2,U3,gamma1,gamma2):
        fig, ax = plt.subplots()
        dx = self.dx
        N = self.N  #int(1/dx-1)
        M = int(2/dx -1)  #int(2/dx-1)  
        #assemble_room_1
        # 3 boundaries, size (N+2)*(N+1)
        
        room1 = np.zeros((N+2,N+1)) # np.linspace(1,2,(N+2)*(N+1)).reshape(((N+2),(N+1)))
        room1[1:-1,1:] = U1.reshape((N,N))
        room1[:,0] = self.heater_temp
        room1[0,:] = self.wall_temp
        room1[-1,:] = self.wall_temp
        room1[0,0] = (self.wall_temp+self.heater_temp)/2
        room1[-1,0] = (self.wall_temp+self.heater_temp)/2
        # assemble room_2
        # six bounadies
        
        room2= np.zeros((M+2,N+2))
        room2[1:-1,1:-1] = U2.reshape((M,N))
        room2[0,:]= self.heater_temp # upper boundary
        room2[1:N+1,-1] = gamma2 # gamma 2 boundary
        room2[N+1:,-1] = self.wall_temp 
        room2[-1,:] = self.window_temp
        room2[N+2:-1,0] = gamma1 # gamma 1 bound
        room2[:N+2,0] = self.wall_temp
        room2[0,0] = (self.wall_temp+self.heater_temp)/2
        room2[0,-1] = (self.wall_temp+self.heater_temp)/2
        room2[-1,0] = (self.wall_temp+self.window_temp)/2
        #assemble_room_3
        # 3 boundaries, size (N+2)*(N+1)

        room3= np.zeros((N+2,N+1)) #np.ones((N+2,N+1))
        room3[1:-1,:-1] = np.flip(U3.reshape((N,N)),axis=1)
        room3[:,-1] = self.heater_temp
        room3[0,:] = self.wall_temp
        room3[-1,:] = self.wall_temp
        room3[0,-1] = (self.wall_temp+self.heater_temp)/2
        room3[-1,-1] = (self.wall_temp+self.heater_temp)/2
        #Assemble heat map
        
        Map = np.zeros((M+2,N*3+4))
        Map[-(N+2):,:N+1] = room1 #room 1
        Map[:,N+1:N*2+3] = room2 # room 2
        Map[0:N+2,N*2+3:] = room3 # room 3
        
        X, Y = np.meshgrid(np.linspace(-dx/2, 3+dx/2, (N*3+4)),np.linspace(2+dx/2, -dx/2, (M+2)))
        levels = MaxNLocator(nbins=50).tick_values(Map.min(), Map.max())
        # make the plot
        #c = ax.pcolormesh(X, Y, Map, cmap='RdBu', vmin=0, vmax=Map.max(),)
        #y, x = np.mgrid[slice(0, 2 + dx, dx),slice(0, 3 + dx, dx)]
        cf = ax.contourf(X[:, :], Y[:, :], Map,levels=levels, cmap='RdBu_r')
        
        # plt.imshow(Map) # Second plot
        # plt.colorbar()
        ax.axis([X.min(), X.max(), Y.min(), Y.max()])
        fig.colorbar(cf, ax=ax)
        plt.axis('equal')
        plt.title('Iterations = ' + str(self.max_iters) + '. Mesh width = ' + str(self.dx)+'m') 
        plt.show()
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