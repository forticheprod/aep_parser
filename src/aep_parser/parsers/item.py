from __future__ import absolute_import, unicode_literals, division

from ..kaitai.aep import Aep
from ..kaitai.utils import (
    filter_by_list_type,
    find_by_list_type,
    find_by_type,
)
from ..models.items.folder import Folder
from .composition import parse_composition
from .footage import parse_footage
from .utils import (
    get_name,
    get_comment,
)


def parse_item(item_chunk, project, parent_id):
    """
    Parses an item (composition, footage or folder)
    Args:
        item_chunk (Aep.Chunk): The LIST chunk to parse.
        project (Project): The project.
        parent_id (int): The parent folder unique ID.
    Returns:
        Any[CompItem, Folder, FootageItem]: The parsed item.
    """
    is_root = item_chunk.data.list_type == "Fold"
    child_chunks = item_chunk.data.chunks
    comment = get_comment(child_chunks)

    if is_root:
        item_id = 0
        item_name = "root"
        item_type = Aep.ItemType.folder
        label = Aep.Label(0)
    else:
        item_name = get_name(child_chunks)

        idta_chunk = find_by_type(chunks=child_chunks, chunk_type="idta")
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
            parent_id=parent_id,
            comment=comment,
        )

    elif item_type == Aep.ItemType.footage:
        item = parse_footage(
            child_chunks=child_chunks,
            item_id=item_id,
            item_name=item_name,
            label=label,
            parent_id=parent_id,
            comment=comment,
        )

    elif item_type == Aep.ItemType.composition:
        item = parse_composition(
            child_chunks=child_chunks,
            item_id=item_id,
            item_name=item_name,
            label=label,
            parent_id=parent_id,
            comment=comment,
        )

    project.project_items[item_id] = item

    return item


def parse_folder(
    is_root, child_chunks, project, item_id, item_name, label, parent_id, comment
):
    """
    Parses a folder item. This function cannot be moved to it's own file as it calls
    `parse_item`, which can call `parse_folder`.
    Args:
        is_root (bool): Whether the folder is the root folder (ID 0).
        child_chunks (list[Aep.Chunk]): child chunks of the folder LIST chunk.
        project (Project): The project.
        item_id (int): The unique item ID.
        item_name (str): The folder name.
        label (Aep.MarkerLabel): The label color. Colors are represented by their number
                                 (0 for None, or 1 to 16 for one of the preset colors in
                                 the Labels preferences).
        parent_id (int): The folder's parent folder unique ID.
        comment (str): The folder comment.
    Returns:
        Folder: The parsed folder.
    """
    item = Folder(
        comment=comment,
        item_id=item_id,
        label=label,
        name=item_name,
        type_name="Folder",
        parent_id=parent_id,
        folder_items=[],
    )
    # Get folder contents
    if is_root:
        child_item_chunks = filter_by_list_type(chunks=child_chunks, list_type="Item")
    else:
        sfdr_chunk = find_by_list_type(chunks=child_chunks, list_type="Sfdr")
        child_item_chunks = filter_by_list_type(
            chunks=sfdr_chunk.data.chunks, list_type="Item"
        )
    for child_item_chunk in child_item_chunks:
        child_item = parse_item(
            item_chunk=child_item_chunk, project=project, parent_id=item_id
        )
        item.folder_items.append(child_item.item_id)

    return item
