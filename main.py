from map import generate_map
from simulation import Simulation
from pathfinding import astar,dfs,bfs,dijkstra
from data import sample_robots,warehouse_location
#from config import sample_orders


if __name__ == '__main__':
    campus_map, _ = generate_map() # Returns a representation of the environment
    """ #TEST#
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
            closest_robot.add_order(shortest_path, order)
            #closest_robot.set_path(shortest_path, order)
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
    #sim = Simulation(campus_map, sample_orders, sample_robots)
    """
    # Initialize and start the simulation with the map, orders, and robots
    sim = Simulation(campus_map, [], sample_robots)
    # Pre-fill with 12 orders
    for _ in range(12):
        new_order = sim.generate_order()
        new_order['order_id'] = sim.order_id_counter
        sim.orders.append(new_order)
        sim.order_id_counter += 1

    sim.assign_orders_in_batch()
    sim.run() # Launches the visual simulation using Pygame
