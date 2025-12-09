from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Data extracted from optimization logs
# Iterations (approx evaluation order)
iters = range(1, 19)
dists = [
    0.1242,
    0.1279,
    0.1080,
    0.1359,
    0.1261,
    0.1359,
    0.1173,
    0.1196,
    0.1382,
    0.1408,
    0.1305,
    0.1408,
    0.1318,
    0.1398,
    0.1408,
    0.1366,
    0.1331,
    0.1426,
]
# Best Parameters found
params_initial = [0.001, 0.06, 0.028]
params_opt = [0.001007, 0.05997, 0.02890]  # Approx best

OUTPUT_DIR = Path("output_opt")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Plot Convergence
plt.figure(figsize=(10, 5))
plt.plot(iters, dists, "b-o", label="Distance Traveled")
plt.xlabel("Evaluation #")
plt.ylabel("Distance (m)")
plt.title("Real Optimization Progress (Walking)")
plt.grid(True)
plt.legend()
plt.savefig(OUTPUT_DIR / "opt_walking_convergence.png")
print(f"Saved {OUTPUT_DIR / 'opt_walking_convergence.png'}")

# Plot Parameters
labels = ["Dim 1", "Dim 2", "Dim 3"]
x = np.arange(len(labels))
width = 0.35

plt.figure(figsize=(10, 5))
plt.bar(x - width / 2, params_initial, width, label="Initial", color="gray")
plt.bar(x + width / 2, params_opt, width, label="Optimal", color="green")
plt.ylabel("Size (m)")
plt.title("Parameter Optimization (Walking)")
plt.xticks(x, labels)
plt.legend()
plt.grid(True, axis="y")
plt.savefig(OUTPUT_DIR / "opt_walking_params.png")
print(f"Saved {OUTPUT_DIR / 'opt_walking_params.png'}")
