from __future__ import (
    absolute_import,
    unicode_literals,
    division
)

import json
import os

from ..kaitai.utils import (
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.items.footage import FootageItem
from ..models.sources.file import FileSource
from ..models.sources.solid import SolidSource
from ..models.sources.placeholder import PlaceholderSource


def parse_footage(child_chunks, item_id, item_name, label, parent_id, comment):
    pin_chunk = find_by_list_type(
        chunks=child_chunks,
        list_type="Pin "
    )
    pin_child_chunks = pin_chunk.data.chunks
    sspc_chunk = find_by_type(
        chunks=pin_child_chunks,
        chunk_type="sspc"
    )
    opti_chunk = find_by_type(
        chunks=pin_child_chunks,
        chunk_type="opti"
    )
    sspc_data = sspc_chunk.data
    opti_data = opti_chunk.data

    asset_type = opti_data.asset_type

    if not asset_type:
        asset_type = "placeholder"
        item_name = opti_data.placeholder_name
        file = None
        main_source = PlaceholderSource()
    elif asset_type == "Soli":
        asset_type = "solid"
        item_name = opti_data.solid_name
        file = None
        color = [
            opti_data.red,
            opti_data.green,
            opti_data.blue,
            opti_data.alpha
        ]
        main_source = SolidSource(
            color=color
        )
    else:
        asset_type = "file"
        main_source = _parse_file_source(pin_child_chunks)
        file = main_source.file

        if not item_name:
            # TODO image sequence (frame numbers), psd (layers)
            # TODO add is_name_set like in Layer
            item_name = os.path.basename(file)

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
        pixel_aspect=1,  # TODO find this
        width=sspc_data.width,

        file=file,
        main_source=main_source,
        asset_type=asset_type,
        end_frame=sspc_data.end_frame,  # TODO check this
        start_frame=sspc_data.start_frame,  # TODO check this
    )
    return item


def _parse_file_source(pin_child_chunks):
    file_source_data = _get_file_source_data(pin_child_chunks)

    ascendcount_base = file_source_data["ascendcount_base"]
    ascendcount_target = file_source_data["ascendcount_target"]
    file = file_source_data["fullpath"]
    platform = file_source_data["platform"]
    server_name = file_source_data["server_name"]
    server_volume_name = file_source_data["server_volume_name"]
    target_is_folder = file_source_data["target_is_folder"]
    file_source = FileSource(
        ascendcount_base=ascendcount_base,
        ascendcount_target=ascendcount_target,
        file=file,
        platform=platform,
        server_name=server_name,
        server_volume_name=server_volume_name,
        target_is_folder=target_is_folder,
    )
    return file_source


def _get_file_source_data(pin_child_chunks):
    als2_chunk = find_by_list_type(
        chunks=pin_child_chunks,
        list_type="Als2"
    )
    als2_child_chunks = als2_chunk.data.chunks
    alas_chunk = find_by_type(
        chunks=als2_child_chunks,
        chunk_type="alas"
    )
    alas_data = json.loads(str_contents(alas_chunk))
    return alas_data
