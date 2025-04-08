## FOODIE (Food Intelligence Electrified)

1. The campus is a known bounded terrain. There may obstacles along pathways. The simulation uses a 20x20 grid with randomly placed obstacles.

2. Every 10 seconds, a random place will send a food order to the restaurant.
3. The restaurant owns 3 movable robots. Robot speed is controlled by the simulation frame rate.
4. Robots will depart from and return to a food warehouse (FW) in which they:
a. Receive new food items and load up the items into their compartment.
b. Since the restaurant may con6nuously receive new orders, the robots need
consider delivering more than 1 order to more than 1 location and then return.
5. The grid map has static obstacles. Pathfinding uses A* and assumes uniform speed.
Orders are always deliverable unless blocked.

6. Uses A* pathfinding to calculate the shortest route.
Orders are assigned to the closest available robot.

---

Run `main.py` to launch the simulation.
Install dependencies:
```bash
pip install pygame
```

---

For visualization, the color scheme is:
- 🔴 Red: New unassigned order
- 🟠 Orange: Order being delivered
- 🟢 Green: Delivered order
- 🟦 Blue: Warehouse
- 🟩 Orange Square: Robot