import csv
import os
import random

# TODO fix this it generates full mazes (no free spaces)
def generate_maze(width, height):
    maze = [[255 for _ in range(width)] for _ in range(height)]
    
    def carve_passages(x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 255:
                if sum(maze[ny+dy][nx+dx] == 0 for dx, dy in directions) == 1:
                    maze[y][x] = 0
                    maze[ny][nx] = 0
                    carve_passages(nx, ny)
    
    # Start the maze generation
    carve_passages(1, 1)
    
    return maze

def save_maze_to_csv(maze, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(maze)

# Parameters
width = 150
height = 100
directory = 'Dstar-lite-pathplanner/maps/'
filename = 'maze.csv'
filepath = os.path.join(directory, filename)

# Generate and save the maze
maze = generate_maze(width, height)
save_maze_to_csv(maze, filepath)

print(f'Maze saved to {filepath}')