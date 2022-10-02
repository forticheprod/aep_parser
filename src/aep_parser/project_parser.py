from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from aep_parser.item_parser import parse_item
from aep_parser.kaitai.aep import Aep
from aep_parser.models.depth import Depth
from aep_parser.models.item_type import (
    ItemTypeName,
)
from aep_parser.models.project import Project
from aep_parser.rifx.utils import (
    sublist_find,
    find_by_type,
)


"""
based on https://github.com/boltframe/aftereffects-aep-parser/blob/70803375303cc769cc25829faf061ff8061ecc53/project.go
"""


def parse_project(path):
    with Aep.from_file(path) as aep:
        root_blocks = aep.data.entries

        project = Project()

        expression_engines = sublist_find(root_blocks, "ExEn")
        if expression_engines:
            project.expression_engine = expression_engines[0]

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
        project.depth = Depth(nhed_block.data.data)

        root_folder_list = sublist_find(root_blocks, "Fold")
        if not root_folder_list:
            msg = (
                "Could not find 'Fold' block in project {path}"
                .format(
                    path=path,
                )
            )
            raise Exception(msg)
        root_folder_block = root_folder_list[0]

        folder = parse_item(root_folder_block, project)
        project.root_folder = folder

        # Layers that have not been given an explicit name should be named after their source
        for item_id, item in project.items.items():
            if item.item_type == ItemTypeName.ITEM_TYPE_COMPOSITION:
                for layer in item.composition_layers:
                    if layer.name == "":
                        layer.name = project.items[layer.source_id].name

        return project
