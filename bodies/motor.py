from typing import Any, Dict

from model_builder import MujocoBuilderBase, add


class MotorBuilder(MujocoBuilderBase):
    BODY_NAME = "motor_rotor"
    BODY_POS = "0.027 0.05 0.0098"
    COLOR = "0.3 0.8 0.3 1"

    ROTOR_RADIUS = 0.002
    ROTOR_HEIGHT = 0.001

    ARM_SIZE = (0.0075, 0.0005, 0.002)

    SHAFT_RADIUS = 0.001
    SHAFT_HEIGHT = 0.0080

    def __init__(self, parent, idx: int, overrides: Dict[str, Any] = None):
        super().__init__(self.COLOR)
        self.idx = idx
        self.parent = parent
        self.overrides = overrides or {}
        self.rotor = None
        self.body_pos = self.overrides.pop("pos", self.BODY_POS)

    def build(self):
        self._create_body()
        self.add_joint(self.rotor, f"motor_joint_{self.idx}")
        self._add_rotor()
        self._add_arm()
        self._add_shaft()
        return self.rotor

    @staticmethod
    def build_motor_rotor(parent, idx: int, overrides=None):
        return MotorBuilder(parent, idx, overrides).build()

    def _create_body(self):
        attrs = {"name": f"{self.BODY_NAME}_{self.idx}", "pos": self.body_pos}
        attrs.update({k: str(v) for k, v in self.overrides.items()})
        self.rotor = add(self.parent, "body", **attrs)

    def _add_rotor(self):
        hr = self.ROTOR_RADIUS / 2
        hh = self.ROTOR_HEIGHT / 2
        euler = "1.57 0 0"
        self.add_cylinder(
            self.rotor,
            f"motor_geom_{self.idx}",
            f"{hr} {hh}",
            f"0 {self.ROTOR_HEIGHT / 2} 0",
            rgba=self.color,
            euler=euler,
            mass="0.1",
        )

    def _add_arm(self):
        hx, hy, hz = self.ARM_SIZE[0] / 2, self.ARM_SIZE[1] / 2, self.ARM_SIZE[2] / 2
        ARM_X = self.ARM_SIZE[0] / 2
        ARM_Y = self.ROTOR_HEIGHT - self.ARM_SIZE[1] / 2
        ARM_Z = 0
        self.add_box(
            self.rotor,
            f"motor_arm_{self.idx}",
            f"{hx} {hy} {hz}",
            f"{ARM_X} {ARM_Y} {ARM_Z}",
            mass="0.1",
        )

    def _add_shaft(self):
        SHAFT_X = self.ARM_SIZE[0]
        SHAFT_Y = self.ROTOR_HEIGHT + self.SHAFT_HEIGHT - self.ARM_SIZE[1]
        SHAFT_Z = 0
        # Put the shaft on its own child body so its joint is properly scoped
        shaft_body = add(
            self.rotor,
            "body",
            name=f"motor_shaft_body_{self.idx}",
            pos=f"{SHAFT_X} {SHAFT_Y} {SHAFT_Z}",
        )
        self.add_joint(shaft_body, f"motor_shaft_joint_{self.idx}")
        self.add_cylinder(
            shaft_body,
            f"motor_shaft_{self.idx}",
            f"{self.SHAFT_RADIUS} {self.SHAFT_HEIGHT}",
            "0 0 0",
            rgba=self.color,
            euler="1.57 0 0",
            mass="0.1",
        )
        # Site at the shaft tip for connecting to other components
        self.add_site(
            shaft_body, f"motor_shaft_site_{self.idx}", f"0 {0} 0", rgba="0.9 0.2 0.2 1"
        )
        # Stack an additional shaft segment as a child of the shaft body
        stacked_offset_y = (
            self.SHAFT_HEIGHT * 2
        )  # end-to-end offset along the shaft axis
        stacked_body = add(
            shaft_body,
            "body",
            name=f"motor_shaft_body_ext_{self.idx}",
            pos=f"0 {stacked_offset_y} 0",
        )
        self.add_joint(stacked_body, f"motor_shaft_joint_ext_{self.idx}")
        self.add_cylinder(
            stacked_body,
            f"motor_shaft_ext_{self.idx}",
            f"{self.SHAFT_RADIUS} {self.SHAFT_HEIGHT}",
            "0 0 0",
            rgba=self.color,
            euler="1.57 0 0",
            mass="0.1",
        )
        # Site at the end of the extended shaft for downstream connections
        self.add_site(
            stacked_body,
            f"motor_shaft_ext_site_{self.idx}",
            f"0 {0} 0",
            rgba="0.9 0.2 0.2 1",
        )


def build_motor_rotor(chassis, idx: int, overrides: Dict[str, Any] = None):
    return MotorBuilder.build_motor_rotor(chassis, idx, overrides)
