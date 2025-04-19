import numpy as np
import random
from config import  MAP_SIZE, OBSTACLE_RATIO, FW_LOCATION


def generate_map(size=MAP_SIZE, obstacle_ratio=OBSTACLE_RATIO):
    grid = np.zeros((size, size), dtype=int) # Creates a 2D numpy array filled with zeros
    num_obstacles = int(size * size * obstacle_ratio) # Determines how many obstacles to place based on the ratio
    obstacles = set()
    
    # Random Obstacle Placement:
    while len(obstacles) < num_obstacles:
        x, y = random.randint(0, size - 1), random.randint(0, size - 1)
        # Avoiding the warehouse
        if (x, y) != FW_LOCATION:
            obstacles.add((x, y))
            grid[x, y] = 1

    return grid, obstacles