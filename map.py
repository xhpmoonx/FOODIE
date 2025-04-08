import numpy as np
import random

MAP_SIZE = 20
OBSTACLE_RATIO = 0.2
FW_LOCATION = (0, 0)

def generate_map(size=MAP_SIZE, obstacle_ratio=OBSTACLE_RATIO):
    grid = np.zeros((size, size), dtype=int)
    num_obstacles = int(size * size * obstacle_ratio)
    obstacles = set()

    while len(obstacles) < num_obstacles:
        x, y = random.randint(0, size - 1), random.randint(0, size - 1)
        if (x, y) != FW_LOCATION:
            obstacles.add((x, y))
            grid[x, y] = 1

    return grid, obstacles