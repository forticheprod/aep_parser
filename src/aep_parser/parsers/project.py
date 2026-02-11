from __future__ import annotations

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
    LutInterpolationMethod,
    TimeDisplayType,
)
from ..models.project import Project
from .item import parse_folder
from .mappings import (
    map_bits_per_channel,
    map_footage_timecode_display_start_type,
    map_gpu_accel_type,
)
from .render_queue import parse_render_queue


def parse_project(aep_file_path: str | os.PathLike[str]) -> Project:
    """
    Parse an After Effects (.aep) project file.

    Args:
        aep_file_path: path to the project file
    """
    file_path = os.fspath(aep_file_path)
    with Aep.from_file(file_path) as aep:
        root_chunks = aep.data.chunks

        root_folder_chunk = find_by_list_type(chunks=root_chunks, list_type="Fold")
        nnhd_chunk = find_by_type(chunks=root_chunks, chunk_type="nnhd")
        head_chunk = find_by_type(chunks=root_chunks, chunk_type="head")
        acer_chunk = find_by_type(chunks=root_chunks, chunk_type="acer")
        dwga_chunk = find_by_type(chunks=root_chunks, chunk_type="dwga")
        lrdr_chunk = find_by_list_type(chunks=root_chunks, list_type="LRdr")
        rhed_chunk = find_by_type(chunks=lrdr_chunk.chunks, chunk_type="Rhed")
        xmp_packet = ET.fromstring(aep.xmp_packet)

        # Parse version from binary header
        # Format: {major}.{minor}x{build}
        ae_version = (
            f"{head_chunk.ae_version_major}."
            f"{head_chunk.ae_version_minor}x"
            f"{head_chunk.ae_build_number}"
        )
        ae_build_number = head_chunk.ae_build_number

        # Parse color profile settings from JSON in CPPl section
        color_profile = _get_color_profile_settings(root_chunks)

        project = Project(
            ae_version=ae_version,
            ae_build_number=ae_build_number,
            bits_per_channel=map_bits_per_channel(
                nnhd_chunk.bits_per_channel
            ),
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
            frames_count_type=FramesCountType.from_binary(
                nnhd_chunk.frames_count_type
            ),
            frames_use_feet_frames=bool(nnhd_chunk.frames_use_feet_frames),
            gpu_accel_type=map_gpu_accel_type(rhed_chunk.gpu_accel_type),
            linear_blending=any(c.chunk_type == "lnrb" for c in root_chunks),
            linearize_working_space=bool(nnhd_chunk.linearize_working_space),
            working_gamma=2.4 if dwga_chunk.working_gamma_selector else 2.2,
            working_space=_get_working_space(root_chunks),
            items={},
            render_queue=None,
            time_display_type=TimeDisplayType.from_binary(
                nnhd_chunk.time_display_type
            ),
            xmp_packet=xmp_packet,
        )

        root_folder = parse_folder(
            is_root=True,
            child_chunks=root_folder_chunk.chunks,
            project=project,
            item_id=0,
            item_name="root",
            label=Aep.Label(0),
            parent_folder=None,
            comment="",
        )
        project.items[0] = root_folder
        project.root_folder = root_folder

        # Link layers to their source items and parent layers
        for composition in project.compositions:
            # Build layer lookup by id for this composition
            layers_by_id = {layer.id: layer for layer in composition.layers}
            for layer in composition.layers:
                if layer.layer_type == Aep.LayerType.footage and hasattr(layer, "source_id"):
                    source = project.items.get(layer.source_id)
                    if hasattr(layer, "source"):
                        layer.source = source
                if layer.parent_id is not None:
                    layer.parent = layers_by_id.get(layer.parent_id)

        # Parse render_queue after items to link comp references in render queue items
        project.render_queue = parse_render_queue(root_chunks, project)

        return project


def _get_expression_engine(root_chunks: list[Aep.Chunk]) -> str:
    """
    Get the expression engine used in the project.

    Args:
        root_chunks (Aep.Chunk): list of root chunks of the project
    """
    try:
        expression_engine_chunk = find_by_list_type(chunks=root_chunks, list_type="ExEn")
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
