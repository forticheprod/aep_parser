from __future__ import annotations

import typing

from ..kaitai import Aep
from ..kaitai.utils import (
    filter_by_list_type,
    find_by_list_type,
    find_by_type,
)
from ..models.items.folder import Folder
from .composition import parse_composition
from .footage import parse_footage
from .utils import (
    get_comment,
    get_name,
)

if typing.TYPE_CHECKING:
    from ..models.items.composition import CompItem
    from ..models.items.footage import FootageItem
    from ..models.project import Project


def parse_item(
    item_chunk: Aep.Chunk, project: Project, parent_folder: Folder | None
) -> CompItem | Folder | FootageItem:
    """
    Parse an item (composition, footage or folder).

    Args:
        item_chunk: The LIST chunk to parse.
        project: The project.
        parent_folder: The parent folder.
    """
    child_chunks = item_chunk.data.chunks
    comment = get_comment(child_chunks)

    item_name = get_name(child_chunks)

    idta_chunk = find_by_type(chunks=child_chunks, chunk_type="idta")
    idta_data = idta_chunk.data

    item_id = idta_data.item_id
    item_type = idta_data.item_type
    label = idta_data.label

    if item_type == Aep.ItemType.folder:
        item = parse_folder(
            is_root=False,
            child_chunks=child_chunks,
            project=project,
            item_id=item_id,
            item_name=item_name,
            label=label,
            parent_folder=parent_folder,
            comment=comment,
        )

    elif item_type == Aep.ItemType.footage:
        item = parse_footage(
            child_chunks=child_chunks,
            item_id=item_id,
            item_name=item_name,
            label=label,
            parent_folder=parent_folder,
            comment=comment,
        )

    elif item_type == Aep.ItemType.composition:
        item = parse_composition(
            child_chunks=child_chunks,
            item_id=item_id,
            item_name=item_name,
            label=label,
            parent_folder=parent_folder,
            comment=comment,
        )

    project.project_items[item_id] = item

    return item


def parse_folder(
    is_root: bool,
    child_chunks: list[Aep.Chunk],
    project: Project,
    item_id: int,
    item_name: str,
    label: Aep.Label,
    parent_folder: Folder | None,
    comment: str,
) -> Folder:
    """
    Parse a folder item.

    This function cannot be moved to its own file as it calls `parse_item`,
    which can call `parse_folder`.

    Args:
        is_root: Whether the folder is the root folder (ID 0).
        child_chunks: child chunks of the folder LIST chunk.
        project: The project.
        item_id: The unique item ID.
        item_name: The folder name.
        label: The label color. Colors are represented by their number (0 for
            None, or 1 to 16 for one of the preset colors in the Labels
            preferences).
        parent_folder: The folder's parent folder.
        comment: The folder comment.
    """
    folder = Folder(
        comment=comment,
        item_id=item_id,
        label=label,
        name=item_name,
        type_name="Folder",
        parent_folder=parent_folder,
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
            item_chunk=child_item_chunk, project=project, parent_folder=folder
        )
        folder.folder_items.append(child_item.item_id)

    return folder
