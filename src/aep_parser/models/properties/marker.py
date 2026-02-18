from __future__ import annotations

from dataclasses import dataclass, field

from ..enums import Label


@dataclass
class MarkerValue:
    """
    The `MarkerValue` object represents a layer or composition marker, which
    associates a comment, and optionally a chapter reference point, Web-page
    link, or Flash Video cue point with a particular point in a layer.

    See: https://ae-scripting.docsforadobe.dev/other/markervalue/
    """

    chapter: str
    """
    A text chapter link for this marker. Chapter links initiate a jump to a
    chapter in a QuickTime movie or in other formats that support chapter
    marks.
    """

    comment: str
    """
    A text comment for this marker. This comment appears in the Timeline panel
    next to the layer marker.
    """

    cue_point_name: str
    """The Flash Video cue point name, as shown in the Marker dialog box."""

    duration: float
    """The marker's duration, in seconds."""

    frame_duration: int
    """The marker's duration, in frames."""

    frame_target: str
    """
    A text frame target for this marker. Together with the URL value, this
    targets a specific frame within a Web page.
    """

    frame_time: int
    """The time of the marker, in frames."""

    label: Label
    """
    The label color. Colors are represented by their number (0 for None, or 1
    to 16 for one of the preset colors in the Labels preferences).
    """

    navigation: bool
    """Whether the marker is a navigation marker."""

    params: dict[str, str]
    """Key-value pairs for Flash Video cue-point parameters."""

    protected_region: bool
    """
    State of the Protected Region option in the Composition Marker dialog box.
    When `True`, the composition marker behaves as a protected region. Will
    also return `True` for protected region markers on nested composition
    layers, but is otherwise not applicable to layer markers.
    """

    url: str
    """A URL for this marker. This URL is an automatic link to a Web page."""

    event_cue_point: bool = field(init=False)
    """
    When `True`, the FlashVideo cue point is for an event; otherwise, it is
    for navigation.
    """

    def __post_init__(self) -> None:
        """Set computed fields after initialization."""
        self.event_cue_point = not self.navigation
