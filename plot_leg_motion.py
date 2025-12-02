import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

# --- Parameters and Helper Functions ---

# Standard Jansen's linkage link lengths (proportional)
a = 38  # Input crank
b = 41.5  # Rocker link connected to crank
c = 39.3  # Link connecting rocker to main triangle
d = 40.1  # Side of the main triangle
e = 55.8  # Link connecting crank to the 'knee'
f = 39.4  # Upper leg link
g = 36.7  # Lower leg link
h = 65.7  # Link connecting main triangle to 'ankle'
i = 49.0  # Link forming the foot triangle

# Fixed pivot points (ground)
p_crank = np.array([0, 0])
p_fixed = np.array([-38, -7.8])


def intersect_circles(p1, r1, p2, r2):
    """
    Finds the intersection points of two circles.
    Returns one of the two intersection points based on a heuristic
    to avoid linkage 'flipping'.
    """
    d = np.linalg.norm(p2 - p1)
    if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
        return p1 + np.array([r1, 0])  # Return default on failure

    a_calc = (r1**2 - r2**2 + d**2) / (2 * d)
    h_calc = np.sqrt(max(0, r1**2 - a_calc**2))

    p_mid = p1 + a_calc * (p2 - p1) / d

    intersection1 = np.array(
        [
            p_mid[0] + h_calc * (p2[1] - p1[1]) / d,
            p_mid[1] - h_calc * (p2[0] - p1[0]) / d,
        ]
    )
    intersection2 = np.array(
        [
            p_mid[0] - h_calc * (p2[1] - p1[1]) / d,
            p_mid[1] + h_calc * (p2[0] - p1[0]) / d,
        ]
    )

    # Heuristic to choose the correct intersection for this linkage
    if intersection1[1] > intersection2[1]:
        return intersection1
    return intersection2


def update_positions(phi):
    """
    Calculates the positions of all joints for a given crank angle `phi`.
    """
    # Point A (end of crank)
    A = np.array([a * np.cos(phi), a * np.sin(phi)])
    # Point C (intersection from A and the fixed pivot)
    C = intersect_circles(A, c, p_fixed, b)
    # Point D is on the same rigid body as C, relative to the fixed pivot B
    angle_BC = np.arctan2(C[1] - p_fixed[1], C[0] - p_fixed[0])
    D = p_fixed + d * np.array(
        [np.cos(angle_BC + np.radians(28)), np.sin(angle_BC + np.radians(28))]
    )
    # Point E (intersection from A and D)
    E = intersect_circles(A, e, D, f)
    # Point F (intersection from C and E)
    F = intersect_circles(C, h, E, g)
    # Point G (the foot, intersection from D and F)
    G = intersect_circles(D, i, F, g)

    return A, C, D, E, F, G


# --- Plotting and Animation Setup ---

fig, ax = plt.subplots()
ax.set_aspect("equal")
foot_path_x, foot_path_y = [], []

# Create a plot object for each individual link for smooth drawing
(link_AC,) = ax.plot([], [], "o-", lw=2, color="royalblue", markersize=6)
(link_CD,) = ax.plot([], [], "o-", lw=2, color="royalblue", markersize=6)
(link_AE,) = ax.plot([], [], "o-", lw=2, color="royalblue", markersize=6)
(link_DF,) = ax.plot([], [], "o-", lw=2, color="royalblue", markersize=6)
(link_EF,) = ax.plot([], [], "o-", lw=2, color="royalblue", markersize=6)
(link_FG,) = ax.plot([], [], "o-", lw=2, color="royalblue", markersize=6)
(link_DG,) = ax.plot([], [], "o-", lw=2, color="royalblue", markersize=6)
(link_BC,) = ax.plot([], [], "o-", lw=2, color="royalblue", markersize=6)
(link_BD,) = ax.plot([], [], "o-", lw=2, color="royalblue", markersize=6)

# Store all link objects in a list to manage them easily
all_links = [
    link_AC,
    link_CD,
    link_AE,
    link_DF,
    link_EF,
    link_FG,
    link_DG,
    link_BC,
    link_BD,
]

# Plot objects for other components
(fixed_points,) = ax.plot(
    [p_crank[0], p_fixed[0]],
    [p_crank[1], p_fixed[1]],
    "s",
    color="black",
    markersize=8,
    label="Fixed Pivots",
)
(input_crank,) = ax.plot([], [], "o-", color="red", lw=3, label="Input Crank")
(foot_point,) = ax.plot([], [], "o", color="green", markersize=8, label="Foot")
(path_line,) = ax.plot([], [], ":", color="green", lw=1.5, alpha=0.7, label="Foot Path")
ax.legend()


def init():
    """Set up the plot limits and initialize elements."""
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)  # Corrected y-limit

    # Initialize all individual links
    for link in all_links:
        link.set_data([], [])

    input_crank.set_data([], [])
    foot_point.set_data([], [])
    path_line.set_data([], [])

    # The return must include all animated objects
    return all_links + [input_crank, foot_point, path_line]


def animate(frame):
    """Update the plot for each frame of the animation."""
    phi = frame * (2 * np.pi / 200)  # Increased frames for smoother animation
    A, C, D, E, F, G = update_positions(phi)
    B = p_fixed  # B is the alias for the fixed pivot

    # Update foot path
    foot_path_x.append(G[0])
    foot_path_y.append(G[1])
    if len(foot_path_x) > 200:
        foot_path_x.pop(0)
        foot_path_y.pop(0)
    path_line.set_data(foot_path_x, foot_path_y)

    # Update input crank
    input_crank.set_data([p_crank[0], A[0]], [p_crank[1], A[1]])

    # Update foot position
    foot_point.set_data([G[0]], [G[1]])

    # Update data for each physical link individually for smooth plotting
    link_AC.set_data([A[0], C[0]], [A[1], C[1]])
    link_CD.set_data([C[0], D[0]], [C[1], D[1]])
    link_AE.set_data([A[0], E[0]], [A[1], E[1]])
    link_DF.set_data([D[0], F[0]], [D[1], F[1]])
    link_EF.set_data([E[0], F[0]], [E[1], F[1]])
    link_FG.set_data([F[0], G[0]], [F[1], G[1]])
    link_DG.set_data([D[0], G[0]], [D[1], G[1]])
    link_BC.set_data([B[0], C[0]], [B[1], C[1]])
    link_BD.set_data([B[0], D[0]], [B[1], D[1]])

    return all_links + [input_crank, foot_point, path_line]


# --- Run the Animation ---

ani = FuncAnimation(
    fig,
    animate,
    frames=200,  # Increased frames for smoother rotation
    init_func=init,
    blit=True,
    interval=30,  # Interval in ms, smaller is faster
)

plt.grid(True)
plt.show()
