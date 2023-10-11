from __future__ import absolute_import
from __future__ import unicode_literals

import xml.etree.ElementTree as ET

from ..kaitai.aep import Aep
from ..kaitai.utils import (
    find_by_list_type,
    find_by_type,
    filter_by_type,
    str_contents,
)
from ..models.project import Project
from ..models.items.composition import Composition
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
            depth=get_bit_depth(root_chunks),
            effect_names=get_effect_names(root_chunks),
            expression_engine=get_expression_engine(root_chunks),
            framerate=get_framerate(root_chunks),
            project_items=dict(),
        )
        project.metadata = ET.fromstring(aep.xmp)
        software_agent = project.metadata.find(match=SOFTWARE_AGENT_XPATH)
        project.ae_version = software_agent.text

        project.root_folder = parse_item(root_folder_chunk, project)

        # Layers that have not been given an explicit name should be named after their source
        for item in project.project_items.values():
            if isinstance(item, Composition):
                for layer in item.composition_layers:
                    if not layer.name:
                        layer.name = project.project_items[layer.source_id].name


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
    return nhed_chunk.data.depth


def get_framerate(root_chunks):
    """
    Get project framerate
    """
    nnhd_chunk = find_by_type(
        chunks=root_chunks,
        chunk_type="nnhd"
    )
    return nnhd_chunk.data.framerate


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
