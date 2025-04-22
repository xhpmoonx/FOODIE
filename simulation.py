from itertools import permutations

import pygame
import sys
import random
from config import MAP_SIZE, FW_LOCATION
from pathfinding import astar
import numpy as np

CELL_SIZE = 30                        # Size of each grid cell in pixels
GRID_COLOR = (200, 200, 200)
OBSTACLE_COLOR = (0, 0, 0)
ROBOT_COLOR = (255, 165, 0)
ORDER_COLOR = (150, 150, 150)         # New order (unassigned) - Gray-ish
ASSIGNED_ORDER_COLOR = (255, 0, 0)    # Assigned (not yet picked up) - Red
DELIVERED_ORDER_COLOR = (0, 200, 0)   # Delivered - Green
WAREHOUSE_COLOR = (0, 0, 255)
MAX_ORDERS_PER_ROBOT = 4              # Maximum number of orders a robot can carry once 

"""This class handles individual robot behavior

"""
class Robot:
    def __init__(self, robot_id, position):
        self.robot_id = robot_id        # ID                                               ex: R1
        self.position = position        # Position                                         ex: (0, 0)
        self.path = []                  # List of locations to follow                      ex: [(0, 1), (0, 2), (0, 3)] 
        self.busy = False               # Whether robot is currently delivering            
        self.orders_queue = []          # Queue of orders                                  ex: [{'order_id': 1, 'location': (0, 3), 'assigned': True, 'delivered': False, 'created_time': 10000},{'order_id': 2, 'location': (2, 5), 'assigned': True, 'delivered': False, 'created_time': 11000}]
        self.move_delay = 0             # Simulate speed control
        self.waiting = False            # Whether robot is currently in a wait state
        self.wait_start_time = None     # Timestamp from when waiting started
        self.at_warehouse = True        # Whether the robot is at warehouse
        self.total_delivery_time = 0    # Total time taken for all deliveries
        self.deliveries = 0             # Number of successful deliveries

    '''Adds a new delivery to the robot's task list and sets its next path if idle. '''
    def add_order(self, path, order):
        self.orders_queue.append(order)
        self.busy = True
        if not self.path:
            self.path = path[1:]                            # Skip current location

    '''This method is called after a robot finishes its current path. It determines what the robot should do next. '''
    def proceed_to_next_task(self):
        if self.orders_queue:
            completed_order = self.orders_queue.pop(0)      # Remove the completed order
            completed_order['delivered'] = True             # Mark as delivered
            delivery_time = (pygame.time.get_ticks() - completed_order.get('created_time', 0)) // 1000   # Cal how long the order took to get delivered
            self.total_delivery_time += delivery_time       # Add to delivery time
            self.deliveries += 1                            # Add delivery count
            next_target = self.orders_queue[0]['location'] if self.orders_queue else FW_LOCATION         # Next location
            path = astar(self.grid, self.position, next_target)                                          # Path to next location
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

    '''Scans a 5x5 square centered on the robot to find the Manhattan distance to the closest obstacle '''    
    def distance_to_nearest_obstacle(self):
        x, y = self.position
        min_dist = float('inf')
        for i in range(max(0, x-2), min(len(self.grid), x+3)):              # Bounds doesn't exceed the grid size
            for j in range(max(0, y-2), min(len(self.grid[0]), y+3)):       # Bounds doesn't exceed the grid size
                if self.grid[i][j] == 1:
                    dist = np.sqrt(((i - x )**2)+((j-y)**2))
                    #dist = abs(i - x) + abs(j - y)
                    if dist < min_dist:
                        min_dist = dist
        return min_dist
    
    '''Chooses a speed mode based on how close the robot is to an obstacle '''
    def get_speed_mode(self):
        dist = self.distance_to_nearest_obstacle()
        if dist <= 1:
            return "cautious"  # slow
        elif dist <= 3:
            return "normal"    # medium
        else:
            return "fast"      # fast
        
    '''Controls how the robot moves in each simulation tick '''
    def move(self):
        if self.at_warehouse and not self.path and not self.waiting:         # If robot is at warehouse and idle, begin waiting
            self.waiting = True
            self.wait_start_time = pygame.time.get_ticks()                   # Start waiting timer

        if self.waiting:
            if pygame.time.get_ticks() - self.wait_start_time >= 5000:       # Wait 5 seconds (5000 milliseconds)
                self.waiting = False
                self.at_warehouse = False                                    # Done waiting
            else:
                return                                                       # Still waiting, do nothing
        
        # Standard movement logic :
        if self.path:
            self.position = self.path.pop(0)

        if not self.path:
            self.proceed_to_next_task()

        # Check if robot is back at warehouse
        if self.position == FW_LOCATION and not self.orders_queue:
            self.at_warehouse = True

