"""Marker parsing functions.

Extracts composition and layer markers from MRST / Nmrd chunks.
"""

from __future__ import annotations

from ..enums import Label
from ..kaitai import Aep
from ..kaitai.utils import (
    filter_by_list_type,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.properties.marker import MarkerValue
from ..models.properties.property import Property
from .property_value import parse_property
from .utils import split_into_batches


def parse_markers(
    mrst_chunk: Aep.Chunk, time_scale: float, frame_rate: float
) -> Property:
    """
    Parse markers from an MRST chunk.

    Returns the underlying [Property][] (the ``tdbs`` inside the
    ``mrst`` chunk, with keyframes holding marker values).

    Args:
        mrst_chunk: The MRST chunk to parse.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
        frame_rate: The frame rate of the parent composition, used to compute
            marker duration in seconds.
    """
    tdbs_chunk = find_by_list_type(chunks=mrst_chunk.chunks, list_type="tdbs")
    marker_prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name="ADBE Marker",
        time_scale=time_scale,
        property_depth=1,
        frame_rate=frame_rate,
    )
    mrky_chunk = find_by_list_type(chunks=mrst_chunk.chunks, list_type="mrky")
    nmrd_chunks = filter_by_list_type(chunks=mrky_chunk.chunks, list_type="Nmrd")
    for i, nmrd_chunk in enumerate(nmrd_chunks):
        frame_time = marker_prop.keyframes[i].frame_time
        marker_prop.keyframes[i].value = parse_marker(
            nmrd_chunk=nmrd_chunk,
            frame_rate=frame_rate,
            frame_time=frame_time,
        )
    return marker_prop


def parse_marker(
    nmrd_chunk: Aep.Chunk, frame_rate: float, frame_time: int
) -> MarkerValue:
    """
    Parse a marker.

    Args:
        nmrd_chunk: The NMRD chunk to parse.
        frame_rate: The frame rate of the parent composition (unused but kept
            for API consistency).
        frame_time: The time of the marker, in frames.
    """
    nmhd_chunk = find_by_type(chunks=nmrd_chunk.chunks, chunk_type="NmHd")

    utf8_chunks = filter_by_type(chunks=nmrd_chunk.chunks, chunk_type="Utf8")

    # Marker duration from Kaitai instance (stored in 600ths of a second)
    duration = nmhd_chunk.duration

    # Parse cue point params
    params = {}
    for param_name, param_value in split_into_batches(utf8_chunks[5:], 2):
        params[str_contents(param_name)] = str_contents(param_value)

    return MarkerValue(
        chapter=str_contents(utf8_chunks[1]),
        comment=str_contents(utf8_chunks[0]),
        cue_point_name=str_contents(utf8_chunks[4]),
        duration=duration,
        navigation=nmhd_chunk.navigation,
        frame_target=str_contents(utf8_chunks[3]),
        url=str_contents(utf8_chunks[2]),
        label=Label(int(nmhd_chunk.label)),
        protected_region=nmhd_chunk.protected_region,
        params=params,
        frame_duration=nmhd_chunk.frame_duration,
        frame_time=frame_time,
    )
