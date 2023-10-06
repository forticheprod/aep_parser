from __future__ import absolute_import
from __future__ import unicode_literals

import xml.etree.ElementTree as ET

from .item_parser import parse_item
from .kaitai.aep import Aep
from .kaitai.utils import (
    find_by_list_type,
    find_by_type,
    filter_by_type,
    str_contents,
)
from .models.project import Project


"""
based on https://github.com/boltframe/aftereffects-aep-parser/blob/70803375303cc769cc25829faf061ff8061ecc53/project.go
"""


def parse_project(path):
    with Aep.from_file(path) as aep:
        project = Project(
            project_items=dict()
        )

        root_chunks = aep.data.chunks
        expression_engine_chunk = find_by_list_type(
            chunks=root_chunks,
            list_type="ExEn"
        ) 
        if expression_engine_chunk:
            project.expression_engine = str_contents(expression_engine_chunk)  # TODO check

        # Get project depth in BPC (8, 16 or 32)
        nhed_chunk = find_by_type(
            chunks=root_chunks,
            chunk_type="nhed"
        )
        project.depth = nhed_chunk.data.depth  # FIXME

        # Get project framerate
        nnhd_chunk = find_by_type(
            chunks=root_chunks,
            chunk_type="nnhd"
        )
        project.framerate = nnhd_chunk.data.framerate

        # Get names of effects used in project
        pefl_chunk = find_by_list_type(
            chunks=root_chunks,
            list_type="Pefl"
        )
        pefl_child_chunks = pefl_chunk.data.chunks
        pjef_chunks = filter_by_type(
            chunks=pefl_child_chunks,
            chunk_type="pjef"
        )
        project.effect_names = [
            str_contents(pjef_chunk)
            for pjef_chunk in pjef_chunks
        ]

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

        # # Layers that have not been given an explicit name should be named after their source
        # for item in project.project_items.values():
        #     if item.item_type == Aep.ItemType.composition:
        #         for layer in item.composition_layers:
        #             if not layer.name:
        #                 layer.name = project.project_items[layer.source_id].name

        project.metadata = ET.fromstring(aep.xmp)
        software_agent = project.metadata.find(".//{*}softwareAgent")
        project.ae_version = software_agent.text

        return project
