"""Shape value model for mask and shape path properties."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ShapeValue:
    """A shape path value containing Bezier curve data.

    Represents the shape of a mask or shape path property. The shape is
    defined by a series of vertices with incoming and outgoing tangent
    handles that form a Bezier curve.

    All coordinate values are in composition-space pixels (absolute
    coordinates), matching the representation returned by ExtendScript's
    ``MaskPropertyGroup.maskShape`` / ``Property.value`` for shape
    properties.

    See: https://ae-scripting.docsforadobe.dev/other/shape/
    """

    closed: bool
    """When `True`, the shape path is closed (last vertex connects to first)."""

    vertices: list[list[float]]
    """
    List of ``[x, y]`` vertex positions.
    """

    in_tangents: list[list[float]]
    """
    List of ``[x, y]`` incoming tangent offsets relative to each vertex.
    """

    out_tangents: list[list[float]]
    """
    List of ``[x, y]`` outgoing tangent offsets relative to each vertex.
    """
