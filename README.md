# Space Satellite (idk what to call this yet)

A 3D satellite orbital simulation and visualization tool built with Python and PyQt5


## Requirements

- Python 3.6+
- PyQt5
- PyOpenGL
- NumPy (optional for additional calculations)
- matplotlib (for satellite model visualization)
- skyfield (for satellite position calculations)
- requests (for API communication)

## Installation

1. Clone the repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```
3. Run the simulator:
```bash
python main.py
```

## Update 0.3, Satellites:
- Added option for custom textures for satellites
- Added option for rotations around x,y or z axis of satellites
- Adjustable sizes for satellites
- BUGS: there may be bugs involving rotating, custom textured satellites and other satellites which causes really wonky orbits. I believe the issue has been resolved during development, however there may be ways to re-replicate this issue.

### Basic Controls

- **Left-click and drag**: Rotate the view
- **Mouse wheel**: Zoom in/out
- **Space**: Play/pause simulation
- **F**: Increase simulation speed
- **S**: Decrease simulation speed

### Creating a New Simulation

1. Click on **File → New simulation**
2. Configure the planet parameters
3. Click "Start simulation"
From there just figure it out yourself lmao have fun!!

