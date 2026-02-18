from __future__ import annotations

import contextlib
import json
import os
import xml.etree.ElementTree as ET

from ..kaitai import Aep
from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.enums import (
    ColorManagementSystem,
    FeetFramesFilmType,
    FramesCountType,
    Label,
    LutInterpolationMethod,
    TimeDisplayType,
)
from ..models.layers.av_layer import AVLayer
from ..models.project import Project
from ..utils import deprecated
from .app import parse_app
from .item import parse_folder
from .mappings import (
    map_bits_per_channel,
    map_footage_timecode_display_start_type,
)
from .render_queue import parse_render_queue


@deprecated(
    "Use aep_parser.parse() instead, which returns an App object. "
    "Access the project via app.project."
)
def parse_project(aep_file_path: str | os.PathLike[str]) -> Project:
    """Parse an After Effects (.aep) project file.

    Warning: Deprecated
        Use [aep_parser.parse][] instead which returns an
        [App][aep_parser.models.app.App] instance.  Access the project
        via ``app.project``.

    Args:
        aep_file_path: path to the project file
    """
    file_path = os.fspath(aep_file_path)
    with Aep.from_file(file_path) as aep:
        project = _parse_project(aep, file_path)
        return parse_app(aep, project).project


def _parse_project(aep: Aep, file_path: str) -> Project:
    """Parse an After Effects (.aep) project file into a Project.

    Args:
        aep: The parsed Kaitai RIFX structure.
        file_path: Path to the ``.aep`` file (stored on the Project).
    """
    root_chunks = aep.data.chunks

    root_folder_chunk = find_by_list_type(chunks=root_chunks, list_type="Fold")
    head_chunk = find_by_type(chunks=root_chunks, chunk_type="head")
    nnhd_chunk = find_by_type(chunks=root_chunks, chunk_type="nnhd")
    acer_chunk = find_by_type(chunks=root_chunks, chunk_type="acer")
    dwga_chunk = find_by_type(chunks=root_chunks, chunk_type="dwga")
    xmp_packet = ET.fromstring(aep.xmp_packet)

    color_profile = _get_color_profile_settings(root_chunks)

    project = Project(
        bits_per_channel=map_bits_per_channel(nnhd_chunk.bits_per_channel),
        revision=head_chunk.file_revision,
        color_management_system=ColorManagementSystem(
            int(color_profile["colorManagementSystem"])
        ),
        compensate_for_scene_referred_profiles=bool(
            acer_chunk.compensate_for_scene_referred_profiles
        ),
        effect_names=_get_effect_names(root_chunks),
        expression_engine=_get_expression_engine(root_chunks),  # CC 2019+
        feet_frames_film_type=FeetFramesFilmType.from_binary(
            nnhd_chunk.feet_frames_film_type
        ),
        lut_interpolation_method=LutInterpolationMethod(
            int(color_profile["lutInterpolationMethod"])
        ),
        ocio_configuration_file=str(color_profile["ocioConfigurationFile"]),
        file=file_path,
        footage_timecode_display_start_type=map_footage_timecode_display_start_type(
            nnhd_chunk.footage_timecode_display_start_type
        ),
        frame_rate=nnhd_chunk.frame_rate,
        frames_count_type=FramesCountType.from_binary(nnhd_chunk.frames_count_type),
        frames_use_feet_frames=nnhd_chunk.frames_use_feet_frames,
        linear_blending=any(c.chunk_type == "lnrb" for c in root_chunks),
        linearize_working_space=nnhd_chunk.linearize_working_space,
        working_gamma=dwga_chunk.working_gamma,
        working_space=_get_working_space(root_chunks),
        items={},
        render_queue=None,
        time_display_type=TimeDisplayType.from_binary(nnhd_chunk.time_display_type),
        transparency_grid_thumbnails=bool(nnhd_chunk.transparency_grid_thumbnails),
        xmp_packet=xmp_packet,
    )

    root_folder = parse_folder(
        is_root=True,
        child_chunks=root_folder_chunk.chunks,
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
        project.active_item = project.items[fcid_chunk.active_item_id]

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
            if layer._parent_id != 0:
                layer.parent = layers_by_id.get(layer._parent_id)


def _clamp_layer_times(
    layer: Aep.Chunk,
    source: object,
    composition: object,
) -> None:
    """Clamp layer in/outPoint to source duration.

    After Effects clamps timing values when queried via ExtendScript:

    * ``outPoint`` is clamped to
      ``start_time + source.duration * abs(stretch / 100)`` for non-still
      footage layers where ``time_remap_enabled`` is ``False``.
    * ``inPoint`` is clamped to ``start_time`` when it falls before the
      layer's start time (positive stretch only).

    These clamps do **not** apply when ``time_remap_enabled`` is ``True``,
    since time-remapped layers have arbitrary time mapping.

    Note: ``collapse_transformation`` (continuously rasterise) does **not**
    prevent clamping — AE still clamps ``outPoint`` to the source duration.

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
    # Note: collapse_transformation does NOT skip clamping — AE still clamps
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


def _get_expression_engine(root_chunks: list[Aep.Chunk]) -> str:
    """
    Get the expression engine used in the project.

    Args:
        root_chunks (Aep.Chunk): list of root chunks of the project
    """
    try:
        expression_engine_chunk = find_by_list_type(
            chunks=root_chunks, list_type="ExEn"
        )
        utf8_chunk = find_by_type(
            chunks=expression_engine_chunk.chunks, chunk_type="Utf8"
        )
        return str_contents(utf8_chunk)
    except ChunkNotFoundError:
        return "extendscript"


def _get_effect_names(root_chunks: list[Aep.Chunk]) -> list[str]:
    """
    Get the list of effect names used in the project.

    Args:
        root_chunks (Aep.Chunk): list of root chunks of the project
    """
    pefl_chunk = find_by_list_type(chunks=root_chunks, list_type="Pefl")
    pefl_child_chunks = pefl_chunk.chunks
    pjef_chunks = filter_by_type(chunks=pefl_child_chunks, chunk_type="pjef")
    return [str_contents(chunk) for chunk in pjef_chunks]


def _get_color_profile_settings(root_chunks: list[Aep.Chunk]) -> dict[str, int | str]:
    """
    Get color profile settings from the project.

    The settings are stored as JSON in a Utf8 chunk at the root level.

    Args:
        root_chunks: list of root chunks of the project

    Returns:
        Dict with colorManagementSystem, lutInterpolationMethod, and
        ocioConfigurationFile values.
    """
    defaults: dict[str, int | str] = {
        "colorManagementSystem": 0,  # Adobe
        "lutInterpolationMethod": 0,  # Trilinear
        "ocioConfigurationFile": "",
    }
    for chunk in filter_by_type(chunks=root_chunks, chunk_type="Utf8"):
        utf8_content = str_contents(chunk)
        if "lutInterpolationMethod" in utf8_content:
            cms_data = json.loads(utf8_content)
            # Merge with defaults so missing keys get default values
            return {**defaults, **cms_data}

    return defaults


def _get_working_space(root_chunks: list[Aep.Chunk]) -> str:
    """
    Get the working color space name from the project.

    The working space is stored in a Utf8 chunk containing JSON with
    baseColorProfile.colorProfileName.

    Args:
        root_chunks: list of root chunks of the project

    Returns:
        The working space name (e.g., "sRGB IEC61966-2.1") or "None" if not set.
    """
    for chunk in filter_by_type(chunks=root_chunks, chunk_type="Utf8"):
        utf8_content = str_contents(chunk)
        if "baseColorProfile" in utf8_content:
            profile_data = json.loads(utf8_content)
            base_profile = profile_data.get("baseColorProfile", {})
            return str(base_profile.get("colorProfileName", "None"))
    return "None"
