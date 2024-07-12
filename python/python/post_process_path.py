# imports
import numpy as np
from copy import deepcopy
from d_star_lite import DStarLite
import math

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

    ############################################### Modify Path Here ####################################################

    # Idea:
    # Compare curvatures of path and inflated path. Use regular path if its curvature is above minimum radius, but use
    # inflated path if not.

    #####################################################################################################################

    return altered_path

# processing function
def inflate_map(world_map, inflation_rad=3):

    height = len(world_map)
    width = len(world_map[0])
    
    visit_map = np.zeros_like(world_map) # this is not used for this simple algorithm, but can be used when optimizing the algorithm
    new_map = np.zeros_like(world_map)

    def draw_filled_circle(center_x, center_y):
        for x in range(-inflation_rad, inflation_rad + 1):
            for y in range(-inflation_rad, inflation_rad + 1):
                if x*x + y*y <= inflation_rad*inflation_rad:
                    set_pixel(center_x + x, center_y + y)

    def set_pixel(x, y):
        # Set new_map element to 1 (indicating filled) if within bounds
        if 0 <= x < height and 0 <= y < width:
            new_map[x][y] = 255

    # Obstacle corner inflation
    # loop through world grid
    for row in range(height):
        for col in range(width):
            if world_map[row][col] == 255:
                # create local map of surrounding grid spaces
                local_map = np.zeros((3,3))
                for i in range(-1,2):
                    for j in range(-1,2):
                        if row + i < 0 or row + i >= height or col + j < 0 or col + j >= width:
                            local_map[i+1][j+1] = -1
                        elif world_map[row + i][col + j] == 255:
                            local_map[i+1][j+1] = 1

                # if straight line exists in local map move on
                if np.all(local_map[1, :] == 1) or np.all(local_map[:, 1] == 1):
                    new_map[row][col] = 255

                # TODO check if grid is near edge
                else:
                    # draw circle around grid space
                    draw_filled_circle(row, col)
    return new_map