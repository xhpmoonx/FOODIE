# 🍽️ FOODIE — Food Intelligence Electrified

Autonomous campus food delivery simulation with real-time visual feedback, robot batching, and performance stats.

## 📦 Features
- Simulates delivery across a 25x25 grid
- Intelligent A* pathfinding with diagonal movement
- Dynamic obstacle-aware navigation
- 3 Robots pick up and deliver multiple orders in batches
- Prioritized order assignment using age and proximity scoring
- Live dashboard with delivery stats (total orders, robot efficiency)
- Wait-based visual fading of unassigned orders

## 🕹️ How to Run

```bash
pip install pygame
python main.py

## 🎨 Visual Key

For visualization, the color scheme is:
- 🌑 Gray: New unassigned order
- 🔴 Red: Order being delivered
- 🟢 Green: Delivered order
- 🟦 Blue: Warehouse
- 🟧 Orange: Robot