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

## RL Training and Integration

### How the Model is Trained

The Reinforcement Learning (RL) model is trained using **Stable Baselines 3**, a popular RL library for Python. Specifically, we use the **Proximal Policy Optimization (PPO)** algorithm, which is known for its balance of ease of implementation, sample complexity, and ease of tuning.

1.  **Environment Setup**: The `RobotEnv` class (in `robot_env.py`) wraps the MuJoCo simulation into a standard Gymnasium environment. It defines:
    -   **Action Space**: Continuous control signals for the robot's motors.
    -   **Observation Space**: A vector containing sensor data such as joint positions, velocities, and the robot's base position/orientation.
    -   **Reward Function**: A custom reward function defined in `RobotConfig` that encourages forward motion while penalizing control effort and falling.

2.  **Training Loop**: When you run `python main.py train`, the script:
    -   Initializes the `RobotEnv`.
    -   Instantiates a PPO agent with an MLP (Multi-Layer Perceptron) policy.
    -   Runs the training loop for a specified number of timesteps (default: 100,000).
    -   During training, the agent interacts with the environment, collecting experience (observations, actions, rewards) and updating its policy to maximize cumulative reward.

3.  **Saving**: The trained model is saved as a `.zip` file (e.g., `ppo_robot_walker.zip`).

### How the Model is Inserted into MuJoCo

The integration of the trained RL model back into the MuJoCo simulation for inference (running the agent) works as follows:

1.  **Loading the Model**: When you run `python main.py run --load-path ...`, the script loads the saved PPO model using `PPO.load()`.

2.  **Simulation Loop**:
    -   The script resets the `RobotEnv` to get the initial observation.
    -   It enters a loop where it continuously:
        1.  Passes the current observation to the trained model (`model.predict(obs)`).
        2.  Receives the optimal action (motor control signals) from the model.
        3.  Steps the MuJoCo environment with this action (`env.step(action)`).
        4.  Renders the simulation to visualize the robot's behavior.

This process allows the trained neural network to control the MuJoCo robot in real-time based on the policy it learned during training.
