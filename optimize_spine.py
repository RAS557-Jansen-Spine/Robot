import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize


def objective_function(x):
    """
    Placeholder objective function.
    Minimizes distance to a 'target' size.
    """
    # Current values being tested
    d1, d2, d3 = x

    # Target size we want to achieve (Placeholder logic)
    target = np.array([0.002, 0.05, 0.03])

    # Simple squared error loss
    loss = np.sum((x - target) ** 2)
    return loss


def plot_results(history, x0, x_opt, bounds):
    """
    Plots the optimization convergence and parameter comparison.
    """
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    history = np.array(history)
    iterations = range(1, len(history) + 1)

    # Plot 1: Convergence (Loss vs Iteration)
    losses = [objective_function(x) for x in history]

    plt.figure(figsize=(10, 5))
    plt.plot(iterations, losses, "b-o", label="Objective Loss")
    plt.xlabel("Iteration")
    plt.ylabel("Loss (MSE)")
    plt.title("Optimization Convergence")
    plt.grid(True)
    plt.legend()
    plt.savefig("outputs/opt_convergence.png")
    print("Saved outputs/opt_convergence.png")
    plt.close()

    # Plot 2: Parameters Change (Initial vs Optimal)
    labels = ["Dim 1", "Dim 2", "Dim 3"]
    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(10, 5))
    plt.bar(x - width / 2, x0, width, label="Initial", color="gray")
    plt.bar(x + width / 2, x_opt, width, label="Optimal", color="green")

    # Add target markers for reference
    target = [0.002, 0.05, 0.03]
    plt.plot(x, target, "rx", markersize=10, markeredgewidth=2, label="Target (Hidden)")

    plt.ylabel("Size (meters)")
    plt.title("Parameter Optimization Results")
    plt.xticks(x, labels)
    plt.legend()
    plt.grid(True, axis="y")
    plt.savefig("outputs/opt_parameters.png")
    print("Saved outputs/opt_parameters.png")
    plt.close()


def optimize_spine():
    # Initial guess (Current INNER_SHAFT_SIZE)
    x0 = [0.001, 0.06, 0.028]

    # Bounds
    bounds = (
        (0.0001, 0.01),  # Dimension 1
        (0.01, 0.15),  # Dimension 2
        (0.01, 0.1),  # Dimension 3
    )

    print("Starting optimization...")
    print(f"Initial Guess: {x0}")

    # Callback to store history
    history = []

    def callback(xk):
        history.append(np.copy(xk))

    # Optimization
    result = minimize(
        objective_function,
        x0,
        method="L-BFGS-B",
        bounds=bounds,
        callback=callback,
        options={"disp": True},
    )

    # Add final point to history if not there
    if len(history) == 0 or not np.array_equal(history[-1], result.x):
        history.append(result.x)

    print("\nOptimization Result:")
    print(f"Success: {result.success}")
    print(f"Optimal INNER_SHAFT_SIZE: {tuple(result.x)}")
    print(f"Objective Value: {result.fun}")

    # Plotting
    plot_results(history, x0, result.x, bounds)


if __name__ == "__main__":
    optimize_spine()
