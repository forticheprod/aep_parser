"""Marker parsing functions.

Extracts composition and layer markers from MRST / Nmrd chunks.
"""

from __future__ import annotations

import typing

from ..kaitai import Aep
from ..kaitai.utils import (
    filter_by_list_type,
    filter_by_type,
    find_by_list_type,
    find_by_type,
)
from ..models.properties.marker import MarkerValue
from ..models.properties.property import Property
from .property_value import parse_property

if typing.TYPE_CHECKING:
    from ..models.items.composition import CompItem
    from ..models.properties.keyframe import Keyframe


def parse_markers(
    mrst_chunk: Aep.Chunk,
    composition: CompItem,
    property_depth: int = 1,
) -> Property:
    """
    Parse markers from an MRST chunk.

    Returns the underlying [Property][] (the `tdbs` inside the
    `mrst` chunk, with keyframes holding marker values).

    Args:
        mrst_chunk: The MRST chunk to parse.
        composition: The parent composition.
        property_depth: The nesting depth of this property (default 1).
    """
    tdbs_chunk = find_by_list_type(chunks=mrst_chunk.body.chunks, list_type="tdbs")
    marker_prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name="ADBE Marker",
        composition=composition,
        property_depth=property_depth,
    )
    mrky_chunk = find_by_list_type(chunks=mrst_chunk.body.chunks, list_type="mrky")
    nmrd_chunks = filter_by_list_type(chunks=mrky_chunk.body.chunks, list_type="Nmrd")
    for i, nmrd_chunk in enumerate(nmrd_chunks):
        kf = marker_prop.keyframes[i]
        marker_prop.keyframes[i].value = parse_marker(
            nmrd_chunk=nmrd_chunk,
            keyframe=kf,
        )
    return marker_prop


def parse_marker(
    nmrd_chunk: Aep.Chunk,
    keyframe: Keyframe | None = None,
    frame_time: int = 0,
) -> MarkerValue:
    """
    Parse a marker.

    Args:
        nmrd_chunk: The NMRD chunk to parse.
        keyframe: The keyframe that holds this marker value.
        frame_time: Fallback time in frames (used when no keyframe ref).
    """
    nmhd_chunk = find_by_type(chunks=nmrd_chunk.body.chunks, chunk_type="NmHd")

    utf8_chunks = filter_by_type(chunks=nmrd_chunk.body.chunks, chunk_type="Utf8")

    # Collect cue point param Utf8 bodies
    param_utf8s = [c.body for c in utf8_chunks[5:]]

    return MarkerValue(
        _nmhd=nmhd_chunk.body,
        _comment_utf8=utf8_chunks[0].body,
        _chapter_utf8=utf8_chunks[1].body,
        _url_utf8=utf8_chunks[2].body,
        _frame_target_utf8=utf8_chunks[3].body,
        _cue_point_name_utf8=utf8_chunks[4].body,
        _keyframe=keyframe,
        frame_time=frame_time,
        _param_utf8s=param_utf8s,
    )
