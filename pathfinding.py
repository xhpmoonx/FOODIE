import heapq
import numpy as np

# The “h” score is calculated by Euclidean distance instead of Manhattan distance.
def heuristic(a, b):
    return np.sqrt(((b[0] - a[0] )**2)+((b[1]-a[1])**2))
# Improving Robot Direction movability : The agent can move horizontally and vertically, but also diagonally.
def astar(grid, start, goal):
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1),(-1,-1),(1,-1),(-1,1),(1,1)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = []

    heapq.heappush(oheap, (fscore[start], start))

    while oheap:
        _, current = heapq.heappop(oheap)
        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            data.append(start)
            return data[::-1]

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + 1
            if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]:
                if grid[neighbor[0]][neighbor[1]] == 1:
                    continue
            else:
                continue

            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue

            if tentative_g_score < gscore.get(neighbor, float('inf')):
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))

    return None