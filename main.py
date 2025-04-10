from map import generate_map
from simulation import Simulation
from pathfinding import astar
from data import sample_robots,warehouse_location
from config import sample_orders


if __name__ == '__main__':
    campus_map, _ = generate_map()
    for robot, order in zip(sample_robots, sample_orders):
        path = astar(campus_map, robot.position, order['location'])
        if path:
            order['assigned'] = True
            robot.set_path(path, order)
        else:
            print(f"[ERROR] No valid path for Robot {robot.robot_id} to Order {order['order_id']} at {order['location']}")

    sim = Simulation(campus_map, sample_orders, sample_robots)
    sim.run()
