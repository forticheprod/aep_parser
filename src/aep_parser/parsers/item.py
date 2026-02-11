from __future__ import annotations

from typing import TYPE_CHECKING

from ..kaitai import Aep
from ..kaitai.utils import (
    filter_by_list_type,
    find_by_list_type,
    find_by_type,
)
from ..models.items.folder import FolderItem
from .composition import parse_composition
from .footage import parse_footage
from .utils import (
    get_comment,
    get_name,
)

if TYPE_CHECKING:
    from ..models.items.composition import CompItem
    from ..models.items.footage import FootageItem
    from ..models.project import Project


def parse_item(
    item_chunk: Aep.Chunk, project: Project, parent_folder: FolderItem
) -> CompItem | FolderItem | FootageItem:
    """
    Parse an item (composition, footage or folder).

    Args:
        item_chunk: The LIST chunk to parse.
        project: The project.
        parent_folder: The parent folder.
    """
    child_chunks = item_chunk.chunks
    comment = get_comment(child_chunks)

    item_name = get_name(child_chunks)

    idta_chunk = find_by_type(chunks=child_chunks, chunk_type="idta")

    item_id = idta_chunk.id
    item_type = idta_chunk.item_type
    label = idta_chunk.label

    item: CompItem | FolderItem | FootageItem
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

    project.items[item_id] = item

    return item


def parse_folder(
    is_root: bool,
    child_chunks: list[Aep.Chunk],
    project: Project,
    item_id: int,
    item_name: str,
    label: Aep.Label,
    parent_folder: FolderItem | None,
    comment: str,
) -> FolderItem:
    """
    Parse a folder item.

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
    folder = FolderItem(
        comment=comment,
        id=item_id,
        label=label,
        name=item_name,
        type_name="Folder",
        parent_folder=parent_folder,
    )
    # Get folder contents
    if is_root:
        child_item_chunks = filter_by_list_type(chunks=child_chunks, list_type="Item")
    else:
        sfdr_chunk = find_by_list_type(chunks=child_chunks, list_type="Sfdr")
        child_item_chunks = filter_by_list_type(
            chunks=sfdr_chunk.chunks, list_type="Item"
        )
    for child_item_chunk in child_item_chunks:
        child_item = parse_item(
            item_chunk=child_item_chunk, project=project, parent_folder=folder
        )
        folder.items.append(child_item)

    return folder
