# Bio-Inspired Foldable Robot (RAS 557 Final Project)

**Team 01**:
- Jeevan Hebbal Manjunath (jhebbalm@asu.edu)
- Varun Karthik (vnolas82@asu.edu)
- Yeshwanth Reddy Gurreddy (ygurreddy@asu.edu)

## Project Overview

This repository contains the complete source code, documentation, and design files for the Team 01 Final Project in RAS 557. The project focuses on the design, simulation, and fabrication of a **bio-inspired foldable robot** featuring **Jensen linkage legs** and a **compliant spine**.

The goal of the project is to explore the efficacy of laminate manufacturing for complex kinematic chains and to analyze the impact of spine flexibility on locomotion performance through both MuJoCo simulations and physical experimentation.

---

## Repository Structure & Branches

This repository is organized into specific branches for different implementation domains. Please switch to the relevant branch to access the specific source code:

| Branch Name | Description | Key Contents |
| :--- | :--- | :--- |
| **`website`** | **Documentation & Report** | Project Website (`index.html`), Final Report (LaTeX/PDF), Images, Videos. |
| **`mujoco-simulation`** | **Simulation** | MuJoCo environments, Spine optimization scripts, Reinforcement Learning models. |
| **`motor-control`** | **Firmware & Control** | ESP32 MicroPython code (`main.py`), BNO055 IMU drivers, Live Plotting scripts. |
| **`cut_file_generator`** | **Manufacturing** | Python scripts & Jupyter Notebooks to generate laser-cutting DXF files. |
| **`main`** | **Root / Legacy** | General project files and older prototypes. |

---

## Branch Details

### 1. Website & Documentation (`website`)
This branch hosts the project's public-facing materials.
- **Website**: `index.html`, `js/main.js`, `css/style.css` - A responsive dashboard presenting the team, project gallery, and videos.
- **Final Report**: Located in `Final-Report/`. Contains the `Team-01-Final-Report.pdf` and LaTeX source files.
- **Gallery**: `images/` contains high-res photos of the robot manufacturing, assembly, and experimental results.

### 2. MuJoCo Simulation (`mujoco-simulation`)
Detailed physics simulation environment to test spine designs and walking gaits.
- **`main.py`**: Entry point for running simulations.
- **`model_builder.py`**: Procedurally generates the MuJoCo XML model based on robot parameters.
- **`optimize_spine.py`**: Script for running optimization routines to find ideal spine stiffness and length.
- **`ppo_robot_walker.zip`**: Pre-trained Reinforcement Learning model weights.

### 3. Motor Control & Firmware (`motor-control`)
MicroPython code developed for the ESP32 microcontroller to drive the physical robot.
- **`main.py`**: The core control loop.
  - **`MotorDriver` class**: Controls two DC motors (Front/Back) via PWM.
  - **IMU Handling**: Reads orientation (Heading, Roll, Pitch) from the BNO055 sensor over I2C.
- **`live_plot.py`**: PC-side Python script to parse serial data from the ESP32 and visualize Robot orientation/trajectory in real-time.
- **`boot.py`**: ESP32 boot configuration.
- **`imu_logs/`**: CSV logs of experimental trials.

### 4. Manufacturing / Cut File Generator (`cut_file_generator`)
A toolchain for designing the laminate structure of the robot.
- **`cut_generator.ipynb`**: Jupyter Notebook that defines the laminate layers (body, adhesive, flexure) and generates fabrication files.
- **`dxfv2.py`**: Custom library for robust DXF read/write operations (supports `ezdxf` and `foldable-robotics`).
- **`dxf/input/`**: Base designs (e.g., `jensen-leg.dxf`).
- **`dxf/output/`**: Generated files for laser cutting (`final_cut.dxf`, `first_pass.dxf`).

**Installation (for Cut Generator):**
```bash
git checkout cut_file_generator
pip install .  # Installs dependencies like foldable-robotics, ezdxf, shapely
```

---

## References
This project builds upon research in:
- Myriapod-like ambulation and segmented microrobots.
- Compliant spine mechanics in quadrupedal locomotion.
- Foldable robotics manufacturing techniques (laminate processes).

*For detailed citations, please refer to the `website` branch or the Final Report.*
