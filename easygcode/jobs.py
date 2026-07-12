"""Shared print-job models for EasyGcode backends."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from .core import DesignSpec

PrintMode = Literal["direct", "bambu_studio"]


class PrintJob(BaseModel):
    """A user-facing print task shared by direct and slicer-based workflows."""

    mode: PrintMode = Field("bambu_studio", description="Backend used to prepare the print")
    printer_id: str = Field("generic", min_length=1)
    design: DesignSpec = Field(default_factory=DesignSpec)
    material: str = Field("PLA", min_length=1)
    nozzle_diameter: float = Field(0.4, gt=0, le=2)
    bed_type: str = Field("textured_pei", min_length=1)
    output_path: Optional[str] = None


class PreparedPrint(BaseModel):
    """Prepared artifact metadata returned to the frontend before printing."""

    mode: PrintMode
    status: Literal["ready", "needs_bambu_studio", "blocked"]
    filename: str
    mime_type: str
    content: str
    encoding: Literal["text", "base64"] = "text"
    warnings: list[str] = Field(default_factory=list)
    summary: dict[str, object] = Field(default_factory=dict)
