import pygame
import sys
import random
from config import MAP_SIZE, FW_LOCATION
from pathfinding import astar

CELL_SIZE = 30
GRID_COLOR = (200, 200, 200)
OBSTACLE_COLOR = (0, 0, 0)
ROBOT_COLOR = (255, 165, 0)
ORDER_COLOR = (165, 165, 0)
ASSIGNED_ORDER_COLOR = (255, 0, 0)
DELIVERED_ORDER_COLOR = (0, 200, 0)
WAREHOUSE_COLOR = (0, 0, 255)

class Robot:
    def __init__(self, robot_id, position):
        self.robot_id = robot_id
        self.position = position
        self.path = []
        self.busy = False
        self.target_order = None

    def set_path(self, path, order):
        self.path = path[1:] if path else []
        self.busy = bool(self.path)
        self.target_order = order

    def move(self):
        if self.path:
            self.position = self.path.pop(0)
        # If order just delivered, go back to warehouse
        if not self.path and self.target_order:
            self.target_order['delivered'] = True
            self.target_order = None
            from map import FW_LOCATION
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

    def generate_order(self):
        while True:
            x, y = random.randint(0, MAP_SIZE - 1), random.randint(0, MAP_SIZE - 1)
            if self.grid[x][y] == 0 and (x, y) != FW_LOCATION:
                return {'order_id': self.order_id_counter, 'location': (x, y), 'assigned': False, 'delivered': False}

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
        return False

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

            if self.elapsed_seconds % 10 == 0:
                new_order = self.generate_order()
                new_order['order_id'] = self.order_id_counter
                if self.assign_order(new_order):
                    self.order_id_counter += 1
                else:
                    print(f"[INFO] No available robot for Order {new_order['order_id']}, retrying later")

            for robot in self.robots:
                robot.move()

            self.draw_grid()
            pygame.display.flip()

        pygame.quit()
        sys.exit()