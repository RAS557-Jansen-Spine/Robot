from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np

from model_builder import MujocoBuilderBase, add


class WedgeBuilder(MujocoBuilderBase):
    BODY_NAME = "hollow_wedge"
    BODY_POS = "0 0 0"
    COLOR = "0.8 0.3 0.3 1"
    FRONT_FACE_SIZE = [0.0558, 0.03, 0.001]
    BACK_FACE_SIZE = [0.0415, 0.03, 0.001]

    BACK_FACE_1_SIZE = [0.0657, 0.03, 0.001]
    FRONT_FACE_1_SIZE = [0.049, 0.03, 0.001]

    LINK_0_SIZE = [0.05, 0.015, 0.001]
    LINK_1_SIZE = [0.0393, 0.030, 0.001]
    LINK_2_SIZE = [0.0394, 0.030, 0.001]
    LINK_3_SIZE = [0.0618, 0.015, 0.001]

    def __init__(
        self,
        parent,
        assets,
        idx: int = 1,
        *,
        overrides: Optional[Dict[str, Any]] = None,
        include_links: bool = False,
        link_overrides: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        super().__init__(self.COLOR)
        self.parent = parent
        self.assets = assets
        self.idx = idx
        self.overrides = dict(overrides or {})
        self.body_pos = self.overrides.pop("pos", self.BODY_POS)
        self.include_links = include_links
        self.link_overrides = link_overrides or {}

        self.wedge = None
        self.wedge_2 = None

    def build(self):
        self._create_body()
        self._add_leg_shaft()
        self.add_wedge_1_geometry()
        self.add_links()

    @staticmethod
    def build_wedge(
        parent,
        assets,
        idx: int = 1,
        *,
        shape_variant: str = "angled",
        overrides: Optional[Dict[str, Any]] = None,
        joint_overrides: Optional[Dict[str, Any]] = None,
        shape_overrides: Optional[Dict[str, Dict[str, Any]]] = None,
        include_links: bool = False,
        link_overrides: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        builder = WedgeBuilder(
            parent,
            assets,
            idx,
            shape_variant=shape_variant,
            overrides=overrides,
            joint_overrides=joint_overrides,
            shape_overrides=shape_overrides,
            include_links=include_links,
            link_overrides=link_overrides,
        )
        return builder.build()

    def _create_body(self):
        body_name = f"{self.BODY_NAME}_{self.idx}"
        attrs = {"name": body_name, "pos": self.body_pos}
        attrs.update({k: str(v) for k, v in self.overrides.items()})
        self.wedge = add(self.parent, "body", **attrs)

    def _add_leg_shaft(self):
        joint_name = f"wedge_joint_{self.idx}"
        self.add_joint(self.wedge, joint_name)

    def add_wedge_1_geometry(self, parent=None):
        parent = parent or self.wedge
        # Euler angles as tuples for math, later stringified for MuJoCo
        front_face_euler = (0.0, 0.836, 0.0)
        front_face_hx = self.FRONT_FACE_SIZE[0] / 2
        front_face_hy = self.FRONT_FACE_SIZE[1] / 2
        front_face_hz = self.FRONT_FACE_SIZE[2] / 2
        front_face_posx = front_face_hx * np.cos(front_face_euler[1]) + 0.00268
        front_face_posz = front_face_hx * np.sin(front_face_euler[1])
        front_face_euler_str = " ".join(str(v) for v in front_face_euler)

        back_face_hx = self.BACK_FACE_SIZE[0] / 2
        back_face_hy = self.BACK_FACE_SIZE[1] / 2
        back_face_hz = self.BACK_FACE_SIZE[2] / 2
        back_face_euler = (0.0, 3.14159 - 1.506, 0.0)
        back_face_posx = back_face_hx * np.cos(back_face_euler[1]) + 0.00268
        back_face_posz = back_face_hx * np.sin(back_face_euler[1])
        self.back_face_pos_x = back_face_posx
        self.back_face_pos_z = back_face_posz
        back_face_euler_str = " ".join(str(v) for v in back_face_euler)

        left_face_pos = f"{0.0} {0.0} {0.0}"
        right_face_pos = f"{0.0} {0.03} {0.0}"

        front_name = f"wedge_front_{self.idx}"
        back_name = f"wedge_back_{self.idx}"
        left_name = f"wedge_left_{self.idx}"
        right_name = f"wedge_right_{self.idx}"

        self.add_box(
            parent,
            name=front_name,
            pos=f"{front_face_posx} {front_face_hy} {front_face_posz}",
            size=f"{front_face_hx} {front_face_hy} {front_face_hz}",
            rgba=self.color,
            euler=front_face_euler_str,
        )
        self.add_box(
            parent,
            name=back_name,
            pos=f"{back_face_posx} {back_face_hy} {back_face_posz}",
            size=f"{back_face_hx} {back_face_hy} {back_face_hz}",
            rgba=self.color,
            euler=back_face_euler_str,
        )
        self._add_triangular_face(
            left_name,
            pos=left_face_pos,
            corners=[(0.00, 0.0, 0.00), (0.00268, 0.0, 0.04141), (0.0401, 0.0, 0.0)],
            thickness=0.001,
            axis=(0, 1, 0),
            rgba=self.color,
            parent=parent,
        )
        self._add_triangular_face(
            right_name,
            pos=right_face_pos,
            corners=[(0.00, 0.0, 0.00), (0.00268, 0.0, 0.04141), (0.0401, 0.0, 0.0)],
            thickness=0.001,
            axis=(0, 1, 0),
            rgba=self.color,
            parent=parent,
        )

    def add_wedge_2_geometry(self, parent=None, *, name_prefix: str = ""):
        parent = parent or self.wedge_2
        # Euler angles as tuples for math, later stringified for MuJoCo
        front_face_euler = (0.0, 1.73 - 1.57, 0.0)
        front_face_hx = self.FRONT_FACE_1_SIZE[0] / 2
        front_face_hy = self.FRONT_FACE_1_SIZE[1] / 2
        front_face_hz = self.FRONT_FACE_1_SIZE[2] / 2
        front_face_posx = front_face_hx * np.cos(front_face_euler[1])
        front_face_posz = front_face_hx * np.sin(front_face_euler[1])
        front_face_euler_str = " ".join(str(v) for v in front_face_euler)

        back_face_hx = self.BACK_FACE_1_SIZE[0] / 2
        back_face_hy = self.BACK_FACE_1_SIZE[1] / 2
        back_face_hz = self.BACK_FACE_1_SIZE[2] / 2
        back_face_euler = (0.0, 1.57 - 0.828, 0.0)
        back_face_posx = back_face_hx * np.cos(back_face_euler[1])
        back_face_posz = back_face_hx * np.sin(back_face_euler[1])
        self.back_face_1_pos_x = back_face_posx
        self.back_face_1_pos_z = back_face_posz
        back_face_euler_str = " ".join(str(v) for v in back_face_euler)

        left_face_pos = f"{0.0} {0.0} {0.0}"
        right_face_pos = f"{0.0} {0.03} {0.0}"

        front_name = f"{name_prefix}wedge_front_{self.idx}"
        back_name = f"{name_prefix}wedge_back_{self.idx}"
        left_name = f"{name_prefix}wedge_left_{self.idx}"
        right_name = f"{name_prefix}wedge_right_{self.idx}"

        self.add_box(
            parent,
            name=front_name,
            pos=f"{-front_face_posx} {front_face_hy} {front_face_posz}",
            size=f"{front_face_hx} {front_face_hy} {front_face_hz}",
            rgba=self.color,
            euler=front_face_euler_str,
        )
        self.add_box(
            parent,
            name=back_name,
            pos=f"{-back_face_posx} {back_face_hy} {-0.0367 + back_face_posz}",
            size=f"{back_face_hx} {back_face_hy} {back_face_hz}",
            rgba=self.color,
            euler=back_face_euler_str,
        )
        self._add_triangular_face(
            left_name,
            pos=left_face_pos,
            corners=[(0.00, 0.0, 0.00), (0.0, 0.0, -0.0367), (-0.0484, 0.0, 0.0078)],
            thickness=0.001,
            axis=(0, 1, 0),
            rgba=self.color,
            parent=parent,
        )
        self._add_triangular_face(
            right_name,
            pos=right_face_pos,
            corners=[(0.00, 0.0, 0.00), (0.0, 0.0, -0.0367), (-0.0484, 0.0, 0.0078)],
            thickness=0.001,
            axis=(0, 1, 0),
            rgba=self.color,
            parent=parent,
        )

    def add_links(self):
        link_0_hx = self.LINK_0_SIZE[0] / 2
        link_0_hy = self.LINK_0_SIZE[1] / 2
        link_0_hz = self.LINK_0_SIZE[2] / 2

        link_1_hx = self.LINK_1_SIZE[0] / 2
        link_1_hy = self.LINK_1_SIZE[1] / 2
        link_1_hz = self.LINK_1_SIZE[2] / 2

        link_2_hx = self.LINK_2_SIZE[0] / 2
        link_2_hy = self.LINK_2_SIZE[1] / 2
        link_2_hz = self.LINK_2_SIZE[2] / 2

        link_3_hx = self.LINK_3_SIZE[0] / 2
        link_3_hy = self.LINK_3_SIZE[1] / 2
        link_3_hz = self.LINK_3_SIZE[2] / 2

        pos = f"{0.00268} {link_0_hy} {0.04141}"
        link_0_body = add(self.wedge, "body", name=f"link_0_{self.idx}", pos=pos)
        self.add_joint(link_0_body, f"link_0_joint_{self.idx}")
        self.add_box(
            link_0_body,
            name=f"link_0_{self.idx}",
            pos=f"{-link_0_hx} {0} {0}",
            size=f"{link_0_hx} {link_0_hy} {link_0_hz}",
            rgba=self.color,
        )
        self.add_site(
            link_0_body,
            f"link_0_site_{self.idx}",
            f"{-self.LINK_0_SIZE[0] - 0.001} {0} {0}",
            rgba="0.2 0.9 0.2 1",
        )

        pos = f"{0.0} {link_1_hy} {0.0}"
        link_1_body = add(self.wedge, "body", name=f"link_1_{self.idx}", pos=pos)
        self.add_joint(link_1_body, f"link_1_joint_{self.idx}")
        self.add_box(
            link_1_body,
            name=f"link_1_{self.idx}",
            pos=f"{-link_1_hx} {0} {0}",
            size=f"{link_1_hx} {link_1_hy} {link_1_hz}",
            rgba=self.color,
        )
        # Optionally nest another wedge geometry as a child of link_1
        self.wedge_2 = add(
            link_1_body,
            "body",
            name=f"link_1_child_{self.idx}",
            pos=f"{-0.0393} {-link_1_hy} 0",
        )
        self.add_joint(self.wedge_2, f"link_1_child_joint_{self.idx}")
        self.add_wedge_2_geometry(
            parent=self.wedge_2, name_prefix=f"link_1_child_{self.idx}_"
        )
        self.add_site(
            self.wedge_2,
            name=f"wedge_site_1_{self.idx}",
            pos=f"{0} {0.015} {-0.0367}",
            rgba="0.2 0.9 0.2 1",
        )

        pos = f"{0.0401} {link_2_hy} {0.0}"
        link_2_body = add(self.wedge, "body", name=f"link_2_{self.idx}", pos=pos)
        self.add_joint(link_2_body, f"link_2_joint_{self.idx}")
        self.add_box(
            link_2_body,
            name=f"link_2_{self.idx}",
            pos=f"{-link_2_hx} {0} {0}",
            size=f"{link_2_hx} {link_2_hy} {link_2_hz}",
            rgba=self.color,
        )
        self.add_site(
            link_2_body,
            f"link_2_site_{self.idx}",
            f"{-self.LINK_2_SIZE[0] - 0.001} {0} {0}",
            rgba="0.2 0.9 0.2 1",
        )

        pos = f"{0.0} {link_3_hy} {0.0}"
        link_3_body = add(self.wedge_2, "body", name=f"link_3_{self.idx}", pos=pos)
        self.add_joint(link_3_body, f"link_3_joint_{self.idx}")
        self.add_box(
            link_3_body,
            name=f"link_3_{self.idx}",
            pos=f"{link_3_hx} {link_3_hy * 2} {0}",
            size=f"{link_3_hx} {link_3_hy} {link_3_hz}",
            rgba=self.color,
        )
        self.add_site(
            link_3_body,
            f"link_3_site_{self.idx}",
            f"{0.0619} {link_3_hy * 2} {0}",
            rgba="0.2 0.9 0.2 1",
        )

    def _build_geom_attrs(
        self, base_name: str, geom_def: Dict[str, Any]
    ) -> Dict[str, Any]:
        geom_name = base_name if self.idx == 1 else f"{base_name}_{self.idx}"
        attrs = {
            "name": geom_name,
            "type": geom_def.get("type", "box"),
            "rgba": geom_def.get("rgba", self.color),
        }
        for key, value in geom_def.items():
            if key in ("type", "rgba", "enabled"):
                continue
            attrs[key] = self._format_attr_value(value)
        return attrs

    def _add_triangular_face(
        self,
        geom_name: str,
        pos: Any,
        corners: Any,
        thickness: Any,
        axis: Any,
        rgba: Optional[str] = None,
        euler: Any = None,
        parent=None,
    ):
        origin = self._ensure_vec3(pos)
        points = self._normalize_corners(corners)
        thickness_val = float(thickness or 0.0)
        axis_val = self._ensure_vec3(axis)
        half = thickness_val / 2.0

        vertices: List[float] = []
        for corner in points:
            px = origin[0] + corner[0] - half * axis_val[0]
            py = origin[1] + corner[1] - half * axis_val[1]
            pz = origin[2] + corner[2] - half * axis_val[2]
            vertices.extend([px, py, pz])
        for corner in points:
            px = origin[0] + corner[0] + half * axis_val[0]
            py = origin[1] + corner[1] + half * axis_val[1]
            pz = origin[2] + corner[2] + half * axis_val[2]
            vertices.extend([px, py, pz])

        vertex_str = " ".join(str(coord) for coord in vertices)

        # Register dynamic mesh
        mesh_name = f"{geom_name}_mesh"
        if self.assets is not None:
            add(self.assets, "mesh", name=mesh_name, vertex=vertex_str)

        euler_str = self._format_attr_value(euler) if euler is not None else None
        self.add_triangular_face(
            parent or self.wedge, geom_name, mesh_name, rgba, euler_str
        )

    @staticmethod
    def _format_attr_value(value: Any) -> str:
        if isinstance(value, (tuple, list)):
            return " ".join(str(v) for v in value)
        return str(value)

    @staticmethod
    def _ensure_vec3(value: Any) -> Tuple[float, float, float]:
        if value is None:
            return 0.0, 0.0, 0.0
        if isinstance(value, str):
            parts = [float(v) for v in value.split()]
        elif isinstance(value, Iterable):
            parts = [float(v) for v in value]
        else:
            raise ValueError(f"Unsupported vector value: {value!r}")
        if len(parts) == 2:
            parts.append(0.0)
        if len(parts) != 3:
            raise ValueError(f"Expected 2 or 3 coordinates, got {parts}")
        return parts[0], parts[1], parts[2]

    @staticmethod
    def _normalize_corners(corners: Any) -> List[Tuple[float, float, float]]:
        if corners is None:
            raise ValueError("Triangular face requires 'corners'")
        points: List[Tuple[float, float, float]] = []
        if isinstance(corners, str):
            values = [float(v) for v in corners.split()]
            if len(values) % 2 != 0 and len(values) % 3 != 0:
                raise ValueError("Corner string must have 2 or 3 values per vertex")
            step = 2 if len(values) % 3 != 0 else 3
            for idx in range(0, len(values), step):
                chunk = values[idx : idx + step]
                if len(chunk) == 2:
                    chunk.append(0.0)
                points.append((chunk[0], chunk[1], chunk[2]))
        elif isinstance(corners, Iterable):
            for item in corners:
                if isinstance(item, str):
                    coords = [float(v) for v in item.split()]
                elif isinstance(item, Iterable):
                    coords = [float(v) for v in item]
                else:
                    raise ValueError(f"Unsupported corner value: {item!r}")
                if len(coords) == 2:
                    coords.append(0.0)
                if len(coords) != 3:
                    raise ValueError(f"Corner must have 2 or 3 values, got {coords}")
                points.append((coords[0], coords[1], coords[2]))
        else:
            raise ValueError(f"Unsupported corners value: {corners!r}")

        if len(points) != 3:
            raise ValueError(f"Exactly 3 corners required, got {len(points)}")
        return points

    @staticmethod
    def _merge_dicts(
        base: Dict[str, Any], overrides: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        merged = deepcopy(base)
        if overrides:
            for key, value in overrides.items():
                merged[key] = value
        return merged

    @staticmethod
    def _merge_shape_profile(
        base_profile: Dict[str, Dict[str, Any]],
        overrides: Optional[Dict[str, Dict[str, Any]]],
    ) -> Dict[str, Dict[str, Any]]:
        profile = deepcopy(base_profile)
        if not overrides:
            return profile
        for geom_name, geom_overrides in overrides.items():
            if not geom_overrides:
                continue
            geom = profile.setdefault(geom_name, {})
            geom.update(geom_overrides)
        return profile


def build_wedges(
    chassis,
    assets=None,
    overrides: Optional[Dict[str, Any]] = None,
    *,
    idx: int = 1,
    include_links: bool = False,
    link_overrides: Optional[Dict[str, Dict[str, Any]]] = None,
):
    builder = WedgeBuilder(
        chassis,
        assets,
        idx,
        overrides=overrides,
        include_links=include_links,
        link_overrides=link_overrides,
    )
    return builder.build()
