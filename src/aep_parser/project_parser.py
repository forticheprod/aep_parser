from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from aep_parser.item_parser import parse_item
from aep_parser.kaitai.aep import Aep
from aep_parser.models.project import Project
from aep_parser.rifx.utils import (
    find_by_identifier,
    find_by_type,
)


"""
based on https://github.com/boltframe/aftereffects-aep-parser/blob/70803375303cc769cc25829faf061ff8061ecc53/project.go
"""


def parse_project(path):
    with Aep.from_file(path) as aep:
        project = Project()

        root_blocks = aep.data.blocks
        expression_engine = find_by_identifier(root_blocks, "ExEn") 
        if expression_engine:
            project.expression_engine = expression_engine

        # get project depth in BPC (8, 16 or 32)
        nhed_block = find_by_type(root_blocks, Aep.ChunkType.nhed)
        if nhed_block is None:
            msg = (
                "Could not find 'nhed' block in project {path}"
                .format(
                    path=path,
                )
            )
            raise Exception(msg)
        project.depth = nhed_block.data.depth

        root_folder_block = find_by_identifier(root_blocks, "Fold")
        if root_folder_block is None:
            msg = (
                "Could not find 'Fold' block in project {path}"
                .format(
                    path=path,
                )
            )
            raise Exception(msg)

        folder = parse_item(root_folder_block, project)
        if folder is None:
            msg = (
                "Could not parse 'Fold' block in project {path}"
                .format(
                    path=path,
                )
            )
            raise Exception(msg)

        project.root_folder = folder

        # TODO move to layer_parser
        # Layers that have not been given an explicit name should be named after their source
        for item in project.items.values():
            if item.item_type == Aep.ItemType.COMPOSITION:
                for layer in item.composition_layers:
                    if not layer.name:
                        layer.name = project.items[layer.source_id].name

        return project
