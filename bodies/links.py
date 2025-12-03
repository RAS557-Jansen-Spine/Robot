from typing import Any, Dict

from model_builder import build_tree, with_overrides

LINK_0_SPEC: Dict[str, Any] = {
    "tag": "body",
    "attrib": {"name": "link_0", "pos": "0.0401 0.015 0", "axisangle": "0 1 0 1.57"},
    "children": [
        {
            "tag": "joint",
            "attrib": {
                "name": "joint_0",
                "type": "hinge",
                "axis": "0 1 0",
                "range": "-180 180",
                "limited": "true",
            },
        },
        {
            "tag": "geom",
            "attrib": {
                "name": "link_0_geom",
                "type": "box",
                "size": "0.0197 0.015 0.0005",
                "pos": "0.0197 0 0",
                "rgba": "0.3 0.3 0.8 1",
            },
        },
    ],
}

LINK_3_SPEC: Dict[str, Any] = {
    "tag": "body",
    "attrib": {"name": "link_3", "pos": "0.03875 0.0075 0.0414"},
    "children": [
        {
            "tag": "joint",
            "attrib": {
                "name": "joint_4",
                "type": "hinge",
                "axis": "0 1 0",
                "range": "-180 180",
                "limited": "true",
            },
        },
        {
            "tag": "geom",
            "attrib": {
                "name": "link_3_geom",
                "type": "box",
                "size": "0.025 0.0075 0.0005",
                "pos": "0.025 0 0",
                "rgba": "0.3 0.3 0.8 1",
            },
        },
    ],
}

LINK_5_SPEC: Dict[str, Any] = {
    "tag": "body",
    "attrib": {"name": "link_5", "pos": "0.02482 0 0.02703"},
    "children": [
        {
            "tag": "joint",
            "attrib": {
                "name": "joint_5",
                "type": "hinge",
                "axis": "0 1 0",
                "range": "-180 180",
                "limited": "true",
            },
        },
        {
            "tag": "geom",
            "attrib": {
                "name": "link_5_geom",
                "type": "box",
                "size": "0.03095 0.0075 0.0005",
                "pos": "0.03095 0.0075 0",
                "rgba": "0.3 0.3 0.8 1",
            },
        },
    ],
}

LINK_2_SPEC: Dict[str, Any] = {
    "tag": "body",
    "attrib": {
        "name": "link_2",
        "pos": "0.02482 0 0.02703",
        "axisangle": "0 1 0 -1.57",
    },
    "children": [
        {
            "tag": "joint",
            "attrib": {
                "name": "joint_3",
                "type": "hinge",
                "axis": "0 1 0",
                "range": "-180 180",
                "limited": "true",
            },
        },
        {
            "tag": "geom",
            "attrib": {
                "name": "link_2_geom",
                "type": "box",
                "size": "0.001 0.015 0.0005",
                "pos": "0 0 0",
                "rgba": "0.3 0.3 0.8 1",
            },
        },
    ],
}

WEDGE_2_SPEC: Dict[str, Any] = {
    "tag": "body",
    "attrib": {"name": "hollow_wedge_2", "pos": "0.0394 0 0"},
    "children": [
        {
            "tag": "joint",
            "attrib": {
                "name": "joint_2",
                "type": "hinge",
                "axis": "0 1 0",
                "range": "-180 180",
                "limited": "true",
            },
        },
        {
            "tag": "geom",
            "attrib": {
                "name": "rect_left_2",
                "type": "box",
                "size": "0.03285 0.015 0.0005",
                "pos": "0.03285 0 0",
                "euler": "0 0 0",
                "rgba": "0.8 0.3 0.3 1",
            },
        },
        {
            "tag": "geom",
            "attrib": {
                "name": "rect_right_2",
                "type": "box",
                "size": "0.0245 0.015 0.0005",
                "pos": "0.0452 0 0.0135",
                "euler": "0 0.584 0",
                "rgba": "0.8 0.3 0.3 1",
            },
        },
        {
            "tag": "geom",
            "attrib": {
                "name": "tri_front_2",
                "type": "mesh",
                "mesh": "tri_face_2",
                "pos": "0 0.015 0",
                "euler": "1.57 0 0",
                "rgba": "0.8 0.3 0.3 1",
            },
        },
        {
            "tag": "geom",
            "attrib": {
                "name": "tri_back_2",
                "type": "mesh",
                "mesh": "tri_face_2",
                "pos": "0 -0.015 0",
                "euler": "1.57 0 0",
                "rgba": "0.8 0.3 0.3 1",
            },
        },
        LINK_5_SPEC,
        LINK_2_SPEC,
    ],
}

LINK_1_SPEC: Dict[str, Any] = {
    "tag": "body",
    "attrib": {"name": "link_1", "pos": "0 0.015 0", "axisangle": "0 1 0 1.57"},
    "children": [
        {
            "tag": "joint",
            "attrib": {
                "name": "joint_1",
                "type": "hinge",
                "axis": "0 1 0",
                "range": "-180 180",
                "limited": "true",
            },
        },
        {
            "tag": "geom",
            "attrib": {
                "name": "link_1_geom",
                "type": "box",
                "size": "0.0197 0.015 0.0005",
                "pos": "0.0197 0 0",
                "density": "10",
                "rgba": "0.3 0.3 0.8 1",
            },
        },
        WEDGE_2_SPEC,
    ],
}

LINK_SPECS = (LINK_0_SPEC, LINK_3_SPEC, LINK_1_SPEC)


def build_links(wedge_body, overrides: Dict[str, Dict[str, Any]] = None):
    overrides = overrides or {}
    built = {}
    for spec in LINK_SPECS:
        name = spec["attrib"]["name"]
        spec_with_override = with_overrides(spec, overrides.get(name))
        built[name] = build_tree(wedge_body, spec_with_override)
    return built
