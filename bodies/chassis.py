from typing import Any, Dict

from model_builder import MujocoBuilderBase, add

from .motor import MotorBuilder
from .spine import build_spine
from .wedges import build_wedges


class ChassisBuilder(MujocoBuilderBase):
    COLOR = "0.8 0.3 0.3 1"
    BODY_POS = "0 0 0.15"
    CHASSIS_SIZE = (0.15, 0.025, 0.03)

    CHASSIS_MASS = 10

    WALL_THICKNESS = 0.004

    CASE_SIZE = (0.08, 0.1, 0.01)
    CASE_THICKNESS = 0.002
    CASE_OFFSET = (0.0, 0.0, 0.0)

    SUPPORT_RADIUS = 0.005
    SUPPORT_1 = 0.01
    SUPPORT_2 = 0.1
    SUPPORT_3 = 0.005
    # (x, y, z) offsets for each vertical support
    SUPPORT_OFFSETS = [(-0.02, 0.0, 0), (0.02, 0.0, 0)]

    LEG_SUPPORT_SIZE = (0.005, 0.01, 0.03)

    LEG_SHAFT_RADIUS = 0.002
    LEG_SHAFT_HEIGHT = 0.002

    LEG_MOTOR_SIZE = (0.04, 0.02, 0.02)

    def __init__(
        self,
        worldbody,
        assets=None,
        include_motor=False,
        include_wedges=False,
        include_spine=False,
        overrides: Dict[str, Any] = None,
    ):
        super().__init__(self.COLOR)
        self.worldbody = worldbody
        self.assets = assets
        self.include_motor = include_motor
        self.include_wedges = include_wedges
        self.include_spine = include_spine
        self.overrides = overrides or {}
        self.chassis = None

        self.half_x = self.CHASSIS_SIZE[0] / 2
        self.half_y = self.CHASSIS_SIZE[1] / 2
        self.half_z = self.CHASSIS_SIZE[2] / 2

        self.case_half_x = self.CASE_SIZE[0] / 2
        self.case_half_y = self.CASE_SIZE[1] / 2
        self.case_half_z = self.CASE_SIZE[2] / 2

    def build(self):
        self._add_floor()
        self._create_body()
        self._create_shell()
        self._add_board_supports()
        self._add_board_case()
        self._add_leg_supports()
        self._add_leg_shaft()
        self._add_leg_motors()
        self._attach_subassemblies()
        self._add_camera()
        return self.chassis

    # region public helpers -------------------------------------------------

    @staticmethod
    def build_chassis(
        worldbody,
        assets=None,
        include_motor=True,
        include_wedges=True,
        include_spine=False,
        overrides=None,
    ):
        builder = ChassisBuilder(
            worldbody, assets, include_motor, include_wedges, include_spine, overrides
        )
        return builder.build()

    # endregion -------------------------------------------------------------

    def _add_floor(self):
        add(
            self.worldbody,
            "geom",
            name="floor",
            type="plane",
            size="10 10 0.1",
            material="floor_mat",
            rgba="0.8 0.8 0.8 1",
        )

    def _create_body(self):
        chassis_attrs = {"name": "chassis", "pos": self.BODY_POS}
        chassis_attrs.update({k: str(v) for k, v in self.overrides.items()})
        self.chassis = add(self.worldbody, "body", **chassis_attrs)

        # Let the whole system move freely in 6 DOF
        add(self.chassis, "joint", name="root_free", type="free")
        # or equivalently: add(self.chassis, "freejoint")

    def _create_shell(self):
        wall = self.WALL_THICKNESS / 2
        hx, hy, hz = self.half_x, self.half_y, self.half_z

        z_pos = hz - wall
        self.add_box(
            self.chassis,
            "chassis_top",
            f"{hx} {hy} {wall}",
            f"0 0 {z_pos}",
            mass=self.CHASSIS_MASS,
        )
        self.add_box(
            self.chassis,
            "chassis_bottom",
            f"{hx} {hy} {wall}",
            f"0 0 {-z_pos}",
            mass=self.CHASSIS_MASS,
        )

        y_pos = hy - wall
        self.add_box(
            self.chassis,
            "chassis_front",
            f"{hx} {wall} {hz}",
            f"0 {y_pos} 0",
            mass=self.CHASSIS_MASS,
        )
        self.add_box(
            self.chassis,
            "chassis_back",
            f"{hx} {wall} {hz}",
            f"0 {-y_pos} 0",
            mass=self.CHASSIS_MASS,
        )

    def _add_board_supports(self):
        wall = self.WALL_THICKNESS / 2
        support_1_base = [0.0, 0.0, self.half_z + self.SUPPORT_1 / 2 + wall + wall * 2]
        support_2_base = self._offset_vector(
            support_1_base, dy=-self.SUPPORT_2, dz=self.SUPPORT_1
        )
        support_3_base = self._offset_vector(
            support_2_base, dy=-self.SUPPORT_2, dz=self.SUPPORT_3
        )
        self.case_base = support_3_base

        for idx, (off_x, off_y, off_z) in enumerate(self.SUPPORT_OFFSETS, start=1):
            pos_1_vec = self._offset_vector(
                support_1_base, dx=off_x, dy=off_y, dz=off_z
            )
            pos_2_vec = self._offset_vector(
                support_2_base, dx=off_x, dy=off_y, dz=off_z
            )
            pos_3_vec = self._offset_vector(
                support_3_base, dx=off_x, dy=off_y, dz=off_z
            )
            pos_1 = self._format_pos(pos_1_vec)
            pos_2 = self._format_pos(pos_2_vec)
            pos_3 = self._format_pos(pos_3_vec)
            self.add_cylinder(
                self.chassis,
                f"support_{idx}_1",
                f"{self.SUPPORT_RADIUS} {self.SUPPORT_1}",
                pos_1,
            )
            self.add_cylinder(
                self.chassis,
                f"support_{idx}_2",
                f"{self.SUPPORT_RADIUS} {self.SUPPORT_2}",
                pos_2,
                euler="1.57 0 0",
            )
            self.add_cylinder(
                self.chassis,
                f"support_{idx}_3",
                f"{self.SUPPORT_RADIUS} {self.SUPPORT_3}",
                pos_3,
            )

    def _add_board_case(self):
        wall = self.CASE_THICKNESS / 2
        hx, hy, hz = self.case_half_x, self.case_half_y, self.case_half_z
        case_base = self._offset_vector(
            self.case_base,
            dx=self.CASE_OFFSET[0],
            dy=self.CASE_OFFSET[1],
            dz=self.CASE_OFFSET[2] + self.SUPPORT_3 + self.CASE_SIZE[2] / 2,
        )

        z_pos = hz - wall
        self.add_box(
            self.chassis,
            "case_bottom",
            f"{hx} {hy} {wall}",
            f"{case_base[0]} {case_base[1]} {case_base[2] - z_pos}",
        )

        y_pos = hy - wall
        self.add_box(
            self.chassis,
            "case_front",
            f"{hx} {wall} {hz}",
            f"{case_base[0]} {case_base[1] + y_pos} {case_base[2]}",
        )
        self.add_box(
            self.chassis,
            "case_back",
            f"{hx} {wall} {hz}",
            f"{case_base[0]} {case_base[1] - y_pos} {case_base[2]}",
        )

        x_pos = hx - wall
        self.add_box(
            self.chassis,
            "case_left",
            f"{wall} {hy} {hz}",
            f"{case_base[0] - x_pos} {case_base[1]} {case_base[2]}",
        )
        self.add_box(
            self.chassis,
            "case_right",
            f"{wall} {hy} {hz}",
            f"{case_base[0] + x_pos} {case_base[1]} {case_base[2]}",
        )

    def _add_leg_supports(self):
        hx, hy, hz = (
            self.LEG_SUPPORT_SIZE[0] / 2,
            self.LEG_SUPPORT_SIZE[1] / 2,
            self.LEG_SUPPORT_SIZE[2] / 2,
        )

        self.add_box(
            self.chassis,
            "leg_support_left",
            f"{hx} {hy} {hz}",
            f"{-self.CHASSIS_SIZE[0] / 2 + hx} {-self.CHASSIS_SIZE[1] / 2 - hy} {0}",
        )
        self.add_box(
            self.chassis,
            "leg_support_right",
            f"{hx} {hy} {hz}",
            f"{self.CHASSIS_SIZE[0] / 2 - hx} {-self.CHASSIS_SIZE[1] / 2 - hy} {0}",
        )

    def _add_leg_shaft(self):
        hr = self.LEG_SHAFT_RADIUS / 2
        hh = self.LEG_SHAFT_HEIGHT / 2
        euler_left = "0 1.57 0"
        euler_right = "0 1.57 0"

        self.add_cylinder(
            self.chassis,
            "leg_shaft_left",
            f"{hr} {hh}",
            f"{-self.CHASSIS_SIZE[0] / 2} {self.CHASSIS_SIZE[1] / 2 + self.LEG_MOTOR_SIZE[1] / 2 - self.LEG_SHAFT_RADIUS - 0.038 + self.LEG_SHAFT_RADIUS} {-0.0078}",
            euler=euler_left,
        )
        self.add_cylinder(
            self.chassis,
            "leg_shaft_right",
            f"{hr} {hh}",
            f"{self.CHASSIS_SIZE[0] / 2} {self.CHASSIS_SIZE[1] / 2 + self.LEG_MOTOR_SIZE[1] / 2 - self.LEG_SHAFT_RADIUS - 0.038 + self.LEG_SHAFT_RADIUS} {-0.0078}",
            euler=euler_right,
        )

    def _add_leg_motors(self):
        hx, hy, hz = (
            self.LEG_MOTOR_SIZE[0] / 2,
            self.LEG_MOTOR_SIZE[1] / 2,
            self.LEG_MOTOR_SIZE[2] / 2,
        )
        self.add_box(
            self.chassis,
            "leg_motor_left",
            f"{hx} {hy} {hz}",
            f"{-self.CHASSIS_SIZE[0] / 2 + hx} {self.CHASSIS_SIZE[1] / 2 + hy} {0}",
        )
        self.add_box(
            self.chassis,
            "leg_motor_right",
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
                self.chassis, 1, overrides={"pos": motor_1_pos, "euler": motor_1_euler}
            )
            MotorBuilder.build_motor_rotor(
                self.chassis, 2, overrides={"pos": motor_2_pos, "euler": motor_2_euler}
            )
        if self.include_wedges:
            leg_1_support = f"{self.CHASSIS_SIZE[0] / 2 + 0.002} {self.CHASSIS_SIZE[1] / 2 + self.LEG_MOTOR_SIZE[1] / 2 - 0.038} {-0.0078}"
            leg_1_euler = "0 0 -1.57"
            build_wedges(
                self.chassis,
                assets=self.assets,
                overrides={"pos": leg_1_support, "euler": leg_1_euler},
                idx=1,
            )
            leg_2_support = f"{-self.CHASSIS_SIZE[0] / 2 - 0.002 - 0.03} {self.CHASSIS_SIZE[1] / 2 + self.LEG_MOTOR_SIZE[1] / 2 - 0.038} {-0.0078}"
            leg_2_euler = "0 0 -1.57"
            build_wedges(
                self.chassis,
                assets=self.assets,
                overrides={"pos": leg_2_support, "euler": leg_2_euler},
                idx=2,
            )
        if self.include_spine:
            spine_support = f"{0.0} {-0.0125} {0.0}"
            spine_euler = "0 0 0"
            build_spine(
                self.chassis,
                assets=self.assets,
                overrides={"pos": spine_support, "euler": spine_euler},
            )

    def _add_camera(self):
        add(self.worldbody, "camera", name="cam", pos="0.1 -0.15 0.6", euler="0 0 0")


def build_chassis(
    worldbody,
    assets=None,
    include_motor: bool = True,
    include_wedges: bool = True,
    include_spine: bool = False,
    overrides: Dict[str, Any] = None,
):
    return ChassisBuilder.build_chassis(
        worldbody, assets, include_motor, include_wedges, include_spine, overrides
    )
