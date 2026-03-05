from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

from ..enums import (
    AudioBitDepth,
    AudioChannels,
    AudioSampleRate,
    ConvertToLinearLight,
    OutputChannels,
    OutputColorDepth,
    OutputColorMode,
    OutputFormat,
    PostRenderAction,
    ResizeQuality,
)
from ..kaitai import Aep
from ..kaitai.utils import filter_by_type, find_by_type, str_contents
from ..models.items.composition import CompItem
from ..models.renderqueue.output_module import OutputModule
from ..models.renderqueue.render_queue_item import RenderQueueItem
from ..models.settings import OutputModuleSettings
from .format_options import parse_format_options
from .mappings import map_output_audio, map_output_color_space
from .utils import parse_alas_data

if TYPE_CHECKING:
    from ..models.project import Project


def _parse_output_module_settings(
    roou_chunk: Aep.Chunk,
    om_ldat_data: Aep.OutputModuleSettingsLdatBody,
    include_source_xmp: bool,
    post_render_action: PostRenderAction,
    full_flat_path: str,
    base_path: str,
    file_name_template: str,
    output_color_space: str | None,
) -> OutputModuleSettings:
    """Parse all output module settings from Roou chunk and ldat data.

    Combines settings from the Roou chunk (codec, format, audio, etc.)
    with per-output-module settings from the ldat body (crop, channels,
    resize, etc.) into a single dict with ExtendScript-compatible keys.

    Args:
        roou_chunk: The Roou chunk containing output options.
        om_ldat_data: Parsed OutputModuleSettingsLdatBody.
        include_source_xmp: Whether source XMP metadata is included.
        post_render_action: The post-render action setting.
        output_color_space: The resolved output color space name, or
            ``None`` if unknown.

    Returns:
        Dict with ExtendScript keys like "Video Output", "Audio Bit Depth",
        "Crop", "Channels", etc.
    """
    audio_bit_depth = AudioBitDepth.from_binary(roou_chunk.audio_bit_depth)
    audio_channels = AudioChannels.from_binary(roou_chunk.audio_channels)
    color = OutputColorMode(roou_chunk.color_premultiplied)

    # Extract subfolder from file_name_template when it contains path
    # separators.  AE stores the subfolder prepended to the filename
    # template in Utf8[2], e.g. "toto\Comp 1.[fileExtension]".
    if "\\" in file_name_template or "/" in file_name_template:
        sep = "\\" if "\\" in file_name_template else "/"
        last_sep_idx = file_name_template.rfind(sep)
        subfolder_path = file_name_template[:last_sep_idx]
        file_name = file_name_template[last_sep_idx + 1 :]
    else:
        subfolder_path = ""
        file_name = file_name_template

    return {
        "Audio Bit Depth": audio_bit_depth,
        "Audio Channels": audio_channels,
        "Audio Sample Rate": AudioSampleRate.from_binary(
            int(roou_chunk.audio_sample_rate)
        ),
        "Channels": OutputChannels(om_ldat_data.channels),
        "Color": color,
        "Convert to Linear Light": ConvertToLinearLight(
            om_ldat_data.convert_to_linear_light
        ),
        "Crop Bottom": om_ldat_data.crop_bottom,
        "Crop Left": om_ldat_data.crop_left,
        "Crop Right": om_ldat_data.crop_right,
        "Crop Top": om_ldat_data.crop_top,
        "Crop": om_ldat_data.crop,
        "Depth": OutputColorDepth(roou_chunk.depth),
        "Format": OutputFormat.from_format_id(roou_chunk.format_id),
        "Include Project Link": bool(om_ldat_data.include_project_link),
        "Include Source XMP Metadata": include_source_xmp,
        "Lock Aspect Ratio": bool(om_ldat_data.lock_aspect_ratio),
        "Output Audio": map_output_audio(
            roou_chunk.output_audio, om_ldat_data.output_audio
        ),
        "Output Color Space": output_color_space or "",
        "Output File Info": {
            "Full Flat Path": full_flat_path,
            "Base Path": base_path,
            "Subfolder Path": subfolder_path,
            "File Name": file_name,
            "File Template": file_name_template,
        },
        "Post-Render Action": post_render_action,
        "Preserve RGB": bool(om_ldat_data.preserve_rgb),
        "Resize Quality": ResizeQuality(om_ldat_data.resize_quality),
        "Resize to": [roou_chunk.width, roou_chunk.height],
        "Resize": bool(om_ldat_data.resize),
        "Starting #": roou_chunk.starting_number,
        "Use Comp Frame Number": bool(om_ldat_data.use_comp_frame_number),
        "Use Region of Interest": bool(om_ldat_data.use_region_of_interest),
        "Video Output": roou_chunk.video_output,
    }


