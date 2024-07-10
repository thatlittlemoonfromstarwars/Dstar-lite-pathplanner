# imports
import numpy as np

# processing function
def plan_adjusted_path(path, world_map, robot_pos, goal_pos):
    '''
    Inputs:
    path - list of (x,y) coordinates - path planned by unaltered D* Lite algorithm
        NOTE: these are in order from closest to robot, to closest to goal
    
    world_map - Integer 100x150 numpy matrix - represents the map of the environment
        - 255 represents an obstacle
        - 0 represents a clear square (can be driven in)

        Matrix format:
        |----------> y, column
        |           (x=0,y=2)
        |
        V (x=2, y=0)
        x, row

        NOTE: x in this simulator represents the vertical axis, while y represents the horizontal axis

    robot_pos - (x,y) coordinate - current position of robot
    goal_pos - (x,y) coordinate - current position of goal
    '''
    altered_path = [] # list of coordinates representing the new path

    ############################################# ALTERATION CODE GOES HERE #############################################
    for x, y in path:
        altered_path.append((x-1, y+1))

    #####################################################################################################################

    return altered_path