import pygame
import sys
import random
from config import MAP_SIZE, FW_LOCATION
from pathfinding import astar
import numpy as np

CELL_SIZE = 30
GRID_COLOR = (200, 200, 200)
OBSTACLE_COLOR = (0, 0, 0)
ROBOT_COLOR = (255, 165, 0)
ORDER_COLOR = (150, 150, 150)         # New order (unassigned) - Gray-ish
ASSIGNED_ORDER_COLOR = (255, 0, 0)  # Assigned (not yet picked up) - Red
DELIVERED_ORDER_COLOR = (0, 200, 0)  # Delivered - Green
WAREHOUSE_COLOR = (0, 0, 255)
MAX_ORDERS_PER_ROBOT = 4

"""This class handles individual robot behavior

"""
class Robot:
    def __init__(self, robot_id, position):
        self.robot_id = robot_id
        self.position = position
        self.path = [] # List of positions to follow
        self.busy = False # Whether robot is currently delivering
        #self.target_order = None # The assigned order
        self.orders_queue = []  # Queue of orders
        self.move_delay = 0 # Simulate speed control
        self.waiting = False
        self.wait_start_time = None
        self.at_warehouse = True

    """
    # Stores a path and links it to an order. Starts moving if a path is set.
    def set_path(self, path, order):
        self.path = path[1:] if path else []
        self.busy = bool(self.path)
        self.target_order = order
    """
    # Adds a new delivery to the robot's task list and sets its next path if idle.
    def add_order(self, path, order):
        self.orders_queue.append(order)
        self.busy = True
        if not self.path:
            self.path = path[1:]

    #This method is called after a robot finishes its current path. It determines what the robot should do next.
    def proceed_to_next_task(self):
        if self.orders_queue:
            completed_order = self.orders_queue.pop(0)
            completed_order['delivered'] = True
            next_target = self.orders_queue[0]['location'] if self.orders_queue else FW_LOCATION
            path = astar(self.grid, self.position, next_target)
            if path:
                self.path = path[1:]
            else:
                print(f"[ERROR] Robot {self.robot_id} cannot find path to {next_target} from {self.position}")
        else:
            if self.position != FW_LOCATION:
                path = astar(self.grid, self.position, FW_LOCATION)
                if path:
                    self.path = path[1:]
                self.busy = True
            else:
                self.busy = False

    # Scans a 5x5 square centered on the robot to find the Manhattan distance to the closest obstacle     
    def distance_to_nearest_obstacle(self):
        x, y = self.position
        min_dist = float('inf')
        for i in range(max(0, x-2), min(len(self.grid), x+3)):
            for j in range(max(0, y-2), min(len(self.grid[0]), y+3)):
                if self.grid[i][j] == 1:
                    dist = np.sqrt(((i - x )**2)+((j-y)**2))
                    #dist = abs(i - x) + abs(j - y)
                    if dist < min_dist:
                        min_dist = dist
        return min_dist
    
    # Chooses a speed mode based on how close the robot is to an obstacle
    def get_speed_mode(self):
        dist = self.distance_to_nearest_obstacle()
        if dist <= 1:
            return "cautious"  # slow
        elif dist <= 3:
            return "normal"    # medium
        else:
            return "fast"      # fast
        
    # Controls how the robot moves in each simulation tick
    def move(self):
        # If robot is at warehouse and idle, begin waiting
        if self.at_warehouse and not self.path and not self.waiting:
            self.waiting = True
            self.wait_start_time = pygame.time.get_ticks()

        # Wait 5 seconds (5000 milliseconds)
        if self.waiting:
            if pygame.time.get_ticks() - self.wait_start_time >= 5000:
                self.waiting = False
                self.at_warehouse = False  # done waiting
            else:
                return  # still waiting, do nothing

        # Standard movement logic
        ...
        if self.path:
            self.position = self.path.pop(0)

        if not self.path:
            self.proceed_to_next_task()

        # Check if robot is back at warehouse
        if self.position == FW_LOCATION and not self.orders_queue:
            self.at_warehouse = True

    '''
    # Controls how the robot moves in each simulation tick
    def move(self):
        # Determine Robot's speed
        speed_mode = self.get_speed_mode()
        delay_map = {"fast": 1, "normal": 2, "cautious": 3}
        self.move_delay += 1
        if self.move_delay < delay_map[speed_mode]:
            return
        self.move_delay = 0

        # Takes the next step on the path
        if self.path:
            self.position = self.path.pop(0)

        # If order just delivered, go back to warehouse
        if not self.path and self.target_order:
            self.target_order['delivered'] = True
            self.target_order = None
            from pathfinding import astar
            path_back = astar(self.grid, self.position, FW_LOCATION)
            if path_back:
                self.path = path_back[1:]
                self.busy = True
            else:
                print(f"[ERROR] Robot {self.robot_id} cannot return to warehouse from {self.position}")

        # If no path and no target, free to take new order
        if not self.path and not self.target_order:
            self.busy = False
    '''

