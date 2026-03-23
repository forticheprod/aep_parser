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
    filter_by_type,
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
    root_chunks: list[Aep.Chunk] = aep.body.chunks

    root_folder_chunk: Aep.Chunk = find_by_list_type(
        chunks=root_chunks, list_type="Fold"
    )
    head_chunk: Aep.HeadBody = find_by_type(chunks=root_chunks, chunk_type="head").body
    nnhd_chunk: Aep.NnhdBody = find_by_type(chunks=root_chunks, chunk_type="nnhd").body
    acer_chunk: Aep.AcerBody = find_by_type(chunks=root_chunks, chunk_type="acer").body
    adfr_chunk: Aep.AdfrBody = find_by_type(chunks=root_chunks, chunk_type="adfr").body
    dwga_chunk: Aep.DwgaBody = find_by_type(chunks=root_chunks, chunk_type="dwga").body
    gpug_chunk: Aep.Chunk = find_by_list_type(chunks=root_chunks, list_type="gpuG")
    gpug_utf8: Aep.Utf8Body = find_by_type(
        chunks=gpug_chunk.body.chunks, chunk_type="Utf8"
    ).body

    # Expression engine: LIST:ExEn > Utf8
    exen_utf8: Aep.Utf8Body | None = None
    with contextlib.suppress(ChunkNotFoundError):
        exen_chunk = find_by_list_type(chunks=root_chunks, list_type="ExEn")
        exen_utf8 = find_by_type(chunks=exen_chunk.body.chunks, chunk_type="Utf8").body

    # CMS settings JSON and baseColorProfile Utf8 chunks
    cms_utf8: Aep.Utf8Body | None = None
    ws_utf8: Aep.Utf8Body | None = None
    dcs_utf8: Aep.Utf8Body | None = None
    for c in filter_by_type(chunks=root_chunks, chunk_type="Utf8"):
        content = str_contents(c)
        if cms_utf8 is None and "lutInterpolationMethod" in content:
            cms_utf8 = c.body
        if "baseColorProfile" in content:
            if ws_utf8 is None:
                ws_utf8 = c.body
            elif dcs_utf8 is None:
                dcs_utf8 = c.body

    project = Project(
        _nnhd=nnhd_chunk,
        _head=head_chunk,
        _acer=acer_chunk,
        _adfr=adfr_chunk,
        _dwga=dwga_chunk,
        _gpug_utf8=gpug_utf8,
        _exen_utf8=exen_utf8,
        _cms_utf8=cms_utf8,
        _ws_utf8=ws_utf8,
        _dcs_utf8=dcs_utf8,
        _aep=aep,
        file=file_path,
        items={},
        render_queue=None,
    )

    project._effect_param_defs = _parse_effect_definitions(root_chunks)

    root_folder = parse_folder(
        is_root=True,
        child_chunks=root_folder_chunk.body.chunks,
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
        project.active_item = project.items[fcid_chunk.body.active_item_id]

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
    efdf_chunks = filter_by_list_type(chunks=efdg_chunk.body.chunks, list_type="EfDf")

    for efdf_chunk in efdf_chunks:
        efdf_child_chunks = efdf_chunk.body.chunks
        # First tdmn in EfDf contains the effect match name
        tdmn_chunk = find_by_type(chunks=efdf_child_chunks, chunk_type="tdmn")
        effect_match_name = str_contents(tdmn_chunk)

        # Parse param defs from the sspc chunk
        sspc_chunk = find_by_list_type(chunks=efdf_child_chunks, list_type="sspc")
        param_defs = parse_effect_param_defs(sspc_chunk.body.chunks)
        effect_defs[effect_match_name] = param_defs

    return effect_defs
