from __future__ import annotations

import typing
from typing import Any

from ..enums import Label
from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_list_type,
    find_by_list_type,
    find_by_type,
)
from ..models.items.composition import CompItem
from .layer import parse_layer

if typing.TYPE_CHECKING:
    from ..kaitai import Aep
    from ..models.items.folder import FolderItem
    from ..models.properties.property import Property


def parse_composition(
    child_chunks: list[Aep.Chunk],
    item_id: int,
    item_name: str,
    label: Label,
    parent_folder: FolderItem,
    comment: str,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
) -> CompItem:
    """
    Parse a composition item.

    Args:
        child_chunks: child chunks of the composition LIST chunk.
        item_id: The unique item ID.
        item_name: The composition name.
        label: The label color. Colors are represented by their number (0 for
            None, or 1 to 16 for one of the preset colors in the Labels
            preferences).
        parent_folder: The composition's parent folder.
        comment: The composition comment.
        effect_param_defs: Project-level effect parameter definitions, used as
            fallback when layer-level parT chunks are missing.
    """
    cdta_chunk = find_by_type(chunks=child_chunks, chunk_type="cdta")
    try:
        cdrp_chunk = find_by_type(chunks=child_chunks, chunk_type="cdrp")
        cdrp_body = cdrp_chunk.body
    except ChunkNotFoundError:
        cdrp_body = None

    composition = CompItem(
        comment=comment,
        id=item_id,
        label=label,
        name=item_name,
        parent_folder=parent_folder,
        cdta=cdta_chunk.body,
        cdrp=cdrp_body,
    )

    composition.marker_property = _get_markers(
        child_chunks=child_chunks,
        composition=composition,
    )

    # Parse composition's layers
    layer_sub_chunks = filter_by_list_type(chunks=child_chunks, list_type="Layr")

    # Build layer_id-to-index mapping for LAYER control effect properties.
    # ExtendScript reports 1-based layer indices; the binary stores internal
    # layer IDs (ldta.layer_id).  Pre-scan all layer chunks so the mapping
    # is available when parsing effect properties.
    layer_id_to_index: dict[int, int] = {}
    for idx, lc in enumerate(layer_sub_chunks, 1):
        ldta = find_by_type(chunks=lc.body.chunks, chunk_type="ldta")
        layer_id_to_index[ldta.body.layer_id] = idx

    for layer_chunk in layer_sub_chunks:
        layer = parse_layer(
            layer_chunk=layer_chunk,
            composition=composition,
            effect_param_defs=effect_param_defs,
            layer_id_to_index=layer_id_to_index,
        )
        composition.layers.append(layer)

    # Apply effect selected states from Ewst/ewot chunks
    selected_states = _parse_effect_selected(child_chunks)
    effect_idx = 0
    for layer in composition.layers:
        if layer.effects is None:
            continue
        for effect in layer.effects:
            if effect_idx < len(selected_states):
                effect.selected = selected_states[effect_idx]
            effect_idx += 1

    return composition


def _parse_effect_selected(child_chunks: list[Aep.Chunk]) -> list[bool]:
    """Parse effect selected states from LIST:Ewst / ewot chunks.

    The `ewot` chunk inside `LIST:Ewst` stores per-property flags for
    the effect workspace.  Each entry is 4 bytes: the first byte contains
    flags where bit 6 (`0x40`) indicates *selected*.  Entries whose first
    byte has bit 7 (`0x80`) set are child properties of an effect; entries
    **without** bit 7 are effect-group-level entries.  By filtering to the
    group-level entries and checking bit 6 we obtain a boolean per effect.

    Args:
        child_chunks: The composition item's child chunks.

    Returns:
        Ordered list of booleans, one per effect across all layers.
    """
    selected: list[bool] = []
    ewst_chunks = filter_by_list_type(chunks=child_chunks, list_type="Ewst")
    for ewst_chunk in ewst_chunks:
        try:
            ewot_chunk = find_by_type(chunks=ewst_chunk.body.chunks, chunk_type="ewot")
        except ChunkNotFoundError:
            continue

        for entry in ewot_chunk.body.entries:
            # Entries without is_child_property are effect group nodes
            if not entry.is_child_property:
                selected.append(entry.selected)

    return selected


def _get_markers(
    child_chunks: list[Aep.Chunk], composition: CompItem
) -> Property | None:
    """
    Get the composition markers.

    Marker keyframe times in the binary format are stored in absolute
    composition time (not relative to the SecL layer's start time).

    Args:
        child_chunks: child chunks of the composition LIST chunk.
        composition: The parent composition.
    """
    markers_layer_chunk = find_by_list_type(chunks=child_chunks, list_type="SecL")
    markers_layer = parse_layer(
        layer_chunk=markers_layer_chunk,
        composition=composition,
        effect_param_defs={},
    )
    if markers_layer.marker is None:
        return None

    return markers_layer.marker
