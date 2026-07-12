"""High-level framework for building friendly G-code workflows.

This module intentionally keeps the established :mod:`fullcontrol` package as the
core toolpath/G-code engine and adds a smaller, stable API that a UI can call.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sin
from typing import Callable, Literal

import fullcontrol as fc
from pydantic import BaseModel, Field

TemplateName = Literal["line", "rectangle", "grid", "spiral"]


class TemplateOption(BaseModel):
    """Metadata used by frontends to render friendly design choices."""

    id: TemplateName
    label: str
    description: str


class DesignSpec(BaseModel):
    """User-facing design parameters shared by the API, CLI, and frontend."""

    template: TemplateName = "rectangle"
    width: float = Field(40, ge=1, le=300, description="X dimension in millimetres")
    depth: float = Field(30, ge=1, le=300, description="Y dimension in millimetres")
    height: float = Field(0.2, ge=0, le=300, description="Z height in millimetres")
    spacing: float = Field(5, ge=0.1, le=100, description="Spacing for grid or spiral paths")
    feedrate: int = Field(1200, ge=60, le=12000, description="Print move speed in mm/min")
    travel_feedrate: int = Field(6000, ge=60, le=20000, description="Travel move speed in mm/min")
    printer_name: str = Field("generic", min_length=1, description="FullControl printer profile")


class BuildResult(BaseModel):
    """G-code output plus simple summary data for UI status panels."""

    spec: DesignSpec
    gcode: str
    point_count: int
    estimated_bounds: dict[str, float]


@dataclass(frozen=True)
class _Template:
    label: str
    description: str
    builder: Callable[[DesignSpec], list[fc.Point]]


def list_templates() -> list[TemplateOption]:
    """Return templates available to a frontend without exposing internals."""

    return [
        TemplateOption(id=name, label=template.label, description=template.description)
        for name, template in _TEMPLATES.items()
    ]


def build_design(spec: DesignSpec) -> list[object]:
    """Build FullControl steps from a validated, frontend-friendly spec."""

    if spec.spacing > max(spec.width, spec.depth):
        raise ValueError("spacing must be no larger than the design dimensions")
    points = _TEMPLATES[spec.template].builder(spec)
    return [
        fc.Printer(print_speed=spec.feedrate, travel_speed=spec.travel_feedrate),
        fc.Extruder(on=False),
        points[0],
        fc.Extruder(on=True),
        *points[1:],
        fc.Extruder(on=False),
    ]


def generate_gcode(spec: DesignSpec) -> BuildResult:
    """Generate G-code with the FullControl core and return UI-ready metadata."""

    steps = build_design(spec)
    gcode = fc.transform(
        steps,
        "gcode",
        fc.GcodeControls(printer_name=spec.printer_name),
        show_tips=False,
    )
    points = [step for step in steps if isinstance(step, fc.Point)]
    return BuildResult(
        spec=spec,
        gcode=gcode,
        point_count=len(points),
        estimated_bounds={
            "min_x": min(point.x for point in points),
            "max_x": max(point.x for point in points),
            "min_y": min(point.y for point in points),
            "max_y": max(point.y for point in points),
            "min_z": min(point.z for point in points),
            "max_z": max(point.z for point in points),
        },
    )


def _line(spec: DesignSpec) -> list[fc.Point]:
    return [fc.Point(x=0, y=0, z=spec.height), fc.Point(x=spec.width, y=0, z=spec.height)]


def _rectangle(spec: DesignSpec) -> list[fc.Point]:
    return [
        fc.Point(x=0, y=0, z=spec.height),
        fc.Point(x=spec.width, y=0, z=spec.height),
        fc.Point(x=spec.width, y=spec.depth, z=spec.height),
        fc.Point(x=0, y=spec.depth, z=spec.height),
        fc.Point(x=0, y=0, z=spec.height),
    ]


def _grid(spec: DesignSpec) -> list[fc.Point]:
    points: list[fc.Point] = [fc.Point(x=0, y=0, z=spec.height)]
    rows = max(1, int(spec.depth / spec.spacing))
    for row in range(rows + 1):
        y = min(row * spec.spacing, spec.depth)
        x_values = (0, spec.width) if row % 2 == 0 else (spec.width, 0)
        points.extend(fc.Point(x=x, y=y, z=spec.height) for x in x_values)
    return _dedupe_adjacent(points)


def _spiral(spec: DesignSpec) -> list[fc.Point]:
    turns = max(1, int(min(spec.width, spec.depth) / (2 * spec.spacing)))
    samples = max(24, turns * 32)
    cx = spec.width / 2
    cy = spec.depth / 2
    max_radius = min(spec.width, spec.depth) / 2
    points = []
    for index in range(samples + 1):
        progress = index / samples
        radius = max_radius * progress
        angle = turns * 2 * pi * progress
        points.append(
            fc.Point(x=cx + radius * cos(angle), y=cy + radius * sin(angle), z=spec.height)
        )
    return points


def _dedupe_adjacent(points: list[fc.Point]) -> list[fc.Point]:
    deduped: list[fc.Point] = []
    for point in points:
        if not deduped or (
            point.x,
            point.y,
            point.z,
        ) != (deduped[-1].x, deduped[-1].y, deduped[-1].z):
            deduped.append(point)
    return deduped


_TEMPLATES: dict[TemplateName, _Template] = {
    "line": _Template("Single line", "A quick calibration extrusion path.", _line),
    "rectangle": _Template("Rectangle", "A closed rectangular perimeter.", _rectangle),
    "grid": _Template("Grid", "A serpentine infill-style path.", _grid),
    "spiral": _Template("Spiral", "A smooth centre-out spiral preview path.", _spiral),
}
