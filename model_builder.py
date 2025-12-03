from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

# ==========================================
# XML Utils
# ==========================================

ElementSpec = Dict[str, Any]


def _clean_attrs(attrs: Dict[str, Any]) -> Dict[str, str]:
    """Convert values to strings and drop Nones so tags stay compact."""
    return {k: str(v) for k, v in attrs.items() if v is not None}


def add(parent, tag: str, **attrs):
    """Create a child element with sanitized attributes."""
    return SubElement(parent, tag, _clean_attrs(attrs))


def build_tree(parent, spec: ElementSpec):
    """Recursively build an XML subtree from a spec dictionary."""
    tag = spec["tag"]
    attrib = _clean_attrs(spec.get("attrib", {}))
    children: Iterable[ElementSpec] = spec.get("children", []) or []

    elem = SubElement(parent, tag, attrib)
    for child in children:
        build_tree(elem, child)
    return elem


def with_overrides(
    spec: ElementSpec, attrib_overrides: Optional[Dict[str, Any]] = None
) -> ElementSpec:
    """Return a deep-copied spec with optional attribute overrides on the root node."""
    copied = deepcopy(spec)
    if attrib_overrides:
        copied.setdefault("attrib", {}).update(_clean_attrs(attrib_overrides))
    return copied


def prettify(elem: Element) -> str:
    rough = tostring(elem)
    return minidom.parseString(rough).toprettyxml(indent="  ")


# ==========================================
# Mujoco Builder Base
# ==========================================


class MujocoBuilderBase:
    def __init__(self, color: str = None):
        self.color = color or "0.8 0.8 0.8 1"
        self._last_parent = None

    def set_parent(self, parent):
        self._last_parent = parent
        return parent

    def add_box(
        self,
        parent,
        name: str,
        size: str,
        pos: str,
        mass: str = None,
        rgba: str = None,
        euler: str = None,
    ):
        attrs: Dict[str, Any] = {
            "name": name,
            "type": "box",
            "size": size,
            "pos": pos,
            "rgba": rgba or self.color,
        }
        if mass:
            attrs["mass"] = mass
        if euler:
            attrs["euler"] = euler
        add(parent, "geom", **attrs)

    def add_cylinder(
        self,
        parent,
        name: str,
        size: str,
        pos: str,
        mass: str = None,
        rgba: str = None,
        euler: str = None,
    ):
        attrs: Dict[str, Any] = {
            "name": name,
            "type": "cylinder",
            "size": size,
            "pos": pos,
            "rgba": rgba or self.color,
        }
        if mass:
            attrs["mass"] = mass
        if euler:
            attrs["euler"] = euler
        add(parent, "geom", **attrs)

    def add_triangular_face(
        self,
        parent,
        name: str,
        vertex: str,
        rgba: str = None,
        euler: str = None,
        pos: str = None,
    ):
        attrs: Dict[str, Any] = {
            "name": name,
            "type": "mesh",
            "mesh": vertex,
            "rgba": rgba or self.color,
        }
        if euler:
            attrs["euler"] = euler
        if pos:
            attrs["pos"] = pos
        add(parent, "geom", **attrs)

    def add_joint(
        self,
        parent,
        joint_name: str = "motor_joint",
        axis: str = "0 1 0",
        limited: bool = False,
    ):
        add(
            parent,
            "joint",
            name=joint_name,
            type="hinge",
            axis=axis,
            limited="true" if limited else "false",
        )

    def _offset_vector(self, vec, dx=0.0, dy=0.0, dz=0.0):
        return [vec[0] + dx, vec[1] + dy, vec[2] + dz]

    @staticmethod
    def _format_pos(vec):
        return f"{vec[0]} {vec[1]} {vec[2]}"

    def add_site(
        self,
        parent,
        name: str,
        pos: str,
        size: str = "0.001",
        type_: str = "sphere",
        rgba: str = None,
    ):
        attrs: Dict[str, Any] = {
            "name": name,
            "type": type_,
            "pos": pos,
            "size": size,
            "rgba": rgba or self.color,
        }
        add(parent, "site", **attrs)


# ==========================================
# Assets
# ==========================================

AssetSpec = Tuple[str, Dict[str, Any]]

BASE_ASSETS: Iterable[AssetSpec] = (
    (
        "texture",
        {
            "name": "grid",
            "type": "2d",
            "builtin": "checker",
            "width": "512",
            "height": "512",
            "rgb1": "0.95 0.95 0.95",
            "rgb2": "1 1 1",
        },
    ),
    (
        "material",
        {
            "name": "floor_mat",
            "texture": "grid",
            "texrepeat": "50 50",
            "specular": "0.0",
        },
    ),
)


def build_assets(mujoco_root, extra_assets: Iterable[AssetSpec] = ()):
    asset = add(mujoco_root, "asset")
    for tag, attrs in tuple(BASE_ASSETS) + tuple(extra_assets):
        add(asset, tag, **attrs)
    return asset


# ==========================================
# Actuators
# ==========================================

BASE_ACTUATORS: Iterable[Dict[str, Any]] = ()


def velocity_actuator(
    joint: str,
    *,
    name: Optional[str] = None,
    kv: float = 5.0,
    ctrlrange: str = "-20 20",
) -> Dict[str, Any]:
    """Helper to define a velocity actuator spec for a given hinge joint."""
    return {
        "type": "velocity",
        "name": name or f"{joint}_vel",
        "joint": joint,
        "kv": str(kv),
        "ctrlrange": ctrlrange,
    }


def build_actuators(mujoco_root, actuators: Iterable[Dict[str, Any]] = ()):
    actuator_section = add(mujoco_root, "actuator")
    for act in tuple(BASE_ACTUATORS) + tuple(actuators):
        act = dict(act)  # shallow copy so we can pop type safely
        act_type = act.pop("type", "general")
        add(actuator_section, act_type, **act)
    return actuator_section


