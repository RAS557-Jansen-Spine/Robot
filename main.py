import argparse
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import mujoco
import numpy as np
from mujoco import viewer

from live_plotter import LivePlotter
from model_builder import build_model, prettify
from robot_env import RobotEnv

# ==========================================
# Subcommand: Generate
# ==========================================


def generate_model(output_path: Path, model_name: str):
    mujoco_elem = build_model(model_name)
    xml_str = prettify(mujoco_elem)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(xml_str)
    print(f"Wrote {output_path}")
    return output_path


def cmd_generate(args):
    generate_model(args.output, args.model_name)


# ==========================================
# Subcommand: View
# ==========================================


def _load_init_qpos_from_yaml(path: Path) -> Dict[str, List[float]]:
    if not path.exists():
        return {}
    try:
        import yaml
    except ImportError:
        print("PyYAML not installed, skipping init qpos.")
        return {}

    raw = yaml.safe_load(path.read_text()) or {}
    qpos_section = raw.get("initial_qpos", raw)
    parsed: Dict[str, List[float]] = {}
    for joint, vals in qpos_section.items():
        if isinstance(vals, (int, float)):
            parsed[joint] = [float(vals)]
        elif isinstance(vals, Iterable) and not isinstance(vals, (str, bytes)):
            parsed[joint] = [float(v) for v in vals]
    return parsed


def _apply_initial_positions(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    qpos_overrides: Dict[str, Sequence[float]],
):
    if not qpos_overrides:
        return

    for joint_name, values in qpos_overrides.items():
        jnt_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, joint_name)
        if jnt_id == -1:
            continue
        adr = model.jnt_qposadr[jnt_id]
        jnt_type = model.jnt_type[jnt_id]

        if (
            jnt_type == mujoco.mjtJoint.mjJNT_HINGE
            or jnt_type == mujoco.mjtJoint.mjJNT_SLIDE
        ):
            expected = 1
        elif jnt_type == mujoco.mjtJoint.mjJNT_BALL:
            expected = 4
        elif jnt_type == mujoco.mjtJoint.mjJNT_FREE:
            expected = 7
        else:
            continue

        if len(values) == expected:
            data.qpos[adr : adr + expected] = values


def cmd_view(args):
    out_path = generate_model(args.output, args.model_name)
    model = mujoco.MjModel.from_xml_path(str(out_path))
    data = mujoco.MjData(model)

    init_qpos = _load_init_qpos_from_yaml(args.config)
    _apply_initial_positions(model, data, init_qpos)

    # Live Plotter
    plotter = None
    if args.plot:
        # Assuming 4 motors based on RobotConfig
        plotter = LivePlotter(num_motors=4)
        plotter.start()

    print("Launching viewer... Press Ctrl+C to exit.")
    try:
        with viewer.launch_passive(model, data) as v:
            v.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
            v.cam.lookat[:] = (-0.015, -0.04, 0.05)
            v.cam.distance = 0.25
            v.cam.elevation = -10
            v.cam.azimuth = 120

            last = time.time()
            while v.is_running():
                now = time.time()
                while now - last < model.opt.timestep:
                    time.sleep(0.0005)
                    now = time.time()
                last = now

                # Simple demo: spin motors
                if args.demo_spin:
                    data.ctrl[:] = 0.0
                    # Assuming 4 motors
                    if model.nu >= 4:
                        data.ctrl[0] = 2.0
                        data.ctrl[1] = -2.0
                        data.ctrl[2] = 2.0
                        data.ctrl[3] = -2.0

                mujoco.mj_step(model, data)
                v.sync()

                if plotter:
                    # Extract motor qpos/qvel (assuming 4 motors after 7 free joint dofs)
                    if model.nq >= 11:
                        motor_qpos = data.qpos[7:11]
                        motor_qvel = data.qvel[6:10]

                        # Motor Control & Forces
                        # Assuming 4 actuators
                        if data.ctrl.shape[0] >= 4:
                            ctrl = data.ctrl[:4]
                            qfrc = data.qfrc_actuator[
                                6:10
                            ]  # Forces on the 4 motor joints
                        else:
                            ctrl = np.zeros(4)
                            qfrc = np.zeros(4)

                        # Base Pos & Quat
                        base_pos = data.qpos[:3]
                        base_quat = data.qpos[3:7]

                        plotter.put_data(
                            data.time,
                            motor_qpos,
                            motor_qvel,
                            ctrl,
                            qfrc,
                            base_pos,
                            base_quat,
                        )
    except RuntimeError as exc:
        if "launch_passive" in str(exc) and "mjpython" in str(exc):
            print(
                "Viewer requires mjpython on macOS. Run with: mjpython main.py view ..."
            )
        else:
            raise
    except KeyboardInterrupt:
        pass
    finally:
        if plotter:
            plotter.stop()


# ==========================================
# Subcommand: Check
# ==========================================


