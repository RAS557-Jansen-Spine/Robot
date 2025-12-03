import multiprocessing as mp
import time
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


class LivePlotter:
    def __init__(self, num_motors: int = 4, max_points: int = 100):
        self.num_motors = num_motors
        self.max_points = max_points
        self.queue = mp.Queue()
        self.process: Optional[mp.Process] = None

    def start(self):
        """Starts the plotting process."""
        self.process = mp.Process(
            target=self._run_process,
            args=(self.queue, self.num_motors, self.max_points),
            daemon=True,
        )
        self.process.start()

    def stop(self):
        """Stops the plotting process."""
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join()

    def put_data(
        self,
        timestamp: float,
        qpos: np.ndarray,
        qvel: np.ndarray,
        ctrl: np.ndarray,
        qfrc: np.ndarray,
        base_pos: np.ndarray,
        base_quat: np.ndarray,
    ):
        """Pushes data to the plotting queue.

        Args:
            timestamp: Current simulation time.
            qpos: Array of joint positions (length num_motors).
            qvel: Array of joint velocities (length num_motors).
            ctrl: Array of motor control signals (length num_motors).
            qfrc: Array of motor forces (length num_motors).
            base_pos: Array of base position (x, y, z).
            base_quat: Array of base orientation quaternion (w, x, y, z).
        """
        if not self.queue.full():
            self.queue.put((timestamp, qpos, qvel, ctrl, qfrc, base_pos, base_quat))

    @staticmethod
    def _quat_to_euler(quat):
        """Converts quaternion (w, x, y, z) to euler roll, pitch, yaw."""
        w, x, y, z = quat

        # Roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        # Pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        if np.abs(sinp) >= 1:
            pitch = np.copysign(np.pi / 2, sinp)
        else:
            pitch = np.arcsin(sinp)

        # Yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw

    @staticmethod
    def _run_process(queue: mp.Queue, num_motors: int, max_points: int):
        """The main loop running in a separate process."""

        # Data storage
        times = []
        qpos_data = [[] for _ in range(num_motors)]
        qvel_data = [[] for _ in range(num_motors)]
        ctrl_data = [[] for _ in range(num_motors)]
        qfrc_data = [[] for _ in range(num_motors)]
        base_pos_data = [[] for _ in range(3)]  # x, y, z
        base_rpy_data = [[] for _ in range(3)]  # r, p, y

        # Setup plot
        fig, axes = plt.subplots(3, 2, figsize=(12, 10), sharex=True)
        ax_qpos, ax_qvel = axes[0]
        ax_ctrl, ax_qfrc = axes[1]
        ax_pos, ax_rpy = axes[2]

        # Lines
        lines = {"qpos": [], "qvel": [], "ctrl": [], "qfrc": [], "pos": [], "rpy": []}
        colors = ["r", "g", "b", "c", "m", "y", "k"]

        # Motors
        for i in range(num_motors):
            c = colors[i % len(colors)]
            (l,) = ax_qpos.plot([], [], label=f"M{i + 1}", color=c)
            lines["qpos"].append(l)
            (l,) = ax_qvel.plot([], [], label=f"M{i + 1}", color=c)
            lines["qvel"].append(l)
            (l,) = ax_ctrl.plot([], [], label=f"M{i + 1}", color=c)
            lines["ctrl"].append(l)
            (l,) = ax_qfrc.plot([], [], label=f"M{i + 1}", color=c)
            lines["qfrc"].append(l)

        # Base Pos
        for i, label in enumerate(["X", "Y", "Z"]):
            (l,) = ax_pos.plot([], [], label=label, color=colors[i])
            lines["pos"].append(l)

        # Base RPY
        for i, label in enumerate(["Roll", "Pitch", "Yaw"]):
            (l,) = ax_rpy.plot([], [], label=label, color=colors[i])
            lines["rpy"].append(l)

        # Titles and Labels
        ax_qpos.set_title("Joint Positions")
        ax_qpos.set_ylabel("Rad")
        ax_qpos.legend(loc="upper right", fontsize="x-small")
        ax_qpos.grid(True)

        ax_qvel.set_title("Joint Velocities")
        ax_qvel.set_ylabel("Rad/s")
        ax_qvel.grid(True)

        ax_ctrl.set_title("Motor Control")
        ax_ctrl.set_ylabel("Signal")
        ax_ctrl.grid(True)

        ax_qfrc.set_title("Motor Forces")
        ax_qfrc.set_ylabel("Force (N)")
        ax_qfrc.grid(True)

        ax_pos.set_title("Base Position")
        ax_pos.set_ylabel("Meters")
        ax_pos.legend(loc="upper right", fontsize="x-small")
        ax_pos.grid(True)

        ax_rpy.set_title("Base Orientation")
        ax_rpy.set_ylabel("Rad")
        ax_rpy.set_xlabel("Time (s)")
        ax_rpy.legend(loc="upper right", fontsize="x-small")
        ax_rpy.grid(True)

        def update(frame):
            # Consume all available data
            while not queue.empty():
                try:
                    data = queue.get_nowait()
                    t, qp, qv, ctrl, qfrc, bpos, bquat = data

                    times.append(t)

                    # Motors
                    for i in range(num_motors):
                        qpos_data[i].append(qp[i])
                        qvel_data[i].append(qv[i])
                        ctrl_data[i].append(ctrl[i])
                        qfrc_data[i].append(qfrc[i])

                    # Base Pos
                    for i in range(3):
                        base_pos_data[i].append(bpos[i])

                    # Base RPY
                    r, p, y = LivePlotter._quat_to_euler(bquat)
                    base_rpy_data[0].append(r)
                    base_rpy_data[1].append(p)
                    base_rpy_data[2].append(y)

                except Exception:
                    break

            # Trim
            if len(times) > max_points:
                trim = len(times) - max_points
                del times[:trim]
                for d in [qpos_data, qvel_data, ctrl_data, qfrc_data]:
                    for i in range(num_motors):
                        del d[i][:trim]
                for d in [base_pos_data, base_rpy_data]:
                    for i in range(3):
                        del d[i][:trim]

            if not times:
                return []

            # Update lines
            all_lines = []
            for i in range(num_motors):
                lines["qpos"][i].set_data(times, qpos_data[i])
                lines["qvel"][i].set_data(times, qvel_data[i])
                lines["ctrl"][i].set_data(times, ctrl_data[i])
                lines["qfrc"][i].set_data(times, qfrc_data[i])
                all_lines.extend(
                    [
                        lines["qpos"][i],
                        lines["qvel"][i],
                        lines["ctrl"][i],
                        lines["qfrc"][i],
                    ]
                )

            for i in range(3):
                lines["pos"][i].set_data(times, base_pos_data[i])
                lines["rpy"][i].set_data(times, base_rpy_data[i])
                all_lines.extend([lines["pos"][i], lines["rpy"][i]])

            # Rescale
            for ax in axes.flatten():
                ax.relim()
                ax.autoscale_view()

            return all_lines

        ani = FuncAnimation(
            fig, update, interval=50, blit=False, cache_frame_data=False
        )
        plt.tight_layout()
        plt.show()
