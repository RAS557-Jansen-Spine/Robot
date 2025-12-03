from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import gymnasium as gym
import mujoco
import numpy as np
from gymnasium import spaces

# ==========================================
# Robot Config
# ==========================================


@dataclass
class MotorConfig:
    name: str
    joint_name: str
    ctrl_range: List[float] = field(default_factory=lambda: [-1.0, 1.0])
    gear: float = 1.0


@dataclass
class SensorConfig:
    name: str
    # Function to extract sensor data from (model, data)
    # Returns a numpy array or float
    extract_fn: Callable[[Any, Any], np.ndarray]
    dim: int


@dataclass
class RewardConfig:
    name: str
    weight: float
    # Function to compute reward from (model, data, action, info)
    compute_fn: Callable[[Any, Any, np.ndarray, Dict], float]


class RobotConfig:
    def __init__(self):
        # 1. Inputs (Motors)
        # Based on model.xml: motor_joint_1, motor_joint_2, motor_joint_3, motor_joint_4
        self.motors: List[MotorConfig] = [
            MotorConfig(name="motor_1", joint_name="motor_joint_1", ctrl_range=[0, 20]),
            MotorConfig(
                name="motor_2", joint_name="motor_joint_2", ctrl_range=[-20, 0]
            ),
            MotorConfig(name="motor_3", joint_name="motor_joint_3", ctrl_range=[0, 20]),
            MotorConfig(
                name="motor_4", joint_name="motor_joint_4", ctrl_range=[-20, 0]
            ),
        ]

        # 2. Sensors (Observations)
        self.sensors: List[SensorConfig] = [
            # Base Position (z-height is important for falling)
            SensorConfig(
                name="base_pos", extract_fn=lambda m, d: d.qpos[:3].copy(), dim=3
            ),
            # Base Orientation (Quaternion)
            SensorConfig(
                name="base_quat", extract_fn=lambda m, d: d.qpos[3:7].copy(), dim=4
            ),
            # Joint Positions (for the 4 motors)
            SensorConfig(
                name="motor_qpos",
                extract_fn=lambda m, d: np.array(
                    [
                        d.qpos[
                            m.jnt_qposadr[
                                mujoco.mj_name2id(
                                    m, mujoco.mjtObj.mjOBJ_JOINT, mc.joint_name
                                )
                            ]
                        ]
                        for mc in self.motors
                    ]
                ),
                dim=4,
            ),
            # Joint Velocities (for the 4 motors)
            SensorConfig(
                name="motor_qvel",
                extract_fn=lambda m, d: np.array(
                    [
                        d.qvel[
                            m.jnt_dofadr[
                                mujoco.mj_name2id(
                                    m, mujoco.mjtObj.mjOBJ_JOINT, mc.joint_name
                                )
                            ]
                        ]
                        for mc in self.motors
                    ]
                ),
                dim=4,
            ),
        ]

        # 3. Rewards
        self.rewards: List[RewardConfig] = [
            # Reward for moving forward (in x direction)
            RewardConfig(
                name="forward_velocity",
                weight=1.0,
                compute_fn=lambda m, d, a, i: d.qvel[
                    0
                ],  # Assuming qvel[0] is global x velocity
            ),
            # Penalty for control effort
            RewardConfig(
                name="ctrl_cost",
                weight=-0.01,
                compute_fn=lambda m, d, a, i: np.sum(np.square(a)),
            ),
            # Penalty for falling (z-height too low)
            # This might be better handled as a termination condition, but can be a penalty too
            RewardConfig(
                name="alive_bonus", weight=0.1, compute_fn=lambda m, d, a, i: 1.0
            ),
        ]

    def get_observation_dim(self):
        return sum(s.dim for s in self.sensors)

    def get_action_dim(self):
        return len(self.motors)


# ==========================================
# Robot Env
# ==========================================


class RobotEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(
        self,
        model_path: str = "output/model.xml",
        config_path: str = "config/init_qpos.yaml",
        render_mode: Optional[str] = None,
    ):
        self.model_path = model_path
        self.config_path = Path(config_path)
        self.render_mode = render_mode

        # Load Model
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        self.model = mujoco.MjModel.from_xml_path(model_path)
        self.data = mujoco.MjData(self.model)

        self.config = RobotConfig()

        # Load initial positions
        self.init_qpos_config = self._load_init_qpos_from_yaml(self.config_path)

        # Action Space
        # We have N motors, each with a control range
        # We normalize action space to [-1, 1] and scale it in step()
        n_actions = self.config.get_action_dim()
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(n_actions,), dtype=np.float32
        )

        # Observation Space
        obs_dim = self.config.get_observation_dim()
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32
        )

        # Rendering
        self.viewer = None

        # Simulation params
        self.frame_skip = 5  # Number of simulation steps per env step

    def _load_init_qpos_from_yaml(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            print(
                f"Warning: Config file {path} not found. Using default initial positions."
            )
            return {}
        try:
            import yaml

            raw = yaml.safe_load(path.read_text()) or {}
            return raw.get("initial_qpos", raw)
        except ImportError:
            print("Warning: PyYAML not installed. Skipping init qpos load.")
            return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def _apply_initial_positions(self):
        if not self.init_qpos_config:
            return

        for joint_name, values in self.init_qpos_config.items():
            try:
                jnt_id = mujoco.mj_name2id(
                    self.model, mujoco.mjtObj.mjOBJ_JOINT, joint_name
                )
                if jnt_id == -1:
                    continue

                adr = self.model.jnt_qposadr[jnt_id]
                jnt_type = self.model.jnt_type[jnt_id]

                if (
                    jnt_type == mujoco.mjtJoint.mjJNT_HINGE
                    or jnt_type == mujoco.mjtJoint.mjJNT_SLIDE
                ):
                    expected = 1
                    vals = (
                        [float(values)]
                        if isinstance(values, (int, float))
                        else [float(v) for v in values]
                    )
                elif jnt_type == mujoco.mjtJoint.mjJNT_BALL:
                    expected = 4
                    vals = [float(v) for v in values]
                elif jnt_type == mujoco.mjtJoint.mjJNT_FREE:
                    expected = 7
                    vals = [float(v) for v in values]
                else:
                    continue

                if len(vals) == expected:
                    self.data.qpos[adr : adr + expected] = vals
            except Exception as e:
                print(f"Error setting joint {joint_name}: {e}")

    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ):
        super().reset(seed=seed)

        # Reset simulation
        mujoco.mj_resetData(self.model, self.data)

        # Apply initial positions from YAML
        self._apply_initial_positions()

        # Randomize initial state slightly (optional, good for RL)
        # qpos = self.data.qpos + self.np_random.uniform(low=-0.01, high=0.01, size=self.model.nq)
        # qvel = self.data.qvel + self.np_random.uniform(low=-0.01, high=0.01, size=self.model.nv)
        # self.data.qpos[:] = qpos
        # self.data.qvel[:] = qvel

        mujoco.mj_forward(self.model, self.data)

        return self._get_obs(), {}

    def step(self, action):
        # Scale action to control range
        scaled_action = np.zeros_like(action)
        for i, motor in enumerate(self.config.motors):
            low, high = motor.ctrl_range
            # Map [-1, 1] to [low, high]
            scaled_action[i] = low + (action[i] + 1.0) * 0.5 * (high - low)

            # Apply to control
            # We need to find the actuator index.
            # Assuming the order in config matches the order in XML or we find by name.
            # For simplicity/robustness, let's find by joint name if actuator name is not standard
            # But model.xml has actuators named "motor_joint_X_vel" or similar.
            # Let's assume the user wants to control the actuators defined in XML.
            # The config says "motor_joint_1", etc.
            # Let's try to map config motors to actuators.

            # In this specific model.xml, actuators are:
            # <velocity name="motor_joint_1_vel" joint="motor_joint_1" ... />
            # So we can just set data.ctrl directly if we know the index.
            # Let's assume the order in config.motors matches data.ctrl indices 0, 1, 2, 3
            pass

        self.data.ctrl[:] = scaled_action

        # Step simulation
        for _ in range(self.frame_skip):
            mujoco.mj_step(self.model, self.data)

        # Observation
        obs = self._get_obs()

        # Reward
        reward = 0.0
        info = {}
        for reward_cfg in self.config.rewards:
            r = reward_cfg.compute_fn(self.model, self.data, action, info)
            reward += reward_cfg.weight * r

        # Termination
        terminated = False
        truncated = False

        # Example termination: falling over (z-height of chassis < threshold)
        # chassis body pos is index 1 (0 is world) usually, but better to check by name
        # "chassis" body
        # But we have sensors. Let's use base_pos sensor if available, or direct access.
        # Let's check "chassis" body position directly.
        chassis_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "chassis")
        if chassis_id != -1:
            z_pos = self.data.xpos[chassis_id][2]
            if z_pos < 0.05:  # Threshold for falling
                terminated = True
                reward -= 10.0  # Penalty for falling

        return obs, reward, terminated, truncated, info

    def _get_obs(self):
        obs_list = []
        for sensor in self.config.sensors:
            val = sensor.extract_fn(self.model, self.data)
            if isinstance(val, (float, int)):
                obs_list.append([val])
            else:
                obs_list.append(val)
        return np.concatenate(obs_list).astype(np.float32)

    def render(self):
        if self.render_mode == "human":
            if self.viewer is None:
                from mujoco import viewer

                self.viewer = viewer.launch_passive(self.model, self.data)
            self.viewer.sync()
        elif self.render_mode == "rgb_array":
            # Implement offscreen rendering if needed
            pass

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