def cmd_check(args):
    model_path = args.output
    if not model_path.exists():
        print(f"Model not found at {model_path}. Generating...")
        generate_model(model_path, "Model")

    try:
        model = mujoco.MjModel.from_xml_path(str(model_path))
        data = mujoco.MjData(model)
        mujoco.mj_step(model, data)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Check positions
    case_bottom_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "case_bottom")
    floor_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor")

    if case_bottom_id != -1 and floor_id != -1:
        case_bottom_pos = data.geom_xpos[case_bottom_id]
        floor_pos = data.geom_xpos[floor_id]
        print(f"Position of 'case_bottom': {case_bottom_pos}")
        print(f"Position of 'floor': {floor_pos}")
        print(f"Relative Position: {case_bottom_pos - floor_pos}")
    else:
        print("Could not find 'case_bottom' or 'floor' geoms.")


# ==========================================
# Subcommand: Train
# ==========================================


def cmd_train(args):
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.env_checker import check_env
    except ImportError:
        print("stable-baselines3 not installed. Cannot train.")
        return

    env = RobotEnv(model_path=str(args.output))
    print("Checking environment...")
    check_env(env)
    print("Environment check passed!")

    print("Starting training...")
    model = PPO("MlpPolicy", env, verbose=1, device="auto")
    model.learn(total_timesteps=args.timesteps)
    print("Training finished!")

    model.save(args.save_path)
    print(f"Model saved to {args.save_path}")


# ==========================================
# Subcommand: Run (Agent)
# ==========================================


def cmd_run(args):
    try:
        from stable_baselines3 import PPO
    except ImportError:
        print("stable-baselines3 not installed. Cannot run agent.")
        return

    env = RobotEnv(model_path=str(args.output), render_mode="human")
    print(f"Loading model from {args.load_path}...")
    try:
        model = PPO.load(args.load_path)
    except FileNotFoundError:
        print("Model file not found.")
        return

    obs, _ = env.reset()
    obs, _ = env.reset()

    # Live Plotter
    plotter = None
    if args.plot:
        plotter = LivePlotter(num_motors=4)
        plotter.start()

    print("Running agent... Press Ctrl+C to stop.")
    try:
        while True:
            action, _ = model.predict(obs, deterministic=True)
            obs, _, terminated, truncated, _ = env.step(action)
            obs, _, terminated, truncated, _ = env.step(action)
            env.render()

            if plotter:
                if env.model.nq >= 11:
                    motor_qpos = env.data.qpos[7:11]
                    motor_qvel = env.data.qvel[6:10]

                    if env.data.ctrl.shape[0] >= 4:
                        ctrl = env.data.ctrl[:4]
                        qfrc = env.data.qfrc_actuator[6:10]
                    else:
                        ctrl = np.zeros(4)
                        qfrc = np.zeros(4)

                    base_pos = env.data.qpos[:3]
                    base_quat = env.data.qpos[3:7]

                    plotter.put_data(
                        env.data.time,
                        motor_qpos,
                        motor_qvel,
                        ctrl,
                        qfrc,
                        base_pos,
                        base_quat,
                    )

            if terminated or truncated:
                obs, _ = env.reset()
                time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        env.close()
        if plotter:
            plotter.stop()


# ==========================================
# Main CLI
# ==========================================


def main():
    parser = argparse.ArgumentParser(description="Robot Project CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common args
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/model.xml"),
        help="Path to model XML",
    )
    parent_parser.add_argument(
        "--model-name", default="Model", help="Name of the model"
    )

    # Generate
    p_gen = subparsers.add_parser(
        "generate", parents=[parent_parser], help="Generate MuJoCo XML"
    )
    p_gen.set_defaults(func=cmd_generate)

    # View
    p_view = subparsers.add_parser(
        "view", parents=[parent_parser], help="View the model"
    )
    p_view.add_argument(
        "--config",
        type=Path,
        default=Path("config/init_qpos.yaml"),
        help="Init qpos config",
    )
    p_view.add_argument("--demo-spin", action="store_true", help="Spin motors for demo")
    p_view.add_argument("--plot", action="store_true", help="Enable live plotting")
    p_view.set_defaults(func=cmd_view)

    # Check
    p_check = subparsers.add_parser(
        "check", parents=[parent_parser], help="Check model properties"
    )
    p_check.set_defaults(func=cmd_check)

    # Train
    p_train = subparsers.add_parser(
        "train", parents=[parent_parser], help="Train RL agent"
    )
    p_train.add_argument(
        "--timesteps", type=int, default=100000, help="Total timesteps"
    )
    p_train.add_argument(
        "--save-path", default="ppo_robot_walker", help="Path to save model"
    )
    p_train.set_defaults(func=cmd_train)

    # Run
    p_run = subparsers.add_parser(
        "run", parents=[parent_parser], help="Run trained agent"
    )
    p_run.add_argument(
        "--load-path", default="ppo_robot_walker", help="Path to load model"
    )
    p_run.add_argument("--plot", action="store_true", help="Enable live plotting")
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
