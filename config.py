"""
sample_orders = [
    {'order_id': 1, 'location': (5, 15), 'assigned': False},
    {'order_id': 2, 'location': (12, 7), 'assigned': False},
    {'order_id': 3, 'location': (15, 10), 'assigned': False}
] """

MAP_SIZE = 25 # The width and height of the square grid 
OBSTACLE_RATIO = 0.22 # The fraction of the grid to fill with obstacles
FW_LOCATION = (12, 12) # Warehouse Locations
#SP_LOCATION  = [order['location'] for order in sample_orders] # Order drop-off points
