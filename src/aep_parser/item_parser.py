from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division

import json
import os

from .kaitai.aep import Aep
from .kaitai.utils import (
    find_by_list_type,
    find_by_type,
    filter_by_list_type,
    str_contents,
)
from .layer_parser import parse_layer
from .models.items.composition import Composition
from .models.items.folder import Folder
from .models.items.asset import Asset


def parse_item(item_chunk, project):
    # TODO split asset classes and layer classes
    child_chunks = item_chunk.data.chunks
    is_root = item_chunk.data.list_type == "Fold"

    if is_root:
        item_id = 0
        item_name = "root"
        item_type = Aep.ItemType.folder
        label_color = Aep.LabelColor(0)
    else:
        name_chunk = find_by_type(
            chunks=child_chunks,
            chunk_type="Utf8"
        )
        item_name = str_contents(name_chunk)

        idta_chunk = find_by_type(
            chunks=child_chunks,
            chunk_type="idta"
        )
        idta_data = idta_chunk.data

        item_id = idta_data.item_id
        item_type = idta_data.item_type
        label_color = idta_data.label_color

    if item_type == Aep.ItemType.folder:
        item = parse_folder(
            is_root=is_root,
            child_chunks=child_chunks,
            project=project,
            item_id=item_id,
            item_name=item_name,
            label_color=label_color,
        )

    elif item_type == Aep.ItemType.asset:
        item = parse_asset(
            child_chunks=child_chunks,
            project=project,
            item_id=item_id,
            item_name=item_name,
            label_color=label_color,
        )

    elif item_type == Aep.ItemType.composition:
        item = parse_composition(
            child_chunks=child_chunks,
            item_id=item_id,
            item_name=item_name,
            label_color=label_color
        )

    project.project_items[item.item_id] = item

    return item


def parse_folder(is_root, child_chunks, project, item_id, item_name, label_color):
    folder_contents = []
    # Get folder contents
    if is_root:
        child_item_chunks = filter_by_list_type(
            chunks=child_chunks,
            list_type="Item"
        )
    else:
        sfdr_chunk = find_by_list_type(
            chunks=child_chunks,
            list_type="Sfdr"
        )
        child_item_chunks = filter_by_list_type(
            chunks=sfdr_chunk.data.chunks,
            list_type="Item"
        )
    for child_item_chunk in child_item_chunks:
        child_item = parse_item(child_item_chunk, project)
        folder_contents.append(child_item)
    
    item = Folder(
        item_id=item_id,
        name=item_name,
        label_color=label_color,
        folder_contents=folder_contents,
    )
    return item


def parse_asset(child_chunks, project, item_id, item_name, label_color):
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

    asset_type = opti_data.asset_type.strip("\x00")
    item = Asset(
        item_id=item_id,
        name=item_name,
        label_color=label_color,
        width=sspc_data.width,
        height=sspc_data.height,
        framerate=(
            sspc_data.framerate
            or project.framerate
        ),  # audio files have a framerate of 0
        duration_sec=sspc_data.duration_sec,
        duration_frames=(
            int(sspc_data.duration_frames)\
            or int(round(project.framerate * sspc_data.duration_sec))
        ),  # audio files have a frames duration of 0
        asset_type=asset_type,
        start_frame=sspc_data.start_frame,
        end_frame=sspc_data.end_frame,
    )

    if not asset_type:  # Placeholder
        item.asset_type = "placeholder"
        item.name = opti_data.placeholder_name
    elif asset_type == "Soli":  # Solid
        item.asset_type = "solid"
        item.color = [
            opti_data.red,
            opti_data.green,
            opti_data.blue,
            opti_data.alpha
        ]
        item.name = opti_data.solid_name
    else:  # Files
        item.asset_type = "file"
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

        item.ascendcount_base = alas_data["ascendcount_base"]
        item.ascendcount_target = alas_data["ascendcount_target"]
        item.path = alas_data["fullpath"]
        item.platform = alas_data["platform"]
        item.server_name = alas_data["server_name"]
        item.server_volume_name = alas_data["server_volume_name"]
        item.target_is_folder = alas_data["target_is_folder"]

        if not item.name:
            # TODO image sequence (frame numbers), psd (layers)
            # TODO add "name_overriden" or "default_name" ? label like properties ?
            item.name = os.path.basename(item.path)
    return item


def parse_composition(child_chunks, item_id, item_name, label_color):
    cdta_chunk = find_by_type(
        chunks=child_chunks,
        chunk_type="cdta"
    )
    cdta_data = cdta_chunk.data

    # Parse composition's layers
    layer_sub_chunks = filter_by_list_type(
        chunks=child_chunks,
        list_type="Layr"
    )
    composition_layers = []
    for index, layer_chunk in enumerate(layer_sub_chunks, start=1):
        layer = parse_layer(layer_chunk)
        layer.index = index
        composition_layers.append(layer)

    item = Composition(
        item_id=item_id,
        name=item_name,
        label_color=label_color,
        
        x_resolution=cdta_data.x_resolution,
        y_resolution=cdta_data.y_resolution,

        framerate=cdta_data.framerate,  # TODO check
        playhead_sec=cdta_data.playhead,  # TODO check
        playhead_frames=int(cdta_data.playhead_frames),  # TODO check
        in_time_sec=cdta_data.in_time,  # TODO check
        in_time_frames=int(cdta_data.in_time_frames),  # TODO check
        out_time_sec=cdta_data.out_time,  # TODO check
        out_time_frames=int(cdta_data.out_time_frames),  # TODO check
        duration_sec=cdta_data.duration_sec,  # TODO check
        duration_frames=int(cdta_data.duration_frames),  # TODO check

        background_color=cdta_data.background_color,  # TODO check order
        shy_enabled=cdta_data.shy_enabled,
        motion_blur_enabled=cdta_data.motion_blur_enabled,
        frame_blend_enabled=cdta_data.frame_blend_enabled,
        preserve_framerate=cdta_data.preserve_framerate,
        preserve_resolution=cdta_data.preserve_resolution,
        asset_width=cdta_data.width,
        asset_height=cdta_data.height,
        pixel_ratio=cdta_data.pixel_ratio,
        shutter_angle=cdta_data.shutter_angle,
        shutter_phase=cdta_data.shutter_phase,
        samples_limit=cdta_data.samples_limit,
        samples_per_frame=cdta_data.samples_per_frame,

        composition_layers=composition_layers,
    )
    return item