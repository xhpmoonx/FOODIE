from map import generate_map
from simulation import Simulation
from data import sample_robots

if __name__ == '__main__':
    campus_map, _ = generate_map() # Returns a representation of the environment

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