def _build_file_template(
    folder_path: str,
    file_name_template: str,
    is_folder: bool,
) -> str:
    """Build the full output file template path from components.

    Combines the output folder path and file name template into a single
    path string, using the path separator found in the folder path.

    Args:
        folder_path: The output folder path from alas data.
        file_name_template: The file name template
            (e.g., ``[compName].[fileExtension]``).
        is_folder: Whether the alas path points to a folder.

    Returns:
        The complete file template path.
    """
    if not folder_path:
        return ""

    if not file_name_template:
        return folder_path

    if is_folder:
        # Get separator from path to keep consistency with Windows vs.
        # Mac paths in samples. The separator is not always the same
        # as os.path.sep since the AEP file can contain paths from a
        # different OS than the one running the parser.
        path_sep = "\\" if "\\" in folder_path else "/"
        cleaned_path = folder_path.rstrip(path_sep)
        return f"{cleaned_path}{path_sep}{file_name_template}"

    return folder_path


def parse_output_module(
    chunks: list[Aep.Chunk],
    om_ldat_data: Aep.OutputModuleSettingsLdatBody,
    project: Project,
    render_queue_item: RenderQueueItem,
) -> OutputModule:
    """
    Parse an output module from its chunk group.

    Each output module consists of:
    - Roou: Output options (binary data)
    - Ropt: Render options (binary data)
    - hdrm: HDR metadata
    - Utf8: HDR10 / color metadata JSON (e.g. ``{"colorMetadataPresent":true}``)
    - LIST Als2: Output file path info
      - alas: JSON with fullpath and target_is_folder
    - Utf8: Template/format name (e.g., "H.264 - Match Render Settings - 15 Mbps")
    - Utf8: File name template (e.g., "[compName].[fileextension]" or "output.mp4")

    Args:
        chunks: List of chunks belonging to this output module.
        om_ldat_data: Parsed OutputModuleSettingsLdatBody from LdatItem.

    Returns:
        OutputModule with parsed attributes.
    """
    roou_chunk = find_by_type(chunks=chunks, chunk_type="Roou")

    include_source_xmp = om_ldat_data.include_source_xmp
    post_render_action = PostRenderAction.from_binary(om_ldat_data.post_render_action)
    post_render_target_comp_id = om_ldat_data.post_render_target_comp_id or None
    if (
        post_render_action in (PostRenderAction.NONE, PostRenderAction.IMPORT)
        or post_render_target_comp_id is None
    ):
        post_render_target_comp = render_queue_item.comp
    else:
        post_render_target_comp = cast(
            CompItem, project.items[post_render_target_comp_id]
        )

    video_codec = roou_chunk.video_codec.strip("\x00") or None
    frame_rate = roou_chunk.frame_rate
    output_color_space = map_output_color_space(
        om_ldat_data.output_profile_id,
        om_ldat_data.output_color_space_working,
        project.working_space,
    )

    alas_data = parse_alas_data(chunks)
    folder_path = alas_data.get("fullpath", "")
    is_folder = alas_data.get("target_is_folder", False)

    utf8_chunks = filter_by_type(chunks, "Utf8")

    # Utf8[0] = HDR10 / color metadata JSON (e.g. '{"colorMetadataPresent":true}')
    # Utf8[1] = template/format name
    # Utf8[2] = file name template
    template_name = ""
    file_name_template = ""

    if len(utf8_chunks) > 1:
        template_name = str_contents(utf8_chunks[1])
    if len(utf8_chunks) > 2:
        file_name_template = str_contents(utf8_chunks[2])

    file_template = _build_file_template(folder_path, file_name_template, is_folder)

    settings = _parse_output_module_settings(
        roou_chunk,
        om_ldat_data,
        include_source_xmp,
        post_render_action,
        file_template,
        folder_path,
        file_name_template,
        output_color_space,
    )

    format_options = parse_format_options(chunks)

    return OutputModule(
        file_template=file_template,
        format_options=format_options,
        frame_rate=frame_rate,
        include_source_xmp=include_source_xmp,
        name=template_name,
        parent=render_queue_item,
        post_render_action=post_render_action,
        post_render_target_comp=post_render_target_comp,
        settings=settings,
        templates=[],  # Not available in binary format
        _video_codec=video_codec,
        _project_name=Path(project.file).stem if project.file else "Untitled Project",
        _project_color_depth=int(project.bits_per_channel),
    )
