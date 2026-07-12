"""Bambu Studio handoff backend."""

from __future__ import annotations

from shutil import which

from easygcode.jobs import PrintJob


def detect_installation() -> str | None:
    """Return a Bambu Studio executable path when available on PATH."""

    return which("bambu-studio") or which("bambu-studio.exe") or which("BambuStudio.exe")


def export_ascii_stl(job: PrintJob) -> str:
    """Export a simple template-sized block as ASCII STL for slicer handoff.

    This is a first-stage geometry handoff: Bambu Studio remains responsible for
    slicing, supports, AMS/material settings, and final printer-specific G-code.
    """

    width = job.design.width
    depth = job.design.depth
    height = max(job.design.height, 0.2)
    vertices = [
        (0, 0, 0),
        (width, 0, 0),
        (width, depth, 0),
        (0, depth, 0),
        (0, 0, height),
        (width, 0, height),
        (width, depth, height),
        (0, depth, height),
    ]
    faces = [
        (0, 1, 2),
        (0, 2, 3),
        (4, 6, 5),
        (4, 7, 6),
        (0, 4, 5),
        (0, 5, 1),
        (1, 5, 6),
        (1, 6, 2),
        (2, 6, 7),
        (2, 7, 3),
        (3, 7, 4),
        (3, 4, 0),
    ]
    lines = ["solid easygcode"]
    for face in faces:
        lines.extend([
            "  facet normal 0 0 0",
            "    outer loop",
        ])
        for index in face:
            x, y, z = vertices[index]
            lines.append(f"      vertex {x:.6f} {y:.6f} {z:.6f}")
        lines.extend([
            "    endloop",
            "  endfacet",
        ])
    lines.append("endsolid easygcode")
    return "\n".join(lines)


def build_cli_hint(model_filename: str, output_filename: str) -> str:
    """Return a reviewable Bambu Studio CLI command template."""

    executable = detect_installation() or "bambu-studio.exe"
    return (
        f'"{executable}" --orient --arrange 1 --slice 0 '
        f'--export-3mf "{output_filename}" "{model_filename}"'
    )
