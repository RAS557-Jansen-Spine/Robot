from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import ezdxf
from ezdxf.entities import LWPolyline
from ezdxf.math import ConstructionArc, Vec2, bulge_to_arc

CoordList = List[Tuple[float, float]]
CircleSpec = Tuple[Tuple[float, float], float]

__all__ = [
    "read_lines",
    "read_lwpolylines",
    "read_circles",
    "extract_geometry",
    "write_new_dxf",
]


def _matches(entity, *, layer: str | None, color: int | None) -> bool:
    if layer is not None and entity.dxf.layer != layer:
        return False
    if color is not None and entity.get_dxf_attrib("color", None) != color:
        return False
    return True


def read_lines(filename: str | Path, *, layer: str | None = None, color: int | None = None) -> List[List[Tuple[float, float]]]:
    """Load ``LINE`` segments from a DXF file."""
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    lines: List[List[Tuple[float, float]]] = []
    for entity in msp.query("LINE"):  # type: ignore[no-untyped-call]
        if not _matches(entity, layer=layer, color=color):
            continue
        start = entity.dxf.start
        end = entity.dxf.end
        lines.append([(float(start[0]), float(start[1])), (float(end[0]), float(end[1]))])
    return lines


def _bulge_segment_points(start: Vec2, end: Vec2, bulge: float, arc_approx: int) -> List[Vec2]:
    """Return the tessellated vertices for an LWPolyline segment."""
    if abs(bulge) < 1e-12:
        return [start, end]
    arc_approx = max(int(arc_approx), 1)
    center, start_ang, end_ang, radius = bulge_to_arc(start, end, bulge)
    arc = ConstructionArc(
        center=center,
        radius=radius,
        start_angle=math.degrees(start_ang),
        end_angle=math.degrees(end_ang),
    )
    # +1 to include both endpoints
    angles = list(arc.angles(arc_approx + 1))
    return list(arc.vertices(angles))


def _lwpolyline_vertices(entity: LWPolyline, arc_approx: int) -> CoordList:
    """Approximate an ``LWPolyline`` as a list of 2D vertices."""
    data = list(entity.get_points("xyb"))
    if not data:
        return []

    count = len(data)
    coords: CoordList = []

    # If the polyline is open, the bulge of the last vertex is ignored and we
    # stop at the penultimate vertex.
    limit = count if entity.closed else count - 1
    for idx in range(max(limit, 0)):
        x, y, bulge = data[idx]
        start = Vec2(x, y)
        end_x, end_y, _ = data[(idx + 1) % count]
        end = Vec2(end_x, end_y)
        tess = _bulge_segment_points(start, end, bulge, arc_approx)
        coords.extend((pt.x, pt.y) for pt in tess[:-1])  # omit duplicated end

    last_x, last_y, _ = data[0 if entity.closed else -1]
    coords.append((float(last_x), float(last_y)))
    return coords


def read_lwpolylines(
    filename: str | Path,
    *,
    layer: str | None = None,
    color: int | None = None,
    arc_approx: int = 12,
) -> List[CoordList]:
    """Load ``LWPOLYLINE`` vertices as tessellated XY coordinate lists."""
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    polygons: List[CoordList] = []
    for entity in msp.query("LWPOLYLINE"):  # type: ignore[no-untyped-call]
        if not _matches(entity, layer=layer, color=color):
            continue
        polygons.append(_lwpolyline_vertices(entity, arc_approx))
    return polygons


def read_circles(
    filename: str | Path,
    *,
    layer: str | None = None,
    color: int | None = None,
) -> List[CircleSpec]:
    """Load ``CIRCLE`` entities as ``((x, y), radius)`` tuples."""
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    circles: List[CircleSpec] = []
    for entity in msp.query("CIRCLE"):  # type: ignore[no-untyped-call]
        if not _matches(entity, layer=layer, color=color):
            continue
        center = entity.dxf.center
        radius = entity.dxf.radius
        circles.append(((float(center.x), float(center.y)), float(radius)))
    return circles


def extract_geometry(
    dxf_path: str | Path,
    *,
    body_layer: str = "body",
    hole_layer: str = "holes",
    arc_approx: int = 12,
) -> Tuple[List[CoordList], List[CoordList], List[CircleSpec]]:
    """Convenience wrapper that returns body polygons, slot polygons, circles."""
    body_polys = read_lwpolylines(dxf_path, layer=body_layer, arc_approx=arc_approx)
    hole_slots = read_lwpolylines(dxf_path, layer=hole_layer, arc_approx=arc_approx)
    hole_circles = read_circles(dxf_path, layer=hole_layer)
    return body_polys, hole_slots, hole_circles


def write_new_dxf(
    output_path: str | Path,
    *,
    body_polys: Iterable[Sequence[Tuple[float, float]]] = (),
    slot_polys: Iterable[Sequence[Tuple[float, float]]] = (),
    circles: Iterable[CircleSpec] = (),
    body_layer: str = "body",
    hole_layer: str = "holes",
) -> None:
    """Write a new DXF containing the provided geometry."""
    doc = ezdxf.new("R2010")
    doc.layers.new(body_layer, dxfattribs={"color": 3})
    doc.layers.new(hole_layer, dxfattribs={"color": 1})
    msp = doc.modelspace()

    for coords in body_polys:
        msp.add_lwpolyline(coords, format="xy", close=True, dxfattribs={"layer": body_layer})
    for coords in slot_polys:
        msp.add_lwpolyline(coords, format="xy", close=True, dxfattribs={"layer": hole_layer})
    for (cx, cy), radius in circles:
        msp.add_circle((cx, cy), radius, dxfattribs={"layer": hole_layer})

    doc.saveas(output_path)
