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
from .property import parse_property
from .utils import split_into_batches


def parse_markers(
    mrst_chunk: Aep.Chunk, group_match_name: str, time_scale: float, frame_rate: float
) -> list[MarkerValue]:
    """
    Parse markers.

    Args:
        mrst_chunk: The MRST chunk to parse.
        group_match_name: A special name for the property used to build unique
            naming paths. The match name is not displayed, but you can refer
            to it in scripts. Every property has a unique match-name
            identifier. Match names are stable from version to version
            regardless of the display name (the name attribute value) or any
            changes to the application. Unlike the display name, it is not
            localized. An indexed group (`PropertyBase.property_type ==
            PropertyType.indexed_group`) may not have a name value, but
            always has a match_name value.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
        frame_rate: The frame rate of the parent composition, used to compute
            marker duration in seconds.
    """
    tdbs_chunk = find_by_list_type(chunks=mrst_chunk.chunks, list_type="tdbs")
    marker_group = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=group_match_name,
        time_scale=time_scale,
        property_depth=1,
    )
    mrky_chunk = find_by_list_type(chunks=mrst_chunk.chunks, list_type="mrky")
    nmrd_chunks = filter_by_list_type(chunks=mrky_chunk.chunks, list_type="Nmrd")
    markers = []
    for i, nmrd_chunk in enumerate(nmrd_chunks):
        frame_time = marker_group.keyframes[i].frame_time
        marker = parse_marker(
            nmrd_chunk=nmrd_chunk,
            frame_rate=frame_rate,
            frame_time=frame_time,
        )
        markers.append(marker)
    return markers


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
