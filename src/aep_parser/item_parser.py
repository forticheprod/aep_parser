from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division

from aep_parser.kaitai.aep import Aep
from aep_parser.layer_parser import parse_layer
from aep_parser.models.composition import Composition
from aep_parser.models.folder import Folder
from aep_parser.models.asset import Asset
from aep_parser.rifx.utils import (
    find_by_identifier,
    find_by_type,
    filter_by_identifier,
    str_contents,
)


def parse_item(item_chunk, project):
    child_chunks = item_chunk.data.chunks.chunks
    is_root = item_chunk.data.identifier == "Fold"

    # Parse item metadata
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
        if name_chunk is None:
            print(
                "could not find name chunk for {item_chunk}"
                .format(item_chunk=item_chunk)
            )
            return
        item_name = str_contents(name_chunk)

        idta_chunk = find_by_type(
            chunks=child_chunks,
            chunk_type="idta"
        )
        if idta_chunk is None:
            print(
                "could not find idta chunk for {item_chunk}"
                .format(item_chunk=item_chunk)
            )
            return
        idta_data = idta_chunk.data

        item_id = idta_data.item_id
        item_type = Aep.ItemType(idta_data.item_type)
        label_color = Aep.LabelColor(idta_data.label_color)

    # Parse unique item type information
    if item_type == Aep.ItemType.folder:
        item_class = Folder
    elif item_type == Aep.ItemType.asset:
        item_class = Asset
    elif item_type == Aep.ItemType.composition:
        item_class = Composition

    item = item_class(
        item_id = item_id,
        item_type = item_type,
        name = item_name,
        label_color = label_color
    )

    # Parse unique item type information
    if item.item_type == Aep.ItemType.folder:
        folder_contents = []
        child_sfdr_chunks = filter_by_identifier(
            chunks=child_chunks,
            identifier="Sfdr"
        )
        child_item_list_chunks = filter_by_identifier(
            chunks=child_chunks + child_sfdr_chunks,
            identifier="Item"
        )
        for child_item_list_chunk in child_item_list_chunks:
            child_item = parse_item(child_item_list_chunk, project)
            if child_item is None:
                print(
                    "could not parse {child_item_list_chunk}, child chunk of {item_chunk}"
                    .format(
                        child_item_list_chunk=child_item_list_chunk,
                        item_chunk=item_chunk,
                    )
                )
                continue

            folder_contents.append(child_item)
        item.folder_contents = folder_contents

    elif item.item_type == Aep.ItemType.asset:
        pin_chunk = find_by_identifier(
            chunks=child_chunks,
            identifier="Pin "
        )
        if not pin_chunk:
            print(
                "could not find Pin for chunk {item_chunk}"
                .format(item_chunk=item_chunk)
            )
            return

        pin_child_chunks = pin_chunk.data.chunks.chunks

        sspc_chunk = find_by_type(
            chunks=pin_child_chunks,
            chunk_type="sspc"
        )
        if sspc_chunk is None:
            print(
                "could not find sspc for chunk {item_chunk}"
                .format(item_chunk=item_chunk)
            )
            return
        sspc_data = sspc_chunk.data

        item.width = sspc_data.width
        item.height = sspc_data.height
        item.framerate = float(sspc_data.framerate + sspc_data.framerate_dividend) / (1 << 16)
        item.duration_sec = sspc_data.duration

        opti_chunk = find_by_type(
            chunks=pin_child_chunks,
            chunk_type="opti"
        )
        if opti_chunk is None:
            # TODO add warning
            return

        opti_data = opti_chunk.data
        item.asset_type = opti_data.asset_type
        if item.asset_type == "Soli":
            item.color = opti_data.color
            item.name = opti_data.solid_name
        # TODO continue (mov, sound, placeholder, etc)
        # TODO split asset classes
        # TODO split item parser (folder, comp, asset)

    elif item.item_type == Aep.ItemType.composition:
        cdta_chunk = find_by_type(
            chunks=child_chunks,
            chunk_type="cdta"
        )
        if cdta_chunk is None:
            # TODO add warning
            return
        cdta_data = cdta_chunk.data

        item.x_resolution = cdta_data.x_resolution
        item.y_resolution = cdta_data.y_resolution

        item.framerate = cdta_data.framerate
        item.playhead_sec = cdta_data.playhead
        item.playhead_frames = cdta_data.playhead_frames
        item.in_time_sec = cdta_data.in_time
        item.in_time_frames = cdta_data.in_time_frames
        item.out_time_sec = cdta_data.out_time  # TODO check
        item.out_time_frames = cdta_data.out_time_frames
        item.duration_sec = cdta_data.duration
        item.duration_frames = cdta_data.duration_frames

        item.background_color = cdta_data.background_color
        item.shy_enabled = cdta_data.shy_enabled
        item.motion_blur_enabled = cdta_data.motion_blur_enabled
        item.frame_blend_enabled = cdta_data.frame_blend_enabled
        item.preserve_framerate = cdta_data.preserve_framerate
        item.preserve_resolution = cdta_data.preserve_resolution
        item.asset_width = cdta_data.width
        item.asset_height = cdta_data.height
        item.pixel_ratio = cdta_data.pixel_ratio
        item.shutter_angle = cdta_data.shutter_angle
        item.shutter_phase = cdta_data.shutter_phase
        item.samples_limit = cdta_data.samples_limit
        item.samples_per_frame = cdta_data.samples_per_frame

        # Parse composition's layers
        layer_sub_chunks = filter_by_identifier(
            chunks=child_chunks,
            identifier="Layr"
        )
        composition_layers = []
        for index, layer_chunk in enumerate(layer_sub_chunks, start=1):
            layer = parse_layer(layer_chunk)
            if layer is None:
                print(
                    "could not find sspc for chunk {item_chunk}"
                    .format(item_chunk=item_chunk)
                )
                return
            layer.index = index
            composition_layers.append(layer)
        item.composition_layers = composition_layers

    project.project_items[item.item_id] = item

    return item
