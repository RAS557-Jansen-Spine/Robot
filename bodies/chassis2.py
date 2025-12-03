from typing import Any, Dict

from model_builder import MujocoBuilderBase, add

from .motor import MotorBuilder
from .wedges import build_wedges


class Chassis2Builder(MujocoBuilderBase):
    COLOR = "0.8 0.3 0.3 1"
    BODY_POS = "0 0 0"
    CHASSIS_SIZE = (0.15, 0.02, 0.03)
    CHASSIS_MASS = 20
    WALL_THICKNESS = 0.004

    LEG_SUPPORT_SIZE = (0.005, 0.01, 0.03)
    LEG_SHAFT_RADIUS = 0.002
    LEG_SHAFT_HEIGHT = 0.002
    LEG_MOTOR_SIZE = (0.04, 0.02, 0.02)

    def __init__(
        self,
        parent,
        assets=None,
        *,
        include_motor: bool = False,
        include_wedges: bool = False,
        idx_offset: int = 3,
        overrides: Dict[str, Any] = None,
    ):
        super().__init__(self.COLOR)
        self.parent = parent
        self.assets = assets
        self.include_motor = include_motor
        self.include_wedges = include_wedges
        self.idx_offset = idx_offset
        self.overrides = overrides or {}
        self.chassis = None

        self.half_x = self.CHASSIS_SIZE[0] / 2
        self.half_y = self.CHASSIS_SIZE[1] / 2
        self.half_z = self.CHASSIS_SIZE[2] / 2

    def build(self):
        self._create_body()
        self._create_shell()
        self._add_leg_supports()
        self._add_leg_shaft()
        self._add_leg_motors()
        self._attach_subassemblies()
        return self.chassis

    @staticmethod
    def build_chassis2(
        parent,
        assets=None,
        *,
        include_motor=True,
        include_wedges=True,
        idx_offset: int = 3,
        overrides=None,
    ):
        builder = Chassis2Builder(
            parent,
            assets,
            include_motor=include_motor,
            include_wedges=include_wedges,
            idx_offset=idx_offset,
            overrides=overrides,
        )
        return builder.build()

    def _create_body(self):
        attrs = {"name": "chassis2", "pos": self.BODY_POS}
        attrs.update({k: str(v) for k, v in self.overrides.items()})
        self.chassis = add(self.parent, "body", **attrs)

    def _create_shell(self):
        wall = self.WALL_THICKNESS / 2
        hx, hy, hz = self.half_x, self.half_y, self.half_z

        z_pos = hz - wall
        self.add_box(
            self.chassis,
            "chassis2_top",
            f"{hx} {hy} {wall}",
            f"0 0 {z_pos}",
            mass=self.CHASSIS_MASS,
        )
        self.add_box(
            self.chassis,
            "chassis2_bottom",
            f"{hx} {hy} {wall}",
            f"0 0 {-z_pos}",
            mass=self.CHASSIS_MASS,
        )

        y_pos = hy - wall
        self.add_box(
            self.chassis,
            "chassis2_front",
            f"{hx} {wall} {hz}",
            f"0 {y_pos} 0",
            mass=self.CHASSIS_MASS,
        )
        self.add_box(
            self.chassis,
            "chassis2_back",
            f"{hx} {wall} {hz}",
            f"0 {-y_pos} 0",
            mass=self.CHASSIS_MASS,
        )

    def _add_leg_supports(self):
        hx, hy, hz = (
            self.LEG_SUPPORT_SIZE[0] / 2,
            self.LEG_SUPPORT_SIZE[1] / 2,
            self.LEG_SUPPORT_SIZE[2] / 2,
        )
        self.add_box(
            self.chassis,
            "leg_support_left_2",
            f"{hx} {hy} {hz}",
            f"{-self.CHASSIS_SIZE[0] / 2 + hx} {-self.CHASSIS_SIZE[1] / 2 - hy} {0}",
        )
        self.add_box(
            self.chassis,
            "leg_support_right_2",
            f"{hx} {hy} {hz}",
            f"{self.CHASSIS_SIZE[0] / 2 - hx} {-self.CHASSIS_SIZE[1] / 2 - hy} {0}",
        )

    def _add_leg_shaft(self):
        hr = self.LEG_SHAFT_RADIUS / 2
        hh = self.LEG_SHAFT_HEIGHT / 2
        euler = "0 1.57 0"

        self.add_cylinder(
            self.chassis,
            "leg_shaft_left_2",
            f"{hr} {hh}",
            f"{-self.CHASSIS_SIZE[0] / 2} {self.CHASSIS_SIZE[1] / 2 + self.LEG_MOTOR_SIZE[1] / 2 - self.LEG_SHAFT_RADIUS - 0.038 + self.LEG_SHAFT_RADIUS} {-0.0078}",
            euler=euler,
        )
        self.add_cylinder(
            self.chassis,
            "leg_shaft_right_2",
            f"{hr} {hh}",
            f"{self.CHASSIS_SIZE[0] / 2} {self.CHASSIS_SIZE[1] / 2 + self.LEG_MOTOR_SIZE[1] / 2 - self.LEG_SHAFT_RADIUS - 0.038 + self.LEG_SHAFT_RADIUS} {-0.0078}",
            euler=euler,
        )

    def _add_leg_motors(self):
        hx, hy, hz = (
            self.LEG_MOTOR_SIZE[0] / 2,
            self.LEG_MOTOR_SIZE[1] / 2,
            self.LEG_MOTOR_SIZE[2] / 2,
        )
        self.add_box(
            self.chassis,
            "leg_motor_left_2",
            f"{hx} {hy} {hz}",
            f"{-self.CHASSIS_SIZE[0] / 2 + hx} {self.CHASSIS_SIZE[1] / 2 + hy} {0}",
        )
        self.add_box(
            self.chassis,
            "leg_motor_right_2",
            f"{hx} {hy} {hz}",
            f"{self.CHASSIS_SIZE[0] / 2 - hx} {self.CHASSIS_SIZE[1] / 2 + hy} {0}",
        )

    def _attach_subassemblies(self):
        if self.include_motor:
            motor_1_pos = f"{self.CHASSIS_SIZE[0] / 2 + 0.0001} {self.CHASSIS_SIZE[1] / 2 + self.LEG_MOTOR_SIZE[1] / 2} {0}"
            motor_2_pos = f"{-self.CHASSIS_SIZE[0] / 2 - 0.0001} {self.CHASSIS_SIZE[1] / 2 + self.LEG_MOTOR_SIZE[1] / 2} {0}"
            motor_1_euler = "0 0 -1.57"
            motor_2_euler = "3.14 0 1.57"
            MotorBuilder.build_motor_rotor(
                self.chassis,
                self.idx_offset,
                overrides={"pos": motor_1_pos, "euler": motor_1_euler},
            )
            MotorBuilder.build_motor_rotor(
                self.chassis,
                self.idx_offset + 1,
                overrides={"pos": motor_2_pos, "euler": motor_2_euler},
            )
        if self.include_wedges:
            leg_1_support = f"{self.CHASSIS_SIZE[0] / 2 + 0.002} {self.CHASSIS_SIZE[1] / 2 + self.LEG_MOTOR_SIZE[1] / 2 - 0.038} {-0.0078}"
            leg_1_euler = "0 0 -1.57"
            build_wedges(
                self.chassis,
                assets=self.assets,
                overrides={"pos": leg_1_support, "euler": leg_1_euler},
                idx=self.idx_offset,
            )
            leg_2_support = f"{-self.CHASSIS_SIZE[0] / 2 - 0.002 - 0.03} {self.CHASSIS_SIZE[1] / 2 + self.LEG_MOTOR_SIZE[1] / 2 - 0.038} {-0.0078}"
            leg_2_euler = "0 0 -1.57"
            build_wedges(
                self.chassis,
                assets=self.assets,
                overrides={"pos": leg_2_support, "euler": leg_2_euler},
                idx=self.idx_offset + 1,
            )


def build_chassis2(
    parent,
    assets=None,
    *,
    include_motor: bool = True,
    include_wedges: bool = True,
    idx_offset: int = 3,
    overrides: Dict[str, Any] = None,
):
    return Chassis2Builder.build_chassis2(
        parent,
        assets,
        include_motor=include_motor,
        include_wedges=include_wedges,
        idx_offset=idx_offset,
        overrides=overrides,
    )
