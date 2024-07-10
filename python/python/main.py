from gui import Animation
from d_star_lite import DStarLite
from grid import OccupancyGridMap, SLAM
from post_process_path import plan_adjusted_path
import csv
import numpy as np

OBSTACLE = 255
UNOCCUPIED = 0

LOAD_FILE_PATH = 'Dstar-lite-pathplanner/maps/lab_filled_in.csv'
# LOAD_FILE_PATH = None

if __name__ == '__main__':

    """
    set initial values for the map occupancy grid
    |----------> y, column
    |           (x=0,y=2)
    |
    V (x=2, y=0)
    x, row
    """
    x_dim = 100
    y_dim = 150
    start = (10, 10)
    goal = (60, 90)
    view_range = 10

    gui = Animation(title="D* Lite Path Planning",
                    width=10,
                    height=10,
                    margin=0,
                    x_dim=x_dim,
                    y_dim=y_dim,
                    start=start,
                    goal=goal,
                    viewing_range=view_range)

    # Load prexisting world from CSV
    if LOAD_FILE_PATH is not None:
        try:
            # read csv file to matrix
            with open(LOAD_FILE_PATH, 'r') as csvfile:
                reader = csv.reader(csvfile)
                matrix = np.array([list(map(int, row)) for row in reader])
            gui.world.set_map(matrix)
        except:
            print("Unable to open file. Continuing with empty map.")

    new_goal = gui.goal
    old_goal = new_goal

    new_map = gui.world
    old_map = new_map

    new_position = start
    last_position = start

    # D* Lite (optimized)
    dstar = DStarLite(map=new_map,
                      s_start=start,
                      s_goal=goal)

    # SLAM to detect vertices
    slam = SLAM(map=new_map,
                view_range=view_range)

    # move and compute path
    path, g, rhs = dstar.move_and_replan(robot_position=new_position)

    # post process path
    path_adjusted = plan_adjusted_path(path, gui.world, gui.current, gui.goal)

    while not gui.done:
        # update the map
        # drive gui
        gui.run_game(path=path, path_adjusted=path_adjusted)

        new_position = gui.current # contains robot location
        new_observation = gui.observation
        new_map = gui.world # contains map matrix (255 for obstacle, 0 for free space)
        new_goal = gui.goal # contains goal location

        if new_observation is not None:
            old_map = new_map
            slam.set_ground_truth_map(gt_map=new_map)

        if new_position != last_position:
            last_position = new_position

            # slam
            new_edges_and_old_costs, slam_map = slam.rescan(global_position=new_position)

            dstar.new_edges_and_old_costs = new_edges_and_old_costs
            dstar.sensed_map = slam_map

            # d star
            path, g, rhs = dstar.move_and_replan(robot_position=new_position) # path holds the list of coordinates in the path

            # altered path
            path_adjusted = plan_adjusted_path(path, gui.world, gui.current, gui.goal)

        if new_goal != old_goal:
            old_goal = new_goal
            start = gui.current

            new_map = gui.world
            old_map = new_map

            new_position = start
            last_position = start

            # D* Lite (optimized)
            dstar = DStarLite(map=new_map,
                            s_start=start,
                            s_goal=new_goal)

            # SLAM to detect vertices
            slam = SLAM(map=new_map,
                        view_range=view_range)

            # move and compute path
            path, g, rhs = dstar.move_and_replan(robot_position=gui.current)

            # post process path
            path_adjusted = plan_adjusted_path(path, gui.world, gui.current, gui.goal)
