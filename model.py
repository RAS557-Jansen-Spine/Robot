import mujoco
import mujoco.viewer

model = mujoco.MjModel.from_xml_path("jansen_linkage.xml")
data = mujoco.MjData(model)

# Set constant velocity for the crank (30 units/sec)
data.ctrl[0] = 30

with mujoco.viewer.launch_passive(model, data) as viewer:
    while viewer.is_running():
        mujoco.mj_step(model, data)
        viewer.sync()
