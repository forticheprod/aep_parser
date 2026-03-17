"""Shape value model for mask and shape path properties."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FeatherPoint:
    """A single variable-width mask feather point.

    Feather points can be placed anywhere along a closed mask path to vary
    the feather radius at different positions. Reference a specific feather
    point by the number of the mask path segment (portion of the path
    between adjacent vertices) where it appears.

    Tip:
        The feather points on a mask are listed in an array in the order
        that they were created.
    """

    seg_loc: int
    """Mask path segment number where this feather point is located
    (0-based, segments are portions of the path between vertices)."""

    rel_seg_loc: float
    """Relative position on the segment, from 0.0 (at the starting
    vertex) to 1.0 (at the next vertex)."""

    radius: float
    """Feather radius (amount). Negative values indicate inner feather
    points; positive values indicate outer feather."""

    type: int
    """Feather point direction: 0 (outer feather point) or
    1 (inner feather point)."""

    interp: int
    """Radius interpolation type: 0 for non-Hold feather points,
    1 for Hold feather points."""

    tension: float
    """Feather tension amount, from 0.0 (0%) to 1.0 (100%)."""

    rel_corner_angle: float
    """Relative angle percentage between the two normals on either side
    of a curved outer feather boundary at a corner on a mask path.
    The angle value is 0% for feather points not at corners."""


@dataclass
class Shape:
    """
    The Shape object encapsulates information describing a shape in a shape layer, or
    the outline shape of a Mask. It is the value of the "Mask Path" AE properties, and
    of the "Path" AE property of a shape layer.

    A shape has a set of anchor points, or vertices, and a pair of direction handles, or
    tangent vectors, for each anchor point. A tangent vector (in a non-roto_bezier mask)
    determines the direction of the line that is drawn to or from an anchor point. There
    is one incoming tangent vector and one outgoing tangent vector associated with each
    `vertex` in the shape.

    A tangent value is a pair of x,y coordinates specified relative to the associated
    `vertex`. For example, a tangent of [-1,-1] is located above and to the left of the
    `vertex` and has a 45 degree slope, regardless of the actual location of the
    `vertex`. The longer a handle is, the greater its influence; for example, an
    incoming shape segment stays closer to the vector for an `in_tangent` of [-2,-2]
    than it does for an `in_tangent` of [-1,-1], even though both of these come toward
    the `vertex` from the same direction.

    If a shape is not closed, the `in_tangent` for the first `vertex` and the
    `out_tangent` for the final `vertex` are ignored. If the shape is closed, these two
    vectors specify the direction handles of the final connecting segment out of the
    final `vertex` and back into the first `vertex`.

    roto_bezier masks calculate their tangents automatically
    (see MaskPropertyGroup.roto_bezier). If a shape is used in a roto_bezier mask, the
    tangent values are ignored.

    For closed mask shapes, variable-width mask feather points can exist anywhere along
    the mask path. Feather points are part of the Mask Path property. Reference a
    specific feather point by the number of the mask path segment (portion of the path
    between adjacent vertices) where it appears.

    Tip:
        The feather points on a mask are listed in an array in the order that they were
        created.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        comp = app.project.compositions[0]
        shape_layer = comp.shape_layers[0]
        shape_prop = shape_layer.content.property(name="ADBE Vector Shape - Group").property(name="ADBE Vector Shape")
        print(shape_prop.value.vertices)
        ```

    See: https://ae-scripting.docsforadobe.dev/other/shape/
    """

    closed: bool
    """
    When `True`, the first and last vertices are connected to form a closed curve. When
    `False`, the closing segment is not drawn.
    """

    vertices: list[list[float]]
    """
    The anchor points of the shape. Specify each point as an array of two floating-point
    values, and collect the point pairs into an array for the complete set of points.
    """

    in_tangents: list[list[float]]
    """
    The incoming tangent vectors, or direction handles, associated with the vertices of
    the shape. Specify each vector as an array of two floating-point values, and collect
    the vectors into an array the same length as the vertices array.

    Each tangent value defaults to [0,0]. When the mask shape is not roto_bezier, this
    results in a straight line segment.

    If the shape is in a roto_bezier mask, all tangent values are ignored and the
    tangents are automatically calculated.
    """

    out_tangents: list[list[float]]
    """
    The outgoing tangent vectors, or direction handles, associated with the vertices of
    the shape. Specify each vector as an array of two floating-point values, and collect
    the vectors into an array the same length as the vertices array.

    Each tangent value defaults to [0,0]. When the mask shape is not roto_bezier, this
    results in a straight line segment.

    If the shape is in a roto_bezier mask, all tangent values are ignored and the
    tangents are automatically calculated.
    """

    feather_points: list[FeatherPoint] = field(default_factory=list)
    """List of variable-width mask feather points."""

    @property
    def feather_seg_locs(self) -> list[int]:
        """An array containing each feather point's mask path segment
        number (section of the mask path between vertices, numbered
        starting at 0).

        Note:
            Equivalent to
            `[pt.seg_loc for pt in self.feather_points]`.
        """
        return [pt.seg_loc for pt in self.feather_points]

    @property
    def feather_rel_seg_locs(self) -> list[float]:
        """An array containing each feather point's relative position,
        from 0 to 1, on its mask path segment.

        Note:
            Equivalent to
            `[pt.rel_seg_loc for pt in self.feather_points]`.
        """
        return [pt.rel_seg_loc for pt in self.feather_points]

    @property
    def feather_radii(self) -> list[float]:
        """An array containing each feather point's radius (feather
        amount); inner feather points have negative values.

        Note:
            Equivalent to
            `[pt.radius for pt in self.feather_points]`.
        """
        return [pt.radius for pt in self.feather_points]

    @property
    def feather_types(self) -> list[int]:
        """An array containing each feather point's direction, either
        0 (outer feather point) or 1 (inner feather point).

        Note:
            Equivalent to
            `[pt.type for pt in self.feather_points]`.
        """
        return [pt.type for pt in self.feather_points]

    @property
    def feather_interps(self) -> list[int]:
        """An array containing each feather point's radius
        interpolation type (0 for non-Hold feather points, 1 for Hold
        feather points).

        Note:
            Equivalent to
            `[pt.interp for pt in self.feather_points]`.
        """
        return [pt.interp for pt in self.feather_points]

    @property
    def feather_tensions(self) -> list[float]:
        """An array containing each feather point's tension amount,
        from 0.0 (0% tension) to 1.0 (100% tension).

        Note:
            Equivalent to
            `[pt.tension for pt in self.feather_points]`.
        """
        return [pt.tension for pt in self.feather_points]

    @property
    def feather_rel_corner_angles(self) -> list[float]:
        """An array containing each feather point's relative angle
        percentage between the two normals on either side of a curved
        outer feather boundary at a corner on a mask path. The angle
        value is 0% for feather points not at corners.

        Note:
            Equivalent to
            `[pt.rel_corner_angle for pt in self.feather_points]`.
        """
        return [pt.rel_corner_angle for pt in self.feather_points]