# ==========================================
# Constraints
# ==========================================

CONNECT_SPECS: Iterable[Dict[str, Any]] = (
    {
        "name": "connect1",
        "active": "true",
        "site1": "motor_shaft_site_1",
        "site2": "link_0_site_1",
    },
    {
        "name": "connect2",
        "active": "true",
        "site1": "motor_shaft_site_2",
        "site2": "link_0_site_2",
    },
    {
        "name": "connect3",
        "active": "true",
        "site1": "link_2_site_1",
        "site2": "wedge_site_1_1",
    },
    {
        "name": "connect4",
        "active": "true",
        "site1": "link_2_site_2",
        "site2": "wedge_site_1_2",
    },
    {
        "name": "connect5",
        "active": "true",
        "site1": "link_3_site_1",
        "site2": "motor_shaft_ext_site_1",
    },
    {
        "name": "connect6",
        "active": "true",
        "site1": "link_3_site_2",
        "site2": "motor_shaft_ext_site_2",
    },
    {
        "name": "connect7",
        "active": "true",
        "site1": "motor_shaft_site_3",
        "site2": "link_0_site_3",
    },
    {
        "name": "connect8",
        "active": "true",
        "site1": "motor_shaft_site_4",
        "site2": "link_0_site_4",
    },
    {
        "name": "connect9",
        "active": "true",
        "site1": "link_2_site_3",
        "site2": "wedge_site_1_3",
    },
    {
        "name": "connect10",
        "active": "true",
        "site1": "link_2_site_4",
        "site2": "wedge_site_1_4",
    },
    {
        "name": "connect11",
        "active": "true",
        "site1": "link_3_site_3",
        "site2": "motor_shaft_ext_site_3",
    },
    {
        "name": "connect12",
        "active": "true",
        "site1": "link_3_site_4",
        "site2": "motor_shaft_ext_site_4",
    },
    {
        "name": "connect13",
        "active": "true",
        "site1": "inner_segment_2_site_2",
        "site2": "outer_segment_1_2_site_1",
    },
    {
        "name": "connect14",
        "active": "true",
        "site1": "inner_segment_2_site_1",
        "site2": "outer_segment_1_2_site_2",
    },
    {
        "name": "connect15",
        "active": "true",
        "site1": "inner_segment_2_site_4",
        "site2": "outer_segment_2_2_site_1",
    },
    {
        "name": "connect16",
        "active": "true",
        "site1": "inner_segment_2_site_3",
        "site2": "outer_segment_2_2_site_2",
    },
)


def build_constraints(mujoco_root):
    eq = add(mujoco_root, "equality")
    for connect in tuple(CONNECT_SPECS):
        add(eq, "connect", **connect)
    return eq


def build_connection(
    mujoco_root,
    body1: str,
    body2: str,
    *,
    name: Optional[str] = None,
    relpose: str = "0 0 0 1 0 0 0",
    anchor: str = "0 0 0",
    active: str = "true",
):
    """Create a weld-style constraint between two bodies."""
    eq = mujoco_root.find("equality")
    if eq is None:
        eq = add(mujoco_root, "equality")

    weld_name = name or f"{body1}_to_{body2}_weld"
    return add(
        eq,
        "weld",
        name=weld_name,
        active=active,
        body1=body1,
        body2=body2,
        relpose=relpose,
        anchor=anchor,
    )


def build_connect(
    mujoco_root,
    body1: str,
    body2: str,
    *,
    name: Optional[str] = None,
    site1: Optional[str] = None,
    site2: Optional[str] = None,
    anchor: Optional[str] = "0 0 0",
    active: str = "true",
):
    """Create a positional connection (like a ball joint) between two sibling bodies."""
    eq = mujoco_root.find("equality")
    if eq is None:
        eq = add(mujoco_root, "equality")

    connect_name = name or f"{body1}_to_{body2}_connect"
    if (site1 is None) != (site2 is None):
        raise ValueError("site1 and site2 must both be provided or both omitted")

    attrs: Dict[str, Any] = {"name": connect_name, "active": active}
    if site1 and site2:
        attrs.update({"site1": site1, "site2": site2})
    else:
        attrs.update({"body1": body1, "body2": body2})
        if anchor is not None:
            attrs["anchor"] = anchor

    return add(eq, "connect", **attrs)


# ==========================================
# Model Generator
# ==========================================


def build_root(model_name: str = "Model") -> Element:
    mujoco = Element("mujoco", {"model": model_name})
    add(mujoco, "compiler", inertiafromgeom="true", angle="radian")
    add(mujoco, "option", timestep="0.001", gravity="0 0 -9.81", integrator="RK4")
    default = add(mujoco, "default")
    add(default, "joint", damping="0.1", armature="0.01")
    add(default, "geom", density="1000", friction="0.5 0.1 0.1")
    return mujoco


def build_model(model_name: str = "Model") -> Element:
    # Import here to avoid circular dependency if bodies import model_builder
    from bodies.chassis import ChassisBuilder

    mujoco = build_root(model_name)
    assets = build_assets(mujoco)

    worldbody = add(mujoco, "worldbody")
    ChassisBuilder.build_chassis(
        worldbody,
        assets=assets,
        include_motor=True,
        include_wedges=True,
        include_spine=True,
    )

    build_constraints(mujoco)
    build_actuators(
        mujoco,
        actuators=(
            velocity_actuator("motor_joint_1"),
            velocity_actuator("motor_joint_2"),
            velocity_actuator("motor_joint_3"),
            velocity_actuator("motor_joint_4"),
        ),
    )
    return mujoco
