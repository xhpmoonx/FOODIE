import numpy as np
import random

MAP_SIZE = 30 # The width and height of the square grid 
OBSTACLE_RATIO = 0.22 # The fraction of the grid to fill with obstacles
FW_LOCATION = (0, 0)

def generate_map(size=MAP_SIZE, obstacle_ratio=OBSTACLE_RATIO):
    grid = np.zeros((size, size), dtype=int) # Creates a 2D numpy array filled with zeros
    num_obstacles = int(size * size * obstacle_ratio) # Determines how many obstacles to place based on the ratio
    obstacles = set()
    
    # Random Obstacle Placement:
    while len(obstacles) < num_obstacles:
        x, y = random.randint(0, size - 1), random.randint(0, size - 1)
        if (x, y) != FW_LOCATION:
            obstacles.add((x, y))
            grid[x, y] = 1

    return grid, obstacles