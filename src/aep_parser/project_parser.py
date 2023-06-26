from __future__ import absolute_import
from __future__ import unicode_literals

from aep_parser.item_parser import parse_item
from aep_parser.kaitai.aep import Aep
from aep_parser.models.project import Project
from aep_parser.rifx.utils import (
    find_by_identifier,
    find_by_type,
    str_contents,
)


"""
based on https://github.com/boltframe/aftereffects-aep-parser/blob/70803375303cc769cc25829faf061ff8061ecc53/project.go
"""


def parse_project(path):
    with Aep.from_file(path) as aep:
        project = Project()

        root_chunks = aep.data.chunks
        expression_engine_chunk = find_by_identifier(
            chunks=root_chunks,
            identifier="ExEn"
        ) 
        if expression_engine_chunk:
            project.expression_engine = str_contents(expression_engine_chunk)  # FIXME

        # get project depth in BPC (8, 16 or 32)
        nhed_chunk = find_by_type(
            chunks=root_chunks,
            chunk_type="nhed"
        )
        if nhed_chunk is None:
            msg = (
                "Could not find 'nhed' chunk in project {path}"
                .format(
                    path=path,
                )
            )
            raise Exception(msg)
        project.depth = nhed_chunk.data.depth

        root_folder_chunk = find_by_identifier(
            chunks=root_chunks,
            identifier="Fold"
        )
        if root_folder_chunk is None:
            msg = (
                "Could not find 'Fold' chunk in project {path}"
                .format(
                    path=path,
                )
            )
            raise Exception(msg)

        folder = parse_item(root_folder_chunk, project)
        if folder is None:
            msg = (
                "Could not parse 'Fold' chunk in project {path}"
                .format(
                    path=path,
                )
            )
            raise Exception(msg)

        project.root_folder = folder

        # # Layers that have not been given an explicit name should be named after their source
        # for item in project.project_items.values():
        #     if item.item_type == Aep.ItemType.composition:
        #         for layer in item.composition_layers:
        #             if not layer.name:
        #                 layer.name = project.project_items[layer.source_id].name

        return project
