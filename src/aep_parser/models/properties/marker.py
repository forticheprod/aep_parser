from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from ...kaitai.aep import Aep


class Marker:
    def __init__(
        self,
        chapter: str,
        comment: str,
        cue_point_name: str,
        duration: float | None,
        navigation: bool,
        frame_target: str,
        url: str,
        label: Aep.Label,
        protected_region: bool,
        params: dict[str, str],
        frame_duration: int,
        frame_time: int | None = None,
    ):
        """
        Marker object of a layer.

        Args:
            chapter: A text chapter link for this marker. Chapter links
                initiate a jump to a chapter in a QuickTime movie or in other
                formats that support chapter marks.
            comment: A text comment for this marker. This comment appears in
                the Timeline panel next to the layer marker.
            cue_point_name: The Flash Video cue point name, as shown in the
                Marker dialog box.
            duration: The marker's duration, in seconds.
            navigation: Whether the marker is a navigation marker.
            frame_target: A text frame target for this marker. Together with
                the URL value, this targets a specific frame within a Web page.
            url: A URL for this marker. This URL is an automatic link to a
                Web page.
            label: The label color. Colors are represented by their number
                (0 for None, or 1 to 16 for one of the preset colors in the
                Labels preferences).
            protected_region: State of the Protected Region option in the
                Composition Marker dialog box. When true, the composition
                marker behaves as a protected region. Will also return true for
                protected region markers on nested composition layers, but is
                otherwise not applicable to layer markers.
            params: Key-value pairs for Flash Video cue-point parameters.
            frame_duration: The marker's duration, in frames.
            frame_time: The time of the marker, in frames.
        """
        self.chapter = chapter
        self.comment = comment
        self.cue_point_name = cue_point_name
        self.duration = duration
        self.navigation = navigation
        self.event_cue_point = not (navigation)
        self.frame_target = frame_target
        self.url = url
        self.label = label
        self.protected_region = protected_region
        self.params = params

        self.frame_duration = frame_duration
        self.frame_time = frame_time

    def __repr__(self) -> str:
        return str(self.__dict__)
