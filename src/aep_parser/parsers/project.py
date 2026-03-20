from __future__ import annotations

import contextlib
import os
from typing import Any

from ..enums import (
    Label,
)
from ..kaitai import Aep
from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_list_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.layers.av_layer import AVLayer
from ..models.layers.light_layer import LightLayer
from ..models.project import Project
from ..utils import deprecated
from .application import parse_app
from .defaults import set_layer_property_defaults, set_transform_defaults
from .item import parse_folder
from .property import parse_effect_param_defs
from .render_queue import parse_render_queue


@deprecated(
    "Use aep_parser.parse() instead, which returns an Application object. "
    "Access the project via app.project."
)
def parse_project(aep_file_path: str | os.PathLike[str]) -> Project:
    """Parse an After Effects (.aep) project file.

    Warning: Deprecated
        Use [aep_parser.parse][] instead which returns an
        [Application][aep_parser.models.application.Application] instance.  Access the project
        via `app.project`.

    Args:
        aep_file_path: path to the project file
    """
    file_path = os.fspath(aep_file_path)
    with Aep.from_file(file_path) as aep:
        aep._read()
        project = _parse_project(aep, file_path)
        return parse_app(aep, project).project


def _parse_project(aep: Aep, file_path: str) -> Project:
    """Parse an After Effects (.aep) project file into a Project.

    Args:
        aep: The parsed Kaitai RIFX structure.
        file_path: Path to the `.aep` file (stored on the Project).
    """
    root_chunks: list[Aep.Chunk] = aep.data.chunks

    root_folder_chunk: Aep.Chunk = find_by_list_type(chunks=root_chunks, list_type="Fold")
    head_chunk: Aep.Chunk = find_by_type(chunks=root_chunks, chunk_type="head")
    nnhd_chunk: Aep.Chunk = find_by_type(chunks=root_chunks, chunk_type="nnhd")
    acer_chunk: Aep.Chunk = find_by_type(chunks=root_chunks, chunk_type="acer")
    adfr_chunk: Aep.Chunk = find_by_type(chunks=root_chunks, chunk_type="adfr")
    dwga_chunk: Aep.Chunk = find_by_type(chunks=root_chunks, chunk_type="dwga")
    gpug_chunk: Aep.Chunk = find_by_list_type(chunks=root_chunks, list_type="gpuG")
    utf8_chunk: Aep.Chunk = find_by_type(chunks=gpug_chunk.data.chunks, chunk_type="Utf8")

    project = Project(
        _nnhd=nnhd_chunk.data,
        _head=head_chunk.data,
        _acer=acer_chunk.data,
        _adfr=adfr_chunk.data,
        _dwga=dwga_chunk.data,
        _utf8=utf8_chunk.data,
        _aep=aep,
        file=file_path,
        items={},
        render_queue=None,
    )

    project._effect_param_defs = _parse_effect_definitions(root_chunks)

    root_folder = parse_folder(
        is_root=True,
        child_chunks=root_folder_chunk.data.chunks,
        project=project,
        item_id=0,
        item_name="root",
        label=Label(0),
        parent_folder=None,
        comment="",
    )
    project.items[0] = root_folder
    project.root_folder = root_folder

    _link_layers(project)

    project.render_queue = parse_render_queue(root_chunks, project)

    with contextlib.suppress(ChunkNotFoundError):
        fcid_chunk = find_by_type(chunks=root_chunks, chunk_type="fcid")
        project.active_item = project.items[fcid_chunk.data.active_item_id]

    return project


def _link_layers(project: Project) -> None:
    for composition in project.compositions:
        layers_by_id = {layer.id: layer for layer in composition.layers}
        for layer in composition.layers:
            if isinstance(layer, AVLayer) and layer._source_id != 0:
                source = project.items.get(layer._source_id)
                if source is not None:
                    layer.source = source
                    _clamp_layer_times(layer, source, composition)
                    if hasattr(source, "_used_in"):
                        source._used_in.add(composition)
            if isinstance(layer, AVLayer) and layer._matte_layer_id != 0:
                matte = layers_by_id.get(layer._matte_layer_id)
                if isinstance(matte, AVLayer):
                    layer._track_matte_layer = matte
                    matte._is_track_matte = True
            if layer._parent_id != 0:
                layer.parent = layers_by_id.get(layer._parent_id)
            if isinstance(layer, LightLayer) and layer._light_source_id != 0:
                layer.light_source = layers_by_id.get(layer._light_source_id)
            set_transform_defaults(layer)
            set_layer_property_defaults(layer)


def _clamp_layer_times(
    layer: Aep.Chunk,
    source: object,
    composition: object,
) -> None:
    """Clamp layer in/outPoint to source duration.

    After Effects clamps timing values when queried via ExtendScript:

    * `outPoint` is clamped to
      `start_time + source.duration * abs(stretch / 100)` for non-still
      footage layers where `time_remap_enabled` is `False`.
    * `inPoint` is clamped to `start_time` when it falls before the
      layer's start time (positive stretch only).

    These clamps do **not** apply when `time_remap_enabled` is `True`,
    since time-remapped layers have arbitrary time mapping.

    Note: `collapse_transformation` (continuously rasterise) does **not**
    prevent clamping - AE still clamps `outPoint` to the source duration.

    Args:
        layer: The layer whose timing may need clamping.
        source: The source item for the layer.
        composition: The parent composition (for frame rate).
    """
    if source is None:
        return

    # Skip still images (duration=0, no meaningful clamp)
    is_still = False
    if hasattr(source, "main_source"):
        is_still = source.main_source.is_still
    if is_still:
        return

    # Skip layers with time_remap_enabled (time remap has arbitrary mapping)
    # Note: collapse_transformation does NOT skip clamping - AE still clamps
    if getattr(layer, "time_remap_enabled", False):
        return

    source_duration = getattr(source, "duration", 0)
    if source_duration <= 0:
        return

    stretch = getattr(layer, "stretch", 100.0)

    # Skip negative stretch (reverse playback) - different clamp rules
    if stretch < 0:
        return

    frame_rate = getattr(composition, "frame_rate", 24.0)
    stretch_factor = abs(stretch / 100.0) if stretch != 0 else 1.0

    # Clamp inPoint: cannot be before start_time
    if layer.in_point < layer.start_time:
        layer.in_point = layer.start_time
        layer.frame_in_point = round(layer.start_time * frame_rate)

    # Clamp outPoint: cannot exceed start_time + source.duration * stretch
    max_out = layer.start_time + source_duration * stretch_factor
    if layer.out_point > max_out:
        layer.out_point = max_out
        layer.frame_out_point = round(max_out * frame_rate)


def _parse_effect_definitions(
    root_chunks: list[Aep.Chunk],
) -> dict[str, dict[str, dict[str, Any]]]:
    """Parse project-level effect definitions from LIST:EfdG.

    EfdG contains parameter definitions for every effect type used in the
    project. Unlike layer-level sspc chunks, the EfdG definitions always
    include a parT chunk.

    Args:
        root_chunks: The root chunks of the AEP file.

    Returns:
        Dict mapping effect match names to their parameter definitions
        (effect_match_name -> param_match_name -> param_def dict).
    """
    try:
        efdg_chunk = find_by_list_type(chunks=root_chunks, list_type="EfdG")
    except ChunkNotFoundError:
        return {}

    effect_defs: dict[str, dict[str, dict[str, Any]]] = {}
    efdf_chunks = filter_by_list_type(chunks=efdg_chunk.data.chunks, list_type="EfDf")

    for efdf_chunk in efdf_chunks:
        efdf_child_chunks = efdf_chunk.data.chunks
        # First tdmn in EfDf contains the effect match name
        tdmn_chunk = find_by_type(chunks=efdf_child_chunks, chunk_type="tdmn")
        effect_match_name = str_contents(tdmn_chunk)

        # Parse param defs from the sspc chunk
        sspc_chunk = find_by_list_type(chunks=efdf_child_chunks, list_type="sspc")
        param_defs = parse_effect_param_defs(sspc_chunk.data.chunks)
        effect_defs[effect_match_name] = param_defs

    return effect_defs
