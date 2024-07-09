import numpy as np
import random
import csv

def create_maze(grid, x, y, width, height, min_width):
    if width < min_width * 2 or height < min_width * 2:
        return

    horizontal = random.choice([True, False])
    
    if horizontal:
        if height - 2 * min_width <= 0:
            return
        
        wall_y = random.choice(range(y + min_width, y + height - min_width, min_width))
        passage_x = random.choice(range(x, x + width - min_width, min_width))
        for i in range(x, x + width):
            if not (passage_x <= i < passage_x + min_width):
                grid[wall_y:wall_y + min_width, i] = 0

        create_maze(grid, x, y, width, wall_y - y, min_width)
        create_maze(grid, x, wall_y + min_width, width, y + height - wall_y - min_width, min_width)
    else:
        if width - 2 * min_width <= 0:
            return
        
        wall_x = random.choice(range(x + min_width, x + width - min_width, min_width))
        passage_y = random.choice(range(y, y + height - min_width, min_width))
        for i in range(y, y + height):
            if not (passage_y <= i < passage_y + min_width):
                grid[i, wall_x:wall_x + min_width] = 0

        create_maze(grid, x, y, wall_x - x, height, min_width)
        create_maze(grid, wall_x + min_width, y, x + width - wall_x - min_width, height, min_width)

def generate_random_maze(grid_size=(100, 150), min_path_width=2):
    maze = np.ones(grid_size, dtype=int)
    create_maze(maze, 0, 0, grid_size[1], grid_size[0], min_path_width)
    return maze

def save_grid_to_csv(matrix, file_path):
    matrix = matrix.astype(int)
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in matrix:
            writer.writerow(row)

# Example usage
maze = generate_random_maze()
save_path = 'Dstar-lite-pathplanner\maps\\'
save_grid_to_csv(maze, save_path)
print('Maze successfully generated.')