from typing import Any, Dict, Optional

from model_builder import MujocoBuilderBase, add

from .chassis2 import Chassis2Builder


class SpineBuilder(MujocoBuilderBase):
    BODY_NAME = "spine"
    BODY_POS = "0 0 0"
    COLOR = "0.8 0.3 0.3 1"
    INNER_JOINT_SUPPORT_SIZE = (0.001, 0.015, 0.028)

    INNER_SHAFT_SIZE = (0.001, 0.06, 0.028)

    OUTER_JOINT_SUPPORT_SIZE = (0.001, 0.030, 0.030)

    OUTER_SHAFT_SIZE = (0.001, 0.03, 0.030)

    SPIN_COVER_SIZE = (0.030, 0.030, 0.001)

    def __init__(
        self, parent, assets=None, *, overrides: Optional[Dict[str, Any]] = None
    ):
        super().__init__(self.COLOR)
        self.parent = parent
        self.assets = assets
        self.overrides = dict(overrides or {})
        self.body_pos = self.overrides.pop("pos", self.BODY_POS)
        self.body_euler = self.overrides.pop("euler", None)
        self.spine = None

    def build(self):
        self._create_body()
        self._add_inner_segments()
        self._add_outer_segments_1()
        self._add_outer_segments_2()
        # self._add_sites()
        return self.spine

    @staticmethod
    def build_spine(parent, assets=None, overrides: Optional[Dict[str, Any]] = None):
        builder = SpineBuilder(parent, assets=assets, overrides=overrides)
        return builder.build()

    def _create_body(self):
        attrs = {"name": self.BODY_NAME, "pos": self.body_pos}
        if self.body_euler:
            attrs["euler"] = self.body_euler
        attrs.update({k: str(v) for k, v in self.overrides.items()})
        self.spine = add(self.parent, "body", **attrs)

    def _add_inner_segments(self):
        hx = self.INNER_JOINT_SUPPORT_SIZE[0] / 2
        hy = self.INNER_JOINT_SUPPORT_SIZE[1] / 2
        hz = self.INNER_JOINT_SUPPORT_SIZE[2] / 2

        cover_hx = self.SPIN_COVER_SIZE[0] / 2
        cover_hy = self.SPIN_COVER_SIZE[1] / 2
        cover_hz = self.SPIN_COVER_SIZE[2] / 2

        size = f"{hx} {hy} {hz}"
        cover_size = f"{cover_hx} {cover_hy} {cover_hz}"

        pos = f"{0} {0} {0}"
        cover_pos = f"{0} {hy - cover_hy} {-hz - cover_hz}"
        cover_pos_2 = f"{0} {hy - cover_hy} {hz + cover_hz}"

        name = f"inner_segment_1"
        cover_name = f"inner_segment_1_cover"
        cover_name_2 = f"inner_segment_1_cover_2"
        self.inner_segment = add(self.spine, "body", name=name, pos=f"0 {-hy} 0")
        self.add_box(self.inner_segment, name, size, pos, rgba=self.color)
        self.add_box(
            self.inner_segment, cover_name, cover_size, cover_pos, rgba=self.color
        )
        self.add_box(
            self.inner_segment, cover_name_2, cover_size, cover_pos_2, rgba=self.color
        )

        hx = self.INNER_SHAFT_SIZE[0] / 2
        hy = self.INNER_SHAFT_SIZE[1] / 2
        hz = self.INNER_SHAFT_SIZE[2] / 2
        size = f"{hx} {hy} {hz}"
        pos = f"{0} {-hy} {0}"
        name = f"inner_shaft"
        inner_shaft = add(
            self.inner_segment,
            "body",
            name=name,
            pos=f"0 {-self.INNER_JOINT_SUPPORT_SIZE[1] / 2} 0",
        )
        self.add_joint(inner_shaft, name, axis="0 0 1")
        self.add_box(inner_shaft, name, size, pos, rgba=self.color)

        hx = self.INNER_JOINT_SUPPORT_SIZE[0] / 2
        hy = self.INNER_JOINT_SUPPORT_SIZE[1] / 2
        hz = self.INNER_JOINT_SUPPORT_SIZE[2] / 2
        size = f"{hx} {hy} {hz}"
        pos = f"{0} {-hy} {0}"
        name = f"inner_segment_2"
        cover_name = f"inner_segment_2_cover"
        cover_name_2 = f"inner_segment_2_cover_2"
        cover_pos = f"{0} {0} {-hz - cover_hz}"
        cover_pos_2 = f"{0} {0} {hz + cover_hz}"
        self.inner_segment_2 = add(
            inner_shaft, "body", name=name, pos=f"{0} {-self.INNER_SHAFT_SIZE[1]} {0}"
        )
        self.add_joint(self.inner_segment_2, name, axis="0 0 1")
        self.add_box(self.inner_segment_2, name, size, pos, rgba=self.color)
        self.add_box(
            self.inner_segment_2, cover_name, cover_size, cover_pos, rgba=self.color
        )
        self.add_box(
            self.inner_segment_2, cover_name_2, cover_size, cover_pos_2, rgba=self.color
        )
        self.add_site(
            self.inner_segment_2,
            name="inner_segment_2_site_1",
            pos=f"{-0.015} {-0.015} {0.015}",
            rgba="0.2 0.9 0.2 1",
        )
        self.add_site(
            self.inner_segment_2,
            name="inner_segment_2_site_2",
            pos=f"{-0.015} {0.015} {0.015}",
            rgba="0.2 0.9 0.2 1",
        )
        self.add_site(
            self.inner_segment_2,
            name="inner_segment_2_site_3",
            pos=f"{0.015} {-0.015} {0.015}",
            rgba="0.2 0.9 0.2 1",
        )
        self.add_site(
            self.inner_segment_2,
            name="inner_segment_2_site_4",
            pos=f"{0.015} {0.015} {0.015}",
            rgba="0.2 0.9 0.2 1",
        )
        # Attach a secondary chassis to the inner segment; use an offset so joint/body names stay unique.
        Chassis2Builder.build_chassis2(
            self.inner_segment_2,
            assets=self.assets,
            idx_offset=3,
            overrides={"pos": f"{0.0} {-0.025} {0}", "euler": "0 0 0"},
        )

    def _add_outer_segments_1(self):
        hx = self.OUTER_JOINT_SUPPORT_SIZE[0] / 2
        hy = self.OUTER_JOINT_SUPPORT_SIZE[1] / 2
        hz = self.OUTER_JOINT_SUPPORT_SIZE[2] / 2
        size = f"{hx} {hy} {hz}"
        pos = f"{0} {0} {0}"
        name = f"outer_segment_1_1"
        outer_segment_1 = add(self.spine, "body", name=name, pos=f"{-0.015} {-hy} {0}")
        self.add_box(outer_segment_1, name, size, pos, rgba=self.color)

        hx = self.OUTER_SHAFT_SIZE[0] / 2
        hy = self.OUTER_SHAFT_SIZE[1] / 2
        hz = self.OUTER_SHAFT_SIZE[2] / 2
        size = f"{hx} {hy} {hz}"
        pos = f"{0} {-hy} {0}"
        name = f"outer_shaft_1_1"
        outer_shaft_1 = add(
            outer_segment_1,
            "body",
            name=name,
            pos=f"0 {-self.OUTER_JOINT_SUPPORT_SIZE[1] / 2} 0",
        )
        self.add_joint(outer_shaft_1, name, axis="0 0 1")
        self.add_box(outer_shaft_1, name, size, pos, rgba=self.color)

        hx = self.OUTER_SHAFT_SIZE[0] / 2
        hy = self.OUTER_SHAFT_SIZE[1] / 2
        hz = self.OUTER_SHAFT_SIZE[2] / 2
        size = f"{hx} {hy} {hz}"
        pos = f"{0} {-hy} {0}"
        name = f"outer_shaft_1_2"
        outer_shaft_2 = add(
            outer_shaft_1, "body", name=name, pos=f"0 {-self.OUTER_SHAFT_SIZE[1]} 0"
        )
        self.add_joint(outer_shaft_2, name, axis="0 0 1")
        self.add_box(outer_shaft_2, name, size, pos, rgba=self.color)

        hx = self.OUTER_JOINT_SUPPORT_SIZE[0] / 2
        hy = self.OUTER_JOINT_SUPPORT_SIZE[1] / 2
        hz = self.OUTER_JOINT_SUPPORT_SIZE[2] / 2
        size = f"{hx} {hy} {hz}"
        pos = f"{0} {-hy} {0}"
        name = f"outer_segment_1_2"
        outer_segment_2 = add(
            outer_shaft_2, "body", name=name, pos=f"{0} {-self.OUTER_SHAFT_SIZE[1]} {0}"
        )
        self.add_joint(outer_segment_2, name, axis="0 0 1")
        self.add_box(outer_segment_2, name, size, pos, rgba=self.color)
        self.add_site(
            outer_segment_2,
            name="outer_segment_1_2_site_1",
            pos=f"{0} {0} {0.015}",
            rgba="0.2 0.9 0.2 1",
        )
        self.add_site(
            outer_segment_2,
            name="outer_segment_1_2_site_2",
            pos=f"{0} {-0.03} {0.015}",
            rgba="0.2 0.9 0.2 1",
        )

    def _add_outer_segments_2(self):
        hx = self.OUTER_JOINT_SUPPORT_SIZE[0] / 2
        hy = self.OUTER_JOINT_SUPPORT_SIZE[1] / 2
        hz = self.OUTER_JOINT_SUPPORT_SIZE[2] / 2
        size = f"{hx} {hy} {hz}"
        pos = f"{0} {0} {0}"
        name = f"outer_segment_2_1"
        outer_segment_1 = add(self.spine, "body", name=name, pos=f"{0.015} {-hy} {0}")
        self.add_box(outer_segment_1, name, size, pos, rgba=self.color)

        hx = self.OUTER_SHAFT_SIZE[0] / 2
        hy = self.OUTER_SHAFT_SIZE[1] / 2
        hz = self.OUTER_SHAFT_SIZE[2] / 2
        size = f"{hx} {hy} {hz}"
        pos = f"{0} {-hy} {0}"
        name = f"outer_shaft_2_1"
        outer_shaft_1 = add(
            outer_segment_1,
            "body",
            name=name,
            pos=f"0 {-self.OUTER_JOINT_SUPPORT_SIZE[1] / 2} 0",
        )
        self.add_joint(outer_shaft_1, name, axis="0 0 1")
        self.add_box(outer_shaft_1, name, size, pos, rgba=self.color)

        hx = self.OUTER_SHAFT_SIZE[0] / 2
        hy = self.OUTER_SHAFT_SIZE[1] / 2
        hz = self.OUTER_SHAFT_SIZE[2] / 2
        size = f"{hx} {hy} {hz}"
        pos = f"{0} {-hy} {0}"
        name = f"outer_shaft_2_2"
        outer_shaft_2 = add(
            outer_shaft_1, "body", name=name, pos=f"0 {-self.OUTER_SHAFT_SIZE[1]} 0"
        )
        self.add_joint(outer_shaft_2, name, axis="0 0 1")
        self.add_box(outer_shaft_2, name, size, pos, rgba=self.color)

        hx = self.OUTER_JOINT_SUPPORT_SIZE[0] / 2
        hy = self.OUTER_JOINT_SUPPORT_SIZE[1] / 2
        hz = self.OUTER_JOINT_SUPPORT_SIZE[2] / 2
        size = f"{hx} {hy} {hz}"
        pos = f"{0} {-hy} {0}"
        name = f"outer_segment_2_2"
        outer_segment_2 = add(
            outer_shaft_2, "body", name=name, pos=f"{0} {-self.OUTER_SHAFT_SIZE[1]} {0}"
        )
        self.add_joint(outer_segment_2, name, axis="0 0 1")
        self.add_box(outer_segment_2, name, size, pos, rgba=self.color)
        self.add_site(
            outer_segment_2,
            name="outer_segment_2_2_site_1",
            pos=f"{0} {0} {0.015}",
            rgba="0.2 0.9 0.2 1",
        )
        self.add_site(
            outer_segment_2,
            name="outer_segment_2_2_site_2",
            pos=f"{0} {-0.03} {0.015}",
            rgba="0.2 0.9 0.2 1",
        )


def build_spine(parent, assets=None, overrides: Optional[Dict[str, Any]] = None):
    return SpineBuilder.build_spine(parent, assets=assets, overrides=overrides)
