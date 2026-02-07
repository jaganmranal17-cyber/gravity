# Gravity - High-Accuracy Orbital Simulator 🌌🚀

A sophisticated 3D solar system simulator built with Python and Pygame-CE, featuring a 4th-order Runge-Kutta (RK4) physics engine for extreme numerical stability and precision.

## ✨ Features
- **RK4 Physics Engine**: High-accuracy integration that keeps Mercury and Moon orbits stable over long periods.
- **10 Selectable Systems**:
    - Complete Solar System + Extended Solar (Dwarf Planets & Asteroids).
    - Detailed Jovian, Saturnian, Uranian, and Neptunian systems.
    - Dedicated Mars and Pluto systems.
    - **TRAPPIST-1**: An exoplanetary system with 7 Earth-sized planets.
- **Dynamic Data**: Real-time orbital vectors fetched from the **JPL Horizons API**.
- **Interactive UI**:
    - System selection menu.
    - Linear time-warp slider (1x to 200x).
    - 3D labels for all celestial bodies.
- **3D Visualization**: Adjustable camera with zoom and rotate, depth-sorted rendering, and alpha-faded motion trails.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- [Pygame-CE](https://pyg-ce.org/)
- NumPy
- Requests

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/jaganmranal/gravity.git
   cd gravity
   ```
2. Install dependencies:
   ```bash
   pip install pygame-ce numpy requests
   ```
3. Run the simulator:
   ```bash
   python main.py
   ```

## 🎮 Controls
- **Left Mouse Click + Drag**: Rotate Camera.
- **Mouse Wheel**: Zoom In/Out.
- **UI Menu**: Select systems and adjust simulation speed.

## 📂 Project Structure
- `main.py`: Entry point and rendering loop.
- `physics.py`: RK4 integrator and vector math.
- `data.py`: JPL API interface and system configurations.
- `ui.py`: Custom UI components (Buttons, Sliders).
- `visualization.py`: 3D projection and camera logic.

---
Created by jaganmranal
