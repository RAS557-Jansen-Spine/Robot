# Analysis of a Bio-Inspired Myriapod Robot
## With a Modified Hybrid Spine and Jansen Linkage Legs

This project presents the design, kinematic modeling, and dynamic analysis of a centipede-inspired terrestrial locomotion mechanism. It investigates the coupled dynamics of an asymmetrically compliant spine and biologically realistic leg kinematics, aiming to bridge the gap between stability and maneuverability in foldable robotic systems.

## Project Overview

The robot mimics the morphology of *Lithobius forficatus* (stone centipede) and introduces a dual-modification to standard myriapod templates:

1.  **Hybrid Spine Architecture**: Integrates a rigid anterior spinal connection with a compliant posterior Sarrus linkage. This design is intended to enhance anterior stability while retaining posterior compliance for turning maneuverability.
2.  **Jansen Linkage Locomotion**: Implements planar, 1-DOF Jansen linkages to generate biologically relevant ovoid foot loci, improving ground clearance and step repeatability compared to simple rotary legs.

## Repository Structure

- **`centipede.xml`**: The MuJoCo model file defining the robot's physical structure, joints, actuators, and simulation parameters.
- **`crawller.ipynb`**: A Jupyter Notebook for running physics-based simulations using MuJoCo. It handles model loading, simulation stepping, and rendering.
- **`plot_leg_motion.py`**: A Python script that calculates and animates the kinematic trajectory of the Jansen linkage leg mechanism.
- **`report/`**: Contains the LaTeX source code and assets for the detailed project report ("Team-01-Project-01.tex").
- **`output/`**: Directory for storing simulation artifacts and generated media.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- [MuJoCo](https://mujoco.org/) physics engine

### Installation

Install the required packages using `pip`:

```bash
pip install matplotlib mediapy mujoco numpy
```

### Usage

#### 1. Kinematic Visualization
To visualize the motion of the Jansen linkage leg and the foot path:
```bash
python plot_leg_motion.py
```
This will generate an animation showing the linkage movement and the resulting foot trajectory.

#### 2. Physics Simulation
Open `crawller.ipynb` in Visual Studio Code or Jupyter Lab. This notebook allows you to:
- Load the `centipede.xml` model.
- Run the simulation step-by-step.
- Visualize the robot's behavior in the MuJoCo environment.
- Render and save simulation videos.

## Authors

- **Jeevan Hebbal Manjunath
- **Varun Karthik
- **Yeshwanth Reddy Gurreddy

## Course Information

**RAS 557: Foldable Robotics**
*Arizona State University*
*Fall 2025*

