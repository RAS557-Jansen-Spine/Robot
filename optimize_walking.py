import os
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

from bodies.spine import SpineBuilder

# Project Imports
from model_builder import build_model, prettify
from robot_env import RobotEnv

# Directory for temp files
OUTPUT_DIR = Path("output_opt")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_simulation(xml_path, duration=2.0):
    """
    Runs the simulation for a fixed duration using a simple open-loop gait.
    Returns the final X position (distance traveled).
    """
    try:
        env = RobotEnv(model_path=str(xml_path))
    except Exception as e:
        print(f"Failed to load model: {e}")
        return -100.0  # Penalty for invalid model

    env.reset()

    # Simulation Loop
    # We use a fixed gait (Sine waves) to test mechanical capability
    dt = env.model.opt.timestep
    steps = int(duration / dt)

    total_reward = 0

    for i in range(steps):
        t = i * dt

        # Simple Crawl Gait (Sine waves with phase offsets)
        # Assuming 4 motors: FL, FR, BL, BR
        freq = 2.0  # Hz
        amp = 1.0

        # Actions in [-1, 1] range
        action = np.zeros(4)
        action[0] = amp * np.sin(2 * np.pi * freq * t)  # FL
        action[1] = amp * np.sin(2 * np.pi * freq * t + np.pi)  # FR (Anti-phase)
        action[2] = amp * np.sin(2 * np.pi * freq * t + np.pi)  # BL (Anti-phase to FL)
        action[3] = amp * np.sin(2 * np.pi * freq * t)  # BR (Same as FL)

        obs, reward, terminated, truncated, info = env.step(action)

        if terminated or truncated:
            break

    # Success Metric: Final X Position
    final_x = env.data.qpos[0]

    env.close()
    return final_x


def objective_function(x):
    """
    Objective: Minimize Negative Distance (Maximize Distance).
    """
    # 1. Update Parameters (Monkeypatching)
    # Ensure values are positive to avoid MuJoCo errors
    if np.any(x <= 0):
        return 100.0  # Penalty

    SpineBuilder.INNER_SHAFT_SIZE = tuple(x)

    # 2. Build Model
    model_name = "OptBot"
    try:
        mujoco_elem = build_model(model_name)
        xml_str = prettify(mujoco_elem)
        xml_path = OUTPUT_DIR / "temp_model.xml"
        xml_path.write_text(xml_str)
    except Exception as e:
        print(f"Build failed: {e}")
        return 100.0

    # 3. Reimulate - Simulate
    distance = run_simulation(xml_path)

    print(f"Eval: {x} -> Dist: {distance:.4f}m")

    return -distance  # Minimize negative distance


def plot_results(history, scores, x0, x_opt):
    """
    Plots optimization progress.
    """
    iterations = range(1, len(history) + 1)

    plt.figure(figsize=(10, 5))
    plt.plot(iterations, scores, "b-o")
    plt.xlabel("Iteration")
    plt.ylabel("Distance Traveled (m)")
    plt.title("Optimization Progress: Walking Distance")
    plt.grid(True)
    plt.savefig(OUTPUT_DIR / "opt_walking_convergence.png")
    print(f"Saved {OUTPUT_DIR / 'opt_walking_convergence.png'}")
    plt.close()


def optimize_walking():
    # Initial Guess (Current Values)
    x0 = [0.001, 0.06, 0.028]

    bounds = (
        (0.001, 0.02),  # Thickness
        (0.03, 0.15),  # Length
        (0.015, 0.05),  # Width
    )

    print("Starting REAL Optimization (Simulation-Based)...")
    print("This may take a while.")

    history = []
    scores = []

    def callback(xk):
        # Evaluate current best to log score
        score = -objective_function(xk)  # Re-evaluate or cache?
        # Note: Calling obj_func inside callback doubles comp time technically,
        # but capturing 'distance' from the main loop is harder in scipy without global/class.
        # For visualization, we'll just append xk.
        history.append(np.copy(xk))
        # We will assume the last printed Eval was this score for simplicity in this script,
        # or we can re-run. Let's just store xk.

    # We'll use Nelder-Mead as it's robust for noisy/non-smooth functions (simulation)
    # L-BFGS-B needs gradients, which we don't have analytically.
    result = minimize(
        objective_function,
        x0,
        method="Nelder-Mead",
        bounds=bounds,
        callback=callback,
        options={"maxiter": 20, "disp": True},  # Limit iters for speed
    )

    print("\nOptimization Result:")
    print(f"Optimal INNER_SHAFT_SIZE: {tuple(result.x)}")
    print(f"Max Distance: {-result.fun:.4f} m")

    # Generate scores for plot (Re-evaluating history for clean plot)
    print("Generating plot...")
    for x in history:
        # We temporarily set the spine builder again just in case
        SpineBuilder.INNER_SHAFT_SIZE = tuple(x)
        # Reuse existing xml if possible but parameter changed, so rebuild
        # Recalling objective_function does the build + sim
        scores.append(-objective_function(x))

    plot_results(history, scores, x0, result.x)


if __name__ == "__main__":
    optimize_walking()