"""Handles the whole simulation loop, screen drawing, event handling, and robot coordination.

"""
class Simulation:
    def __init__(self, grid, orders, robots):
        pygame.init()                                       # Initialize all pygame modules
        self.grid = grid                                    # Store the warehouse map
        self.orders = orders                                # List of all current orders
        self.robots = robots                                # List of all robot 
        self.screen = pygame.display.set_mode((MAP_SIZE * CELL_SIZE, MAP_SIZE * CELL_SIZE + 120))       # Create a display window
        pygame.display.set_caption("FOODIE Simulation")     # Set the window title
        self.clock = pygame.time.Clock()                    # Create a clock to manage the frame rate
        self.elapsed_seconds = 0                            # How long the simulation has been running
        self.order_id_counter = len(orders) + 1             # Generating unique order IDs
        self.font = pygame.font.SysFont(None, 28)           # GUI font used
        for robot in self.robots:
            robot.grid = self.grid                          # Access to the shared grid

    '''Assign orders to idle robots at the warehouse'''
    def assign_orders_in_batch(self):
        # Filter unassigned orders
        unassigned = [o for o in self.orders if not o['assigned']]
        '''Smart priority: older and closer to warehouse = higher score'''
        def order_priority(order):
            age = (pygame.time.get_ticks() - order.get('created_time', 0)) // 1000      # How many seconds the order was created.
            dx = order['location'][0] - FW_LOCATION[0]                                  # Horizontal distance from warehouse
            dy = order['location'][1] - FW_LOCATION[1]                                  # Vertical distance from warehouse
            dist = (dx * dx + dy * dy) ** 0.5                                           # Euclidean distance
            return age - dist                                                           # higher = better (older & closer)
        
        unassigned.sort(key=order_priority, reverse=True)                               # Sort unassigned orders by smart score
        for robot in [r for r in self.robots if r.at_warehouse and not r.busy]:         # Loop through robots that are currently idle at the warehouse
            if not unassigned:
                break
            base_order = unassigned.pop(0)                                              # Take one order and try to find nearby ones
            group = [base_order]                                                        # Build a group of nearby orders
            base_order['assigned'] = True                                               # mark it early too
            
            # Group nearby orders up to MAX
            for other in unassigned[:]:
                if other['assigned']:
                    continue                                                            # skip already taken orders
                dx = base_order['location'][0] - other['location'][0]
                dy = base_order['location'][1] - other['location'][1]
                if dx * dx + dy * dy <= 25:                                             # Within 5x5 range (squared distance ≤ 25)
                    group.append(other)
                    other['assigned'] = True                                            # pre-assign to lock it
                    unassigned.remove(other)
                    if len(group) == MAX_ORDERS_PER_ROBOT:
                        break

            # Try all permutations of the order group and pick the shortest total path
            best_order_sequence = None
            best_total_distance = float('inf')

            for perm in permutations(group):
                total_distance = 0
                last_pos = robot.position
                valid = True
                for order in perm:
                    path = astar(self.grid, last_pos, order['location'])
                    if not path:
                        valid = False
                        break
                    total_distance += len(path)
                    last_pos = order['location']
                if valid and total_distance < best_total_distance:
                    best_total_distance = total_distance
                    best_order_sequence = perm

            # Assign orders in optimal sequence
            if best_order_sequence:
                last_pos = robot.position
                for order in best_order_sequence:
                    path = astar(self.grid, last_pos, order['location'])
                    robot.add_order(path, order)
                    order['assigned'] = True
                    last_pos = order['location']
                print(f"[INFO] Robot {robot.robot_id} assigned orders {[o['order_id'] for o in best_order_sequence]}")

    '''Generates a random, valid order'''
    def generate_order(self):
        while True:
            x, y = random.randint(0, MAP_SIZE - 1), random.randint(0, MAP_SIZE - 1)
            if self.grid[x][y] == 0 and (x, y) != FW_LOCATION:
                return {
                    'order_id': self.order_id_counter,
                    'location': (x, y),
                    'assigned': False,
                    'delivered': False,
                    'created_time': pygame.time.get_ticks()
                }
    """Old Version  
    '''Assign a specific new order'''
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

    '''Draws the grid, robots, and order states'''
    def draw_grid(self):
        self.screen.fill((255, 255, 255))
        for x in range(MAP_SIZE):
            for y in range(MAP_SIZE):
                rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.grid[x][y] == 1:
                    pygame.draw.rect(self.screen, OBSTACLE_COLOR, rect)
                else:
                    pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

        # Draw warehouse
        wx, wy = FW_LOCATION
        pygame.draw.rect(self.screen, WAREHOUSE_COLOR, (wy * CELL_SIZE, wx * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw orders
        for order in self.orders:
            ox, oy = order['location']
            if order.get('delivered'):
                color = DELIVERED_ORDER_COLOR
            elif order.get('assigned'):
                color = ASSIGNED_ORDER_COLOR
            else:
                # Unassigned - darken gray over time
                age = (pygame.time.get_ticks() - order.get('created_time', 0)) // 1000  # seconds
                shade = max(50, 150 - age * 10)  # gets darker every 1s, stops at 50
                color = (shade, shade, shade)
            pygame.draw.circle(self.screen, color, (oy * CELL_SIZE + 15, ox * CELL_SIZE + 15), 10)

        # Draw robots
        for robot in self.robots:
            rx, ry = robot.position
            pygame.draw.rect(self.screen, ROBOT_COLOR, (ry * CELL_SIZE + 5, rx * CELL_SIZE + 5, 20, 20))

        info_text = self.font.render(f"Orders Generated: {self.order_id_counter - 1}", True, (0, 0, 0))
        self.screen.blit(info_text, (10, MAP_SIZE * CELL_SIZE + 10))
        
        # Draw stats
        self.draw_stats_panel()
    '''Displays delivery stats below the grid'''
    def draw_stats_panel(self):
        panel_top = MAP_SIZE * CELL_SIZE + 10
        line_height = 22
        padding = 10

        # Draw background panel
        pygame.draw.rect(
            self.screen,
            (240, 240, 240),  # light gray background
            (0, MAP_SIZE * CELL_SIZE, MAP_SIZE * CELL_SIZE, 110)
        )

        # Title
        title = self.font.render("Delivery Stats", True, (0, 0, 0))
        self.screen.blit(title, (padding, panel_top))

        # Total orders
        total_orders = self.font.render(f"Total Orders: {self.order_id_counter - 1}", True, (0, 0, 0))
        self.screen.blit(total_orders, (padding, panel_top + line_height))

        # Robot stats
        for i, robot in enumerate(self.robots):
            avg_time = robot.total_delivery_time / robot.deliveries if robot.deliveries else 0
            stats_line = f"{robot.robot_id}: {robot.deliveries} deliveries | avg: {avg_time:.1f}s"
            text = self.font.render(stats_line, True, (0, 0, 0))
            self.screen.blit(text, (padding, panel_top + line_height * (i + 2)))
    
    '''Main simulation loop'''
    def run(self):
        running = True
        while running:
            # Limit the simulation to 10 frames (ticks) per second
            self.clock.tick(10)             
            self.elapsed_seconds += 1

            # Exit the loop if the user closes the window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Every 5 seconds, generate one new order
            if self.elapsed_seconds % 5 == 0:
                new_order = self.generate_order()
                new_order['order_id'] = self.order_id_counter
                self.orders.append(new_order)
                self.order_id_counter += 1

            # On the next tick, assign any unassigned orders in batch
            if self.elapsed_seconds % 5 == 1:
                self.assign_orders_in_batch()
            # Move all robots
            for robot in self.robots:
                robot.move()
            # Redraw the entire screen: grid, robots, orders, warehouse, and stats
            self.draw_grid()
            # Update the visual display with what's been drawn
            pygame.display.flip()
        # After simulation ends, print stats to console
        print("\n==== DELIVERY STATS ====")
        for robot in self.robots:
            avg_time = robot.total_delivery_time / robot.deliveries if robot.deliveries else 0
            print(f"{robot.robot_id}: {robot.deliveries} deliveries, avg time = {avg_time:.2f} sec")
        pygame.quit()
        sys.exit()
