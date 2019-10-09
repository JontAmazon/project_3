# -*- coding: utf-8 -*-



class Room(object):
    
    def __init__(self,kwargs, rank, d_x = 1/3):
        ''' initalizes the room object for the corresponding 
        '''
        self.room = rank + 1
        self.wall_temp = 273.15 + 15 #deg kelvin
        self.heater_temp = 273.15 + 40 #deg kelvin
        self.window_temp = 273.15 + 5 #deg kelvin

        assert (rank < 4),'The rank is too high, you might be trying to initiate too many instances'
        if room == 1:
            self.A,self.b,self.U = self.room_omega_1()
        elif room == 2:
            self.A,self.b,self.U = self.room_omega_2()
        else:
            self.A,self.b,self.U = self.room_omega_3()

    def room_omega_1():
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
        # A=
        # B =
        # U = uvektorn för rum 1
        return A,b,U
    def room_omega_2():
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
        # A=
        # B =
        # U
        return A,b,U
    def room_omega_3():
        ''' generates room 1 aka omega_3
                
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
        # A=
        # B =
        # U =
        return A,b,U