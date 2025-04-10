from map import generate_map
from simulation import Simulation
from pathfinding import astar
from data import sample_robots,warehouse_location
from config import sample_orders


if __name__ == '__main__':
    campus_map, _ = generate_map() # Returns a representation of the environmen
    available_robots = sample_robots[:]  # make a copy so we can remove assigned ones

    # Loop over each predefined order to assign it to the closest available robot
    for order in sample_orders:
        closest_robot = None
        shortest_path = None

        # Check each available robot for the shortest valid path to the order location
        for robot in available_robots:
            path = astar(campus_map, robot.position, order['location'])
            if path and (shortest_path is None or len(path) < len(shortest_path)):
                closest_robot = robot
                shortest_path = path

        # If a valid robot and path were found, assign the order
        if closest_robot and shortest_path:
            order['assigned'] = True
            closest_robot.set_path(shortest_path, order)
            available_robots.remove(closest_robot)
        else:
            print(f"[ERROR] No valid robot for Order {order['order_id']} at {order['location']}")
    
    ''' # Prevoius Version Used to Zip the orders to robots in parallel
        for robot, order in zip(sample_robots, sample_orders):
        path = astar(campus_map, robot.position, order['location'])
        if path:
            order['assigned'] = True
            robot.set_path(path, order)
        else:
            print(f"[ERROR] No valid path for Robot {robot.robot_id} to Order {order['order_id']} at {order['location']}")

    '''
    # Initialize and start the simulation with the map, orders, and robots
    sim = Simulation(campus_map, sample_orders, sample_robots)
    sim.run() # Launches the visual simulation using Pygame
