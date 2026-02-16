from __future__ import annotations

import os
import re
import typing

from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    find_chunks_before,
    str_contents,
)
from ..models.items.footage import FootageItem
from ..models.sources.file import FileSource
from ..models.sources.placeholder import PlaceholderSource
from ..models.sources.solid import SolidSource
from .mappings import map_alpha_mode, map_field_separation_type
from .utils import parse_alas_data

if typing.TYPE_CHECKING:
    from ..kaitai import Aep
    from ..models.items.folder import FolderItem


def parse_footage(
    child_chunks: list[Aep.Chunk],
    item_id: int,
    item_name: str,
    label: Aep.Label,
    parent_folder: FolderItem,
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
        parent_folder: The item's parent folder.
        comment: The item's comment.
    """
    pin_chunk = find_by_list_type(chunks=child_chunks, list_type="Pin ")

    pin_child_chunks = pin_chunk.chunks
    sspc_chunk = find_by_type(chunks=pin_child_chunks, chunk_type="sspc")
    opti_chunk = find_by_type(chunks=pin_child_chunks, chunk_type="opti")

    asset_type = opti_chunk.asset_type
    start_frame = sspc_chunk.start_frame
    end_frame = sspc_chunk.end_frame

    # Common source attributes from sspc
    source_attrs = {
        "has_alpha": sspc_chunk.has_alpha,
        "alpha_mode": map_alpha_mode(
            sspc_chunk.alpha_mode_raw, sspc_chunk.has_alpha
        ),
        "invert_alpha": sspc_chunk.invert_alpha,
        "field_separation_type": map_field_separation_type(
            sspc_chunk.field_separation_type_raw,
            sspc_chunk.field_order,
        ),
        "high_quality_field_separation": sspc_chunk.high_quality_field_separation != 0,
        "loop": sspc_chunk.loop,
        "conform_frame_rate": sspc_chunk.conform_frame_rate,
        "is_still": sspc_chunk.duration == 0,
        # premul_color: RGB bytes (0-255) converted to floats (0.0-1.0)
        "premul_color": [
            sspc_chunk.premul_color_r / 255.0,
            sspc_chunk.premul_color_g / 255.0,
            sspc_chunk.premul_color_b / 255.0,
        ],
    }

    main_source: FileSource | SolidSource | PlaceholderSource
    if not asset_type:
        asset_type = "placeholder"
        item_name = opti_chunk.placeholder_name
        main_source = PlaceholderSource(**source_attrs)
    elif asset_type == "Soli":
        asset_type = "solid"
        item_name = opti_chunk.solid_name
        color = [opti_chunk.red, opti_chunk.green, opti_chunk.blue, opti_chunk.alpha]
        main_source = SolidSource(color=color, **source_attrs)
    else:
        asset_type = "file"
        file_source = _parse_file_source(pin_child_chunks, source_attrs)

        # If start frame or end frame is undefined, try to get it from the filenames
        if 0xFFFFFFFF in (start_frame, end_frame):
            first_file_numbers = re.findall(r"\d+", file_source.file_names[0])
            last_file_numbers = re.findall(r"\d+", file_source.file_names[-1])
            if len(file_source.file_names) == 1:
                start_frame = end_frame = int(first_file_numbers[-1])
            else:
                for first, last in zip(
                    reversed(first_file_numbers), reversed(last_file_numbers)
                ):
                    if first != last:
                        start_frame = int(first)
                        end_frame = int(last)

        if not item_name:
            if (
                not source_attrs["is_still"]
                and file_source.target_is_folder
            ):
                item_name = _build_sequence_name(
                    pin_child_chunks, start_frame, end_frame,
                    file_names=file_source.file_names,
                )
            if not item_name:
                item_name = os.path.basename(file_source.file)

        main_source = file_source

    item = FootageItem(
        comment=comment,
        id=item_id,
        label=label,
        name=item_name,
        parent_folder=parent_folder,
        type_name="Footage",
        duration=sspc_chunk.duration,
        frame_duration=int(sspc_chunk.frame_duration),
        frame_rate=sspc_chunk.frame_rate,
        height=sspc_chunk.height,
        pixel_aspect=sspc_chunk.pixel_aspect,
        width=sspc_chunk.width,
        main_source=main_source,
        asset_type=asset_type,
        end_frame=end_frame,
        start_frame=start_frame,
    )
    return item


def _parse_file_source(
    pin_child_chunks: list[Aep.Chunk], source_attrs: dict
) -> FileSource:
    """
    Parse a file source.

    Args:
        pin_child_chunks: The Pin chunk's child chunks.
        source_attrs: Common source attributes from sspc.
    """
    try:
        stvc_chunk = find_by_list_type(chunks=pin_child_chunks, list_type="StVc")
        stvc_child_chunks = stvc_chunk.chunks
        utf8_chunks = filter_by_type(chunks=stvc_child_chunks, chunk_type="Utf8")
        file_names = [str_contents(chunk) for chunk in utf8_chunks]
    except ChunkNotFoundError:
        file_names = []

    alas_data = parse_alas_data(pin_child_chunks)
    if file_names:
        file = os.path.join(alas_data.get("fullpath", ""), file_names[0])
    else:
        file = alas_data.get("fullpath", "")

    target_is_folder = alas_data.get("target_is_folder", False)
    file_source = FileSource(
        file=file,
        file_names=file_names,
        target_is_folder=target_is_folder,
        **source_attrs,
    )
    return file_source


def _build_sequence_name(
    pin_child_chunks: list[Aep.Chunk],
    start_frame: int,
    end_frame: int,
    file_names: list[str] | None = None,
) -> str:
    """Build the display name for an image sequence with ``[start-end]`` format.

    After Effects displays image sequence footage items using the pattern
    ``prefix[start_frame-end_frame]extension``, for example
    ``render.[0001-0700].exr``. The prefix and extension are stored as two
    consecutive ``Utf8`` chunks immediately before the ``opti`` chunk inside
    the ``Pin`` LIST.

    Args:
        pin_child_chunks: The Pin chunk's child chunks.
        start_frame: The first frame number of the sequence.
        end_frame: The last frame number of the sequence.
        file_names: Optional list of actual filenames from StVc chunks,
            used to derive the correct zero-padding width.
    """
    if 0xFFFFFFFF in (start_frame, end_frame):
        return ""

    try:
        utf8_before_opti = find_chunks_before(
            chunks=pin_child_chunks,
            chunk_type="Utf8",
            before_type="opti",
        )
    except ChunkNotFoundError:
        return ""

    if len(utf8_before_opti) < 2:
        return ""

    prefix = str_contents(utf8_before_opti[-2])
    extension = str_contents(utf8_before_opti[-1])

    if not prefix and not extension:
        return ""

    padding = _get_frame_padding(file_names, start_frame, end_frame)
    frame_range = f"[{start_frame:0{padding}d}-{end_frame:0{padding}d}]"
    return f"{prefix}{frame_range}{extension}"


def _get_frame_padding(
    file_names: list[str] | None,
    start_frame: int,
    end_frame: int,
) -> int:
    """Determine the zero-padding width for frame numbers.

    Examines actual filenames from the sequence to detect the padding used
    on disk. Falls back to ``max(4, digits_needed)`` when filenames are
    unavailable.

    Args:
        file_names: Actual filenames from StVc chunks.
        start_frame: The first frame number.
        end_frame: The last frame number.
    """
    if file_names:
        # Extract the last group of digits from the first filename to
        # determine the padding used on disk.
        match = re.search(r"(\d+)(?=\D*$)", file_names[0])
        if match:
            return len(match.group(1))

    return max(4, len(str(end_frame)))
