# Robot Walker Project

This project implements a MuJoCo-based robot walker with reinforcement learning capabilities.

## Prerequisites

- Python 3.8+
- MuJoCo
- `mujoco-python`
- `stable-baselines3`
- `gymnasium`
- `PyYAML`

Install dependencies:
```bash
pip install mujoco stable-baselines3 gymnasium pyyaml
```

## Usage

The project uses a unified entry point `main.py`.

### Global Arguments
These arguments apply to all subcommands (except where noted):
- `--output <path>`: Path to the model XML file (default: `output/model.xml`).
- `--model-name <name>`: Name of the model in the XML (default: `Model`).

### Subcommands

#### 1. Generate Model
Generate the MuJoCo XML model file.
```bash
python main.py generate [--output output/model.xml] [--model-name MyRobot]
```

#### 2. View Model
Visualize the generated model.
**Note for macOS users:** You may need to use `mjpython` to launch the passive viewer.
```bash
# Standard
python main.py view [--config config/init_qpos.yaml] [--demo-spin]

# macOS
mjpython main.py view
```
- `--config <path>`: Path to the initial joint positions YAML file (default: `config/init_qpos.yaml`).
- `--demo-spin`: Apply a simple spin control to motors for demonstration.

#### 3. Check Model
Verify model properties (e.g., geometric alignment).
```bash
python main.py check [--output output/model.xml]
```

#### 4. Train Agent
Train a PPO agent to control the robot.
```bash
python main.py train --timesteps 100000 --save-path ppo_robot_walker
```
- `--timesteps <n>`: Total training timesteps (default: 100000).
- `--save-path <path>`: Path to save the trained model (default: `ppo_robot_walker`).

#### 5. Run Agent
Run a trained agent in the environment.
```bash
# Standard
python main.py run --load-path ppo_robot_walker

# macOS
mjpython main.py run --load-path ppo_robot_walker
```
- `--load-path <path>`: Path to load the trained model from (default: `ppo_robot_walker`).

## Project Structure

- `main.py`: Unified entry point for all commands.
- `model_builder.py`: Centralized logic for generating MuJoCo XML.
- `robot_env.py`: Gymnasium environment and robot configuration.
- `bodies/`: Component builders for the robot (chassis, legs, motor, etc.).
- `config/`: Configuration files (e.g., initial joint positions).
