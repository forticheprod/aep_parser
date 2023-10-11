from __future__ import (
    absolute_import,
    unicode_literals,
    division
)

import xml.etree.ElementTree as ET

from ..kaitai.aep import Aep
from ..kaitai.utils import (
    find_by_list_type,
    find_by_type,
    filter_by_type,
    str_contents,
)
from ..models.project import Project
from ..models.items.composition import CompItem
from .item import parse_item


SOFTWARE_AGENT_XPATH = ".//{*}softwareAgent"


def parse_project(path):
    with Aep.from_file(path) as aep:
        root_chunks = aep.data.chunks

        root_folder_chunk = find_by_list_type(
            chunks=root_chunks,
            list_type="Fold"
        )
        
        project = Project(
            bits_per_channel=get_bit_depth(root_chunks),
            effect_names=get_effect_names(root_chunks),
            expression_engine=get_expression_engine(root_chunks),
            frame_rate=get_frame_rate(root_chunks),
            items=[],
        )
        project.xmp_packet = ET.fromstring(aep.xmp_packet)
        software_agent = project.xmp_packet.find(path=SOFTWARE_AGENT_XPATH)
        project.ae_version = software_agent.text

        project.root_folder = parse_item(root_folder_chunk, project, parent_folder=None)

        # Layers that have not been given an explicit name should be named after their source
        for item in project.items:
            if isinstance(item, CompItem):
                for layer in item.layers:
                    if not layer.name:
                        layer_source_item = project.item_by_id(layer.source_id)
                        layer.name = layer_source_item.name

        return project


def get_expression_engine(root_chunks):
    """
    Get expression engine used in project
    """
    expression_engine_chunk = find_by_list_type(
        chunks=root_chunks,
        list_type="ExEn"
    )
    if expression_engine_chunk:
        return str_contents(expression_engine_chunk)  # TODO check


def get_bit_depth(root_chunks):
    """
    Get project depth in BPC (8, 16 or 32)
    """
    nhed_chunk = find_by_type(
        chunks=root_chunks,
        chunk_type="nhed"
    )
    return nhed_chunk.data.bits_per_channel


def get_frame_rate(root_chunks):
    """
    Get project frame_rate
    """
    nnhd_chunk = find_by_type(
        chunks=root_chunks,
        chunk_type="nnhd"
    )
    return nnhd_chunk.data.frame_rate


def get_effect_names(root_chunks):
    """
    Get names of effects used in project
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
