import heapq
import numpy as np
from collections import deque
import heapq


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


def dfs(grid, start, goal):
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    stack = [(start, [start])]  # (current_position, path_so_far)
    visited = set()

    while stack:
        current, path = stack.pop()

        if current == goal:
            return path

        if current in visited:
            continue
        visited.add(current)

        for i, j in neighbors:
            neighbor = (current[0] + i, current[1] + j)

            if (0 <= neighbor[0] < grid.shape[0] and
                0 <= neighbor[1] < grid.shape[1] and
                grid[neighbor[0]][neighbor[1]] == 0 and
                neighbor not in visited):
                stack.append((neighbor, path + [neighbor]))

    return None  # No path found


def bfs(grid, start, goal):
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1,-1), (1,-1), (-1,1), (1,1)]
    visited = set()
    queue = deque()
    came_from = {}

    queue.append(start)
    visited.add(start)

    while queue:
        current = queue.popleft()

        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j

            if (0 <= neighbor[0] < grid.shape[0] and
                0 <= neighbor[1] < grid.shape[1] and
                grid[neighbor[0]][neighbor[1]] == 0 and
                neighbor not in visited):
                
                queue.append(neighbor)
                visited.add(neighbor)
                came_from[neighbor] = current

    return None  # No path found


def dijkstra(grid, start, goal):
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    visited = set()
    min_heap = []
    heapq.heappush(min_heap, (0, start))  # (cost, position)
    came_from = {}
    cost_so_far = {start: 0}

    while min_heap:
        current_cost, current = heapq.heappop(min_heap)

        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        if current in visited:
            continue
        visited.add(current)

        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            if (0 <= neighbor[0] < grid.shape[0] and
                0 <= neighbor[1] < grid.shape[1] and
                grid[neighbor[0]][neighbor[1]] == 0):
                
                new_cost = current_cost + 1  # cost between nodes is uniform (1)

                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    heapq.heappush(min_heap, (new_cost, neighbor))
                    came_from[neighbor] = current

    return None  # No path found
