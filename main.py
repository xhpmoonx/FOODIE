from map import generate_map
from simulation import Simulation, Robot
from pathfinding import astar

sample_orders = [
    {'order_id': 1, 'location': (5, 15), 'assigned': False},
    {'order_id': 2, 'location': (12, 7), 'assigned': False},
    {'order_id': 3, 'location': (15, 10), 'assigned': False}
]
warehouse_location = (0, 0)

sample_robots = [
    Robot('R1', warehouse_location),
    Robot('R2', warehouse_location),
    Robot('R3', warehouse_location)
]

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