"""Handles the whole simulation loop, screen drawing, event handling, and robot coordination.

"""
class Simulation:
    def __init__(self, grid, orders, robots):
        pygame.init()
        self.grid = grid
        self.orders = orders
        self.robots = robots
        self.screen = pygame.display.set_mode((MAP_SIZE * CELL_SIZE, MAP_SIZE * CELL_SIZE + 40))
        pygame.display.set_caption("FOODIE Simulation")
        self.clock = pygame.time.Clock()
        self.elapsed_seconds = 0
        self.order_id_counter = len(orders) + 1
        self.font = pygame.font.SysFont(None, 28)
        for robot in self.robots:
            robot.grid = self.grid
    def assign_orders_in_batch(self):
    # Filter unassigned orders
        unassigned = [o for o in self.orders if not o['assigned']]
        random.shuffle(unassigned)  # Randomize to avoid bias

        for robot in [r for r in self.robots if r.at_warehouse and not r.busy]:
            if not unassigned:
                break

            # Take one order and try to find nearby ones
            base_order = unassigned.pop(0)
            group = [base_order]

            # Group nearby orders up to MAX
            for other in unassigned[:]:
                dx = base_order['location'][0] - other['location'][0]
                dy = base_order['location'][1] - other['location'][1]
                if dx * dx + dy * dy <= 25:  # radius squared = 5^2
                    group.append(other)
                    unassigned.remove(other)
                    if len(group) == MAX_ORDERS_PER_ROBOT:
                        break

            # Assign all grouped orders to robot
            last_pos = robot.position
            for order in group:
                path = astar(self.grid, last_pos, order['location'])
                if path:
                    robot.add_order(path, order)
                    order['assigned'] = True
                    last_pos = order['location']
                else:
                    print(f"[ERROR] No path for robot {robot.robot_id} to order {order['order_id']}")
            print(f"[INFO] Robot {robot.robot_id} assigned orders {[o['order_id'] for o in group]}")


    def generate_order(self):
        while True:
            x, y = random.randint(0, MAP_SIZE - 1), random.randint(0, MAP_SIZE - 1)
            if self.grid[x][y] == 0 and (x, y) != FW_LOCATION:
                return {'order_id': self.order_id_counter, 'location': (x, y), 'assigned': False, 'delivered': False}

    def assign_order(self, order):
        # Helper to find nearby unassigned orders
        def find_nearby_orders(base_order, radius=5):
            neighbors = []
            for other in self.orders:
                if not other['assigned'] and other != base_order:
                    dx = other['location'][0] - base_order['location'][0]
                    dy = other['location'][1] - base_order['location'][1]
                    if dx * dx + dy * dy <= radius * radius:
                        neighbors.append(other)
            return neighbors

        # Only consider robots at the warehouse and not busy
        candidates = [robot for robot in self.robots if robot.at_warehouse and not robot.busy]

        if not candidates:
            return False

        # Get nearby unassigned orders
        nearby_orders = find_nearby_orders(order)
        selected_orders = [order]

        # Try to include up to MAX_ORDERS_PER_ROBOT orders
        for o in nearby_orders:
            if len(selected_orders) < MAX_ORDERS_PER_ROBOT:
                selected_orders.append(o)

        # Assign all selected orders to the best robot
        best_robot = None
        best_score = float('inf')

        for robot in candidates:
            total_distance = 0
            last_pos = robot.position
            valid = True
            for o in selected_orders:
                path = astar(self.grid, last_pos, o['location'])
                if path:
                    total_distance += len(path)
                    last_pos = o['location']
                else:
                    valid = False
                    break
            if valid and total_distance < best_score:
                best_score = total_distance
                best_robot = robot

        if best_robot:
            last_pos = best_robot.position
            for o in selected_orders:
                path = astar(self.grid, last_pos, o['location'])
                best_robot.add_order(path, o)
                o['assigned'] = True
                last_pos = o['location']
            self.orders.extend(o for o in selected_orders if o not in self.orders)
            print(f"[INFO] Robot {best_robot.robot_id} assigned orders {[o['order_id'] for o in selected_orders]}")
            return True

        return False


    """
    def assign_order(self, order):
        for robot in self.robots:
            if not robot.busy:
                path = astar(self.grid, robot.position, order['location'])
                if path:
                    order['assigned'] = True
                    robot.set_path(path, order)
                    print(f"[INFO] Assigned Order {order['order_id']} to Robot {robot.robot_id}")
                    self.orders.append(order)
                    return True
        return False """

    def draw_grid(self):
        self.screen.fill((255, 255, 255))
        for x in range(MAP_SIZE):
            for y in range(MAP_SIZE):
                rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.grid[x][y] == 1:
                    pygame.draw.rect(self.screen, OBSTACLE_COLOR, rect)
                else:
                    pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

        wx, wy = FW_LOCATION
        pygame.draw.rect(self.screen, WAREHOUSE_COLOR, (wy * CELL_SIZE, wx * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        for order in self.orders:
            ox, oy = order['location']
            if order.get('delivered'):
                color = DELIVERED_ORDER_COLOR
            elif order.get('assigned'):
                color = ASSIGNED_ORDER_COLOR
            else:
                color = ORDER_COLOR
            pygame.draw.circle(self.screen, color, (oy * CELL_SIZE + 15, ox * CELL_SIZE + 15), 10)

        for robot in self.robots:
            rx, ry = robot.position
            pygame.draw.rect(self.screen, ROBOT_COLOR, (ry * CELL_SIZE + 5, rx * CELL_SIZE + 5, 20, 20))

        info_text = self.font.render(f"Orders Generated: {self.order_id_counter - 1}", True, (0, 0, 0))
        self.screen.blit(info_text, (10, MAP_SIZE * CELL_SIZE + 10))

    def run(self):
        running = True
        while running:
            self.clock.tick(10)
            self.elapsed_seconds += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Every 3 seconds, generate one new order
            if self.elapsed_seconds % 3 == 0:
                new_order = self.generate_order()
                new_order['order_id'] = self.order_id_counter
                self.orders.append(new_order)
                self.order_id_counter += 1

            # On the next tick, assign any unassigned orders in batch
            if self.elapsed_seconds % 3 == 1:
                self.assign_orders_in_batch()

            for robot in self.robots:
                robot.move()

            self.draw_grid()
            pygame.display.flip()

        pygame.quit()
        sys.exit()
