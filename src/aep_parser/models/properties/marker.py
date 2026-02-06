from __future__ import annotations

import typing
from dataclasses import dataclass, field

if typing.TYPE_CHECKING:
    from ...kaitai import Aep


@dataclass
class Marker:
    """
    Marker object of a layer.

    Attributes:
        chapter: A text chapter link for this marker. Chapter links
            initiate a jump to a chapter in a QuickTime movie or in other
            formats that support chapter marks.
        comment: A text comment for this marker. This comment appears in
            the Timeline panel next to the layer marker.
        cue_point_name: The Flash Video cue point name, as shown in the
            Marker dialog box.
        duration: The marker's duration, in seconds.
        event_cue_point: When `True`, the FlashVideo cue point is for an event;
            otherwise, it is for navigation.
        frame_duration: The marker's duration, in frames.
        frame_target: A text frame target for this marker. Together with
            the URL value, this targets a specific frame within a Web page.
        frame_time: The time of the marker, in frames.
        label: The label color. Colors are represented by their number
            (0 for None, or 1 to 16 for one of the preset colors in the
            Labels preferences).
        navigation: Whether the marker is a navigation marker.
        params: Key-value pairs for Flash Video cue-point parameters.
        protected_region: State of the Protected Region option in the
            Composition Marker dialog box. When `True`, the composition
            marker behaves as a protected region. Will also return `True` for
            protected region markers on nested composition layers, but is
            otherwise not applicable to layer markers.
        url: A URL for this marker. This URL is an automatic link to a
            Web page.
    """

    chapter: str
    comment: str
    cue_point_name: str
    duration: float | None
    frame_duration: int
    frame_target: str
    frame_time: int
    label: Aep.Label
    navigation: bool
    params: dict[str, str]
    protected_region: bool
    url: str
    event_cue_point: bool = field(init=False)

    def __post_init__(self) -> None:
        """Set computed fields after initialization."""
        self.event_cue_point = not self.navigation
