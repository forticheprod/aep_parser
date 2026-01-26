from __future__ import annotations

import json
import os
import re
import typing

from ..kaitai.utils import (
    filter_by_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.items.footage import FootageItem
from ..models.sources.file import FileSource
from ..models.sources.placeholder import PlaceholderSource
from ..models.sources.solid import SolidSource

if typing.TYPE_CHECKING:
    from ..kaitai.aep import Aep


def parse_footage(
    child_chunks: list[Aep.Chunk],
    item_id: int,
    item_name: str,
    label: Aep.Label,
    parent_id: int | None,
    comment: str,
) -> FootageItem:
    """
    Parse a footage item.
    Args:
        child_chunks: The footage item child chunks.
        item_id: The item's unique id.
        item_name: The item's name.
        label: The label color. Colors are represented by their number (0 for
            None, or 1 to 16 for one of the preset colors in the Labels
            preferences).
        parent_id: The item's parent folder's unique id.
        comment: The item's comment.
    """
    pin_chunk = find_by_list_type(chunks=child_chunks, list_type="Pin ")
    pin_child_chunks = pin_chunk.data.chunks
    sspc_chunk = find_by_type(chunks=pin_child_chunks, chunk_type="sspc")
    opti_chunk = find_by_type(chunks=pin_child_chunks, chunk_type="opti")
    sspc_data = sspc_chunk.data
    opti_data = opti_chunk.data

    asset_type = opti_data.asset_type
    start_frame = sspc_data.start_frame
    end_frame = sspc_data.end_frame

    if not asset_type:
        asset_type = "placeholder"
        item_name = opti_data.placeholder_name
        main_source = PlaceholderSource()
    elif asset_type == "Soli":
        asset_type = "solid"
        item_name = opti_data.solid_name
        color = [opti_data.red, opti_data.green, opti_data.blue, opti_data.alpha]
        main_source = SolidSource(color=color)
    else:
        asset_type = "file"
        main_source = _parse_file_source(pin_child_chunks)

        # If start frame or end frame is undefined, try to get it from the filenames
        if 0xFFFFFFFF in (start_frame, end_frame):
            first_file_numbers = re.findall(r"\d+", main_source.file_names[0])
            last_file_numbers = re.findall(r"\d+", main_source.file_names[-1])
            if len(main_source.file_names) == 1:
                start_frame = end_frame = int(first_file_numbers[-1])
            else:
                for first, last in zip(
                    reversed(first_file_numbers), reversed(last_file_numbers)
                ):
                    if first != last:
                        start_frame = int(first)
                        end_frame = int(last)

        if not item_name:
            item_name = os.path.basename(main_source.file)

    item = FootageItem(
        comment=comment,
        item_id=item_id,
        label=label,
        name=item_name,
        parent_id=parent_id,
        type_name="Footage",
        duration=sspc_data.duration,
        frame_duration=int(sspc_data.frame_duration),
        frame_rate=sspc_data.frame_rate,
        height=sspc_data.height,
        pixel_aspect=1,
        width=sspc_data.width,
        main_source=main_source,
        asset_type=asset_type,
        end_frame=end_frame,
        start_frame=start_frame,
    )
    return item


def _parse_file_source(pin_child_chunks: list[Aep.Chunk]) -> FileSource:
    """
    Parse a file source.
    Args:
        pin_child_chunks: The Pin chunk's child chunks.
    """
    file_source_data = _get_file_source_data(pin_child_chunks)
    stvc_chunk = find_by_list_type(chunks=pin_child_chunks, list_type="StVc")
    file_names = []
    if stvc_chunk:
        stvc_child_chunks = stvc_chunk.data.chunks
        utf8_chunks = filter_by_type(chunks=stvc_child_chunks, chunk_type="Utf8")
        file_names = [str_contents(chunk) for chunk in utf8_chunks]
    if file_names:
        file = os.path.join(file_source_data["fullpath"], file_names[0])
    else:
        file = file_source_data["fullpath"]

    target_is_folder = file_source_data["target_is_folder"]
    file_source = FileSource(
        file=file,
        file_names=file_names,
        target_is_folder=target_is_folder,
    )
    return file_source


def _get_file_source_data(pin_child_chunks: list[Aep.Chunk]) -> dict:
    """
    Get file source data from the Pin chunk.
    Args:
        pin_child_chunks: The Pin chunk's child chunks.
    """
    als2_chunk = find_by_list_type(chunks=pin_child_chunks, list_type="Als2")
    als2_child_chunks = als2_chunk.data.chunks
    alas_chunk = find_by_type(chunks=als2_child_chunks, chunk_type="alas")
    alas_data = json.loads(str_contents(alas_chunk))
    return alas_data
