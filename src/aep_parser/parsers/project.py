from __future__ import (
    absolute_import,
    unicode_literals,
    division
)
import sys
import xml.etree.ElementTree as ET

from ..kaitai.aep import Aep
from ..kaitai.utils import (
    find_by_list_type,
    find_by_type,
    filter_by_type,
    str_contents,
)
from ..models.project import Project
from .item import parse_item


SOFTWARE_AGENT_XPATH = ".//{*}softwareAgent"


def parse_project(aep_file_path):
    """
    Args:
        aep_file_path (str): path to the project file
    Returns:
        Project: The parsed After Effects (.aep) project
    """
    with Aep.from_file(aep_file_path) as aep:
        root_chunks = aep.data.chunks

        root_folder_chunk = find_by_list_type(
            chunks=root_chunks,
            list_type="Fold"
        )
        nnhd_chunk = find_by_type(
            chunks=root_chunks,
            chunk_type="nnhd"
        )
        nnhd_data = nnhd_chunk.data

        project = Project(
            bits_per_channel=nnhd_data.bits_per_channel,
            effect_names=_get_effect_names(root_chunks),
            expression_engine=_get_expression_engine(root_chunks),  # CC 2019+
            file=aep_file_path,
            footage_timecode_display_start_type=nnhd_data.footage_timecode_display_start_type,
            frame_rate=nnhd_data.frame_rate,
            frames_count_type=nnhd_data.frames_count_type,
            project_items=dict(),
            time_display_type=nnhd_data.time_display_type,
        )

        if sys.version_info >= (3, 0):
            project.xmp_packet = ET.fromstring(aep.xmp_packet)
            software_agent = project.xmp_packet.find(path=SOFTWARE_AGENT_XPATH)
            project.ae_version = software_agent.text
        else:
            project.xmp_packet = ET.fromstring(aep.xmp_packet.encode("utf-8"))
            software_agents = (
                node.text
                for node in project.xmp_packet.iter()
                if node.tag.endswith("softwareAgent")
            )
            project.ae_version = next(software_agents)

        parse_item(root_folder_chunk, project, parent_id=None)

        # Use source item properties for layers
        for composition in project.compositions:
            for layer in composition.layers:
                if layer.layer_type == Aep.LayerType.footage:
                    layer_source_item = project.project_items[layer.source_id]
                    if not layer.name:
                        layer.name = layer_source_item.name
                    layer.width = layer_source_item.width
                    layer.height = layer_source_item.height

        return project


def _get_expression_engine(root_chunks):
    """
    Args:
        root_chunks (Aep.Chunk): list of root chunks of the project
    Returns:
        str: expression engine used in the project
    """
    expression_engine_chunk = find_by_list_type(
        chunks=root_chunks,
        list_type="ExEn"
    )
    if expression_engine_chunk:
        return str_contents(expression_engine_chunk)


def _get_effect_names(root_chunks):
    """
    Args:
        root_chunks (Aep.Chunk): list of root chunks of the project
    Returns:
        list[str]: list of effect names used in the project.
    """
    pefl_chunk = find_by_list_type(
        chunks=root_chunks,
        list_type="Pefl"
    )
    pefl_child_chunks = pefl_chunk.data.chunks
    pjef_chunks = filter_by_type(
        chunks=pefl_child_chunks,
        chunk_type="pjef"
    )
    return [
        str_contents(chunk)
        for chunk in pjef_chunks
    ]
