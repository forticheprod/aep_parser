from __future__ import annotations

import os
import xml.etree.ElementTree as ET

from ..kaitai import Aep
from ..kaitai.utils import (
    filter_by_type,
    find_by_list_type,
    find_by_type,
    get_enum_value,
    str_contents,
)
from ..models.project import Project
from .item import parse_folder
from .mappings import (
    map_bits_per_channel,
    map_footage_timecode_display_start_type,
    map_frames_count_type,
    map_time_display_type,
)

SOFTWARE_AGENT_XPATH = ".//stEvt:softwareAgent"
XMP_NAMESPACES = {"stEvt": "http://ns.adobe.com/xap/1.0/sType/ResourceEvent#"}


def parse_project(aep_file_path: str | os.PathLike[str]) -> Project:
    """
    Parse an After Effects (.aep) project file.

    Args:
        aep_file_path: path to the project file
    """
    file_path = os.fspath(aep_file_path)
    with Aep.from_file(file_path) as aep:
        root_chunks = aep.data.chunks

        root_folder_chunk = find_by_list_type(chunks=root_chunks, list_type="Fold")
        nnhd_chunk = find_by_type(chunks=root_chunks, chunk_type="nnhd")
        nnhd_data = nnhd_chunk.data

        project = Project(
            bits_per_channel=map_bits_per_channel(
                get_enum_value(nnhd_data.bits_per_channel)
            ),
            effect_names=_get_effect_names(root_chunks),
            expression_engine=_get_expression_engine(root_chunks),  # CC 2019+
            file=file_path,
            footage_timecode_display_start_type=map_footage_timecode_display_start_type(
                get_enum_value(nnhd_data.footage_timecode_display_start_type)
            ),
            frame_rate=nnhd_data.frame_rate,
            frames_count_type=map_frames_count_type(
                get_enum_value(nnhd_data.frames_count_type)
            ),
            project_items={},
            time_display_type=map_time_display_type(
                get_enum_value(nnhd_data.time_display_type)
            ),
        )

        project.xmp_packet = ET.fromstring(aep.xmp_packet)
        software_agents = project.xmp_packet.findall(
            path=SOFTWARE_AGENT_XPATH, namespaces=XMP_NAMESPACES
        )
        if software_agents:
            project.ae_version = software_agents[-1].text

        root_folder = parse_folder(
            is_root=True,
            child_chunks=root_folder_chunk.data.chunks,
            project=project,
            item_id=0,
            item_name="root",
            label=Aep.Label(0),
            parent_folder=None,
            comment="",
        )
        project.project_items[0] = root_folder

        # Link layers to their source items and parent layers
        for composition in project.compositions:
            # Build layer lookup by id for this composition
            layers_by_id = {layer.layer_id: layer for layer in composition.layers}
            for layer in composition.layers:
                if layer.layer_type == Aep.LayerType.footage:
                    layer.source = project.project_items.get(layer.source_id)
                if layer.parent_id is not None:
                    layer.parent = layers_by_id.get(layer.parent_id)

        return project


def _get_expression_engine(root_chunks: list[Aep.Chunk]) -> str | None:
    """
    Get the expression engine used in the project.

    Args:
        root_chunks (Aep.Chunk): list of root chunks of the project
    """
    expression_engine_chunk = find_by_list_type(chunks=root_chunks, list_type="ExEn")
    if expression_engine_chunk:
        utf8_chunk = find_by_type(
            chunks=expression_engine_chunk.data.chunks, chunk_type="Utf8"
        )
        return str_contents(utf8_chunk)
    return None


def _get_effect_names(root_chunks: list[Aep.Chunk]) -> list[str]:
    """
    Get the list of effect names used in the project.

    Args:
        root_chunks (Aep.Chunk): list of root chunks of the project
    """
    pefl_chunk = find_by_list_type(chunks=root_chunks, list_type="Pefl")
    pefl_child_chunks = pefl_chunk.data.chunks
    pjef_chunks = filter_by_type(chunks=pefl_child_chunks, chunk_type="pjef")
    return [str_contents(chunk) for chunk in pjef_chunks]
