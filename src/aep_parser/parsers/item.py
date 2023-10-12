from __future__ import (
    absolute_import,
    unicode_literals,
    division
)

from ..kaitai.aep import Aep
from ..kaitai.utils import (
    filter_by_list_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.items.folder import Folder
from .composition import parse_composition
from .footage import parse_footage


def parse_item(item_chunk, project, parent_folder):
    child_chunks = item_chunk.data.chunks
    is_root = item_chunk.data.list_type == "Fold"

    if is_root:
        item_id = 0
        item_name = "root"
        item_type = Aep.ItemType.folder
        label = Aep.Label(0)
    else:
        item_name = _get_name(child_chunks)

        idta_chunk = find_by_type(
            chunks=child_chunks,
            chunk_type="idta"
        )
        idta_data = idta_chunk.data

        item_id = idta_data.item_id
        item_type = idta_data.item_type
        label = idta_data.label

    if item_type == Aep.ItemType.folder:
        item = parse_folder(
            is_root=is_root,
            child_chunks=child_chunks,
            project=project,
            item_id=item_id,
            item_name=item_name,
            label=label,
            parent_folder=parent_folder,
        )

    elif item_type == Aep.ItemType.footage:
        item = parse_footage(
            child_chunks=child_chunks,
            item_id=item_id,
            item_name=item_name,
            label=label,
            parent_folder=parent_folder,
        )

    elif item_type == Aep.ItemType.composition:
        item = parse_composition(
            child_chunks=child_chunks,
            item_id=item_id,
            item_name=item_name,
            label=label,
            parent_folder=parent_folder,
        )

    project.items.append(item)

    return item


def parse_folder(is_root, child_chunks, project, item_id, item_name, label, parent_folder):
    item = Folder(
        item_id=item_id,
        label=label,
        name=item_name,
        type_name="Folder",
        parent_folder=parent_folder,
        items=[],
    )
    # Get folder contents
    if is_root:
        child_item_chunks = filter_by_list_type(
            chunks=child_chunks,
            list_type="Item"
        )
    else:
        sfdr_chunk = find_by_list_type(
            chunks=child_chunks,
            list_type="Sfdr"
        )
        child_item_chunks = filter_by_list_type(
            chunks=sfdr_chunk.data.chunks,
            list_type="Item"
        )
    for child_item_chunk in child_item_chunks:
        child_item = parse_item(
            item_chunk=child_item_chunk,
            project=project,
            parent_folder=item
        )
        item.items.append(child_item)

    return item


def _get_name(child_chunks):
    name_chunk = find_by_type(
        chunks=child_chunks,
        chunk_type="Utf8"
    )
    item_name = str_contents(name_chunk)
    return item_name
