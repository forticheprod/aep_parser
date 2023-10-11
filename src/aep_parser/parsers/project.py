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


"""
based on https://github.com/boltframe/aftereffects-aep-parser/blob/70803375303cc769cc25829faf061ff8061ecc53/project.go
"""


def parse_project(path):
    with Aep.from_file(path) as aep:
        project = Project(
            project_items=dict()
        )

        root_chunks = aep.data.chunks

        project.expression_engine = get_expression_engine(root_chunks)
        project.depth = get_bit_depth(root_chunks)
        project.framerate = get_framerate(root_chunks)
        # Get names of effects used in project
        project.effect_names = get_effect_names(root_chunks)

        root_folder_chunk = find_by_list_type(
            chunks=root_chunks,
            list_type="Fold"
        )
        folder = parse_item(root_folder_chunk, project)
        if folder is None:
            raise Exception(
                "Could not parse 'Fold' chunk in project {path}"
                .format(
                    path=path,
            ))
        project.root_folder = folder

        # Layers that have not been given an explicit name should be named after their source
        for item in project.project_items.values():
            if isinstance(item, Composition):
                for layer in item.composition_layers:
                    if not layer.name:
                        layer.name = project.project_items[layer.source_id].name

        project.metadata = ET.fromstring(aep.xmp)
        software_agent = project.metadata.find(".//{*}softwareAgent")
        project.ae_version = software_agent.text

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
