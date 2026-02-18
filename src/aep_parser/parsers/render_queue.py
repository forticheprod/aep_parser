from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from ..kaitai import Aep
from ..kaitai.utils import (
    filter_by_type,
    find_by_list_type,
    find_by_type,
    split_on_type,
    str_contents,
)
from ..models.enums import (
    AudioBitDepth,
    AudioChannels,
    ColorDepthSetting,
    DiskCacheSetting,
    EffectsSetting,
    FrameBlendingSetting,
    GuideLayers,
    LogType,
    MotionBlurSetting,
    OutputChannels,
    OutputColorMode,
    PostRenderAction,
    ProxyUseSetting,
    RenderQuality,
    RQItemStatus,
    SoloSwitchesSetting,
    TimeSpanSource,
)
from ..models.items.composition import CompItem
from ..models.renderqueue.output_module import OutputModule
from ..models.renderqueue.render_queue import RenderQueue
from ..models.renderqueue.render_queue_item import RenderQueueItem
from ..models.settings import OutputModuleSettings, RenderSettings
from .mappings import map_output_format
from .utils import parse_alas_data, parse_ldat_items

if TYPE_CHECKING:
    from ..models.project import Project

AEP_EPOCH = datetime(1904, 1, 1)  # Mac HFS+ epoch Jan 1, 1904


def parse_render_queue(root_chunks: list[Aep.Chunk], project: Project) -> RenderQueue:
    """
    Parse the render queue from the top-level chunks.

    Args:
        root_chunks: The top-level chunks from the AEP file.
        project: The Project object being constructed, used to link comp
            references in render queue items.
    """
    lrdr_chunk = find_by_list_type(chunks=root_chunks, list_type="LRdr")
    lrdr_child_chunks = lrdr_chunk.chunks
    items = parse_render_queue_items(lrdr_child_chunks, project)
    return RenderQueue(items=items)


def parse_render_queue_items(
    lrdr_child_chunks: list[Aep.Chunk], project: Project
) -> list[RenderQueueItem]:
    """
    Parse render queue items from the child chunks of LRdr.

    The render queue items are stored in a LIST 'list' chunk directly under LRdr.
    Each item consists of:
    - An optional RCom chunk with the item comment
    - A LIST 'list' chunk with item metadata and settings
    - A LIST 'LOm ' chunk with output module info
    - A RenderSettingsLdatBody chunk with the render settings for the item
    - A Rout chunk with per-item render flags

    Args:
        lrdr_child_chunks: The child chunks of the LRdr chunk.
        project: The Project object being constructed, used to link comp
            references in render queue items.
    """
    # Parse render settings from the LIST 'list' directly under LRdr
    # This ldat contains N × item_size bytes, one block per render queue item
    list_settings_chunk = find_by_list_type(chunks=lrdr_child_chunks, list_type="list")

    settings_lhd3 = find_by_type(chunks=list_settings_chunk.chunks, chunk_type="lhd3")
    num_items = settings_lhd3.count
    if num_items == 0:
        return []

    render_settings_chunks: list[Aep.RenderSettingsLdatBody] = parse_ldat_items(
        list_settings_chunk
    )

    rout_chunk = find_by_type(chunks=lrdr_child_chunks, chunk_type="Rout")
    rout_items = rout_chunk.items

    # LItm chunk is probably the RQItemCollection.
    litm_chunk = find_by_list_type(chunks=lrdr_child_chunks, list_type="LItm")

    # Structure: [RCom] + LIST 'list' + LIST 'LOm ' per item
    # RCom is optional and contains the item comment
    items = []
    item_index = 0
    comment = ""
    list_chunk = None

    for chunk in litm_chunk.chunks:
        if chunk.chunk_type == "RCom":
            comment = chunk.chunk.contents
        elif chunk.chunk_type == "LIST":
            list_type = chunk.list_type
            if list_type == "list":
                list_chunk = chunk
            elif list_type == "LOm " and list_chunk is not None:
                # We have both list_chunk and lom_chunk, parse the item
                render_enabled = rout_items[item_index].render
                item = parse_render_queue_item(
                    list_chunk=list_chunk,
                    lom_chunk=chunk,
                    ldat_body=render_settings_chunks[item_index],
                    render_enabled=render_enabled,
                    comment=comment,
                    project=project,
                )
                items.append(item)
                item_index += 1
                comment = ""
                list_chunk = None

    return items


def parse_render_queue_item(
    list_chunk: Aep.Chunk,
    lom_chunk: Aep.Chunk,
    ldat_body: Aep.RenderSettingsLdatBody,
    render_enabled: bool,
    comment: str,
    project: Project,
) -> RenderQueueItem:
    """
    Parse a single render queue item from its component chunks.

    Args:
        list_chunk: The LIST 'list' chunk containing item metadata.
        lom_chunk: The LIST 'LOm ' chunk containing output modules.
        ldat_body: The RenderSettingsLdatBody chunk for this item.
        render_enabled: Whether the item is set to render when queue starts.
        comment: The comment for the render queue item (from RCom chunk).
        project: The Project object being constructed, used to link comp
            references in render queue items.
    """
    om_ldat_items: list[Aep.OutputModuleSettingsLdatBody] = parse_ldat_items(list_chunk)

    # comp_id is stored in the render settings ldat
    comp_id = ldat_body.comp_id
    comp = cast(CompItem, project.items[comp_id])

    settings = _parse_render_settings(ldat_body, comp)

    elapsed_seconds: int | None = (
        ldat_body.elapsed_seconds if ldat_body.elapsed_seconds else None
    )
    log_type_val = LogType.from_binary(ldat_body.log_type)
    queue_item_notify = ldat_body.queue_item_notify
    template_name = ldat_body.template_name.rstrip("\x00")
    time_span_start_frames = ldat_body.time_span_start_frames
    time_span_duration_frames = ldat_body.time_span_duration_frames

    # Parse start_time from Mac HFS+ epoch
    start_time_val: datetime | None = None
    if ldat_body.start_time:
        start_time_val = AEP_EPOCH + timedelta(seconds=ldat_body.start_time)

    lom_child_chunks = lom_chunk.chunks

    # Group chunks by Roou - each Roou starts a new output module
    om_groups = split_on_type(lom_child_chunks, "Roou")

    render_queue_item = RenderQueueItem(
        comment=comment,
        comp=comp,
        elapsed_seconds=elapsed_seconds,
        log_type=log_type_val,
        name=template_name,
        output_modules=[],
        queue_item_notify=queue_item_notify,
        render=render_enabled,
        settings=settings,
        skip_frames=0,  # to be calculated after parsing output module settings
        start_time=start_time_val,
        status=RQItemStatus.from_binary(ldat_body.status),
        time_span_duration_frames=time_span_duration_frames,
        time_span_start_frames=time_span_start_frames,
    )

    output_modules = []
    for om_index, group in enumerate(om_groups):
        output_module = parse_output_module(
            group, om_ldat_items[om_index], project, render_queue_item
        )
        output_modules.append(output_module)

    # Calculate skip_frames from frame rate ratio
    # skip_frames = (comp_frame_rate / output_frame_rate) - 1
    # e.g., 24 fps comp with 6 fps output = skip_frames of 3 (render every 4th frame)
    output_frame_rate = output_modules[0].frame_rate
    if output_frame_rate and output_frame_rate > 0:
        render_queue_item.skip_frames = round(comp.frame_rate / output_frame_rate) - 1

    render_queue_item.output_modules = output_modules

    return render_queue_item


def _parse_render_settings(
    ldat_body: Aep.RenderSettingsLdatBody, comp: CompItem
) -> RenderSettings:
    """Parse render settings from LdatItem.

    Returns a dict with ExtendScript-compatible keys matching getSettings() output.

    Args:
        ldat_body: The parsed RenderSettingsLdatBody from LdatItem.

    Returns:
        Dict with ExtendScript-compatible keys.
    """

    return {
        "3:2 Pulldown": ldat_body.pulldown,
        "Color Depth": ColorDepthSetting.from_binary(ldat_body.color_depth),
        "Disk Cache": DiskCacheSetting.from_binary(ldat_body.disk_cache),
        "Effects": EffectsSetting.from_binary(ldat_body.effects),
        "Field Render": ldat_body.field_render,
        "Frame Blending": FrameBlendingSetting.from_binary(ldat_body.frame_blending),
        "Frame Rate": bool(ldat_body.use_this_frame_rate),
        "Guide Layers": GuideLayers.from_binary(ldat_body.guide_layers),
        "Motion Blur": MotionBlurSetting.from_binary(ldat_body.motion_blur),
        "Proxy Use": ProxyUseSetting.from_binary(ldat_body.proxy_use),
        "Quality": RenderQuality.from_binary(ldat_body.quality),
        "Resolution": [ldat_body.resolution_x, ldat_body.resolution_y],
        "Skip Existing Files": bool(ldat_body.skip_existing_files),
        "Solo Switches": SoloSwitchesSetting.from_binary(ldat_body.solo_switches),
        "Time Span Duration": ldat_body.time_span_duration,
        "Time Span End": ldat_body.time_span_end,
        "Time Span Start": ldat_body.time_span_start,
        "Time Span": TimeSpanSource.from_binary(ldat_body.time_span_source),
        "Use comp's frame rate": comp.frame_rate,
        "Use this frame rate": ldat_body.frame_rate,
    }


def _parse_output_module_settings(
    roou_chunk: Aep.Chunk,
    om_ldat_data: Aep.OutputModuleSettingsLdatBody,
    include_source_xmp: bool,
    post_render_action: PostRenderAction,
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

    Returns:
        Dict with ExtendScript keys like "Video Output", "Audio Bit Depth",
        "Crop", "Channels", etc.
    """
    audio_bit_depth = AudioBitDepth.from_binary(roou_chunk.audio_bit_depth)
    audio_channels = AudioChannels.from_binary(roou_chunk.audio_channels)
    color = OutputColorMode(roou_chunk.color_premultiplied)

    return {
        "Audio Bit Depth": audio_bit_depth,
        "Audio Channels": audio_channels,
        "Audio Sample Rate": int(roou_chunk.audio_sample_rate),
        "Channels": OutputChannels(om_ldat_data.channels),
        "Color": color,
        "Crop Bottom": om_ldat_data.crop_bottom,
        "Crop Left": om_ldat_data.crop_left,
        "Crop Right": om_ldat_data.crop_right,
        "Crop Top": om_ldat_data.crop_top,
        "Crop": om_ldat_data.crop,
        "Depth": roou_chunk.depth,
        "Format": map_output_format(roou_chunk.format_id),
        "Include Project Link": bool(om_ldat_data.include_project_link),
        "Include Source XMP Metadata": include_source_xmp,
        "Lock Aspect Ratio": bool(om_ldat_data.lock_aspect_ratio),
        "Output Audio": roou_chunk.output_audio,
        "Post-Render Action": post_render_action,
        "Resize Quality": om_ldat_data.resize_quality,
        "Resize": bool(om_ldat_data.resize),
        "Starting #": roou_chunk.starting_number,
        "Use Comp Frame Number": om_ldat_data.use_comp_frame_number,
        "Use Region of Interest": om_ldat_data.use_region_of_interest,
        "Video Output": roou_chunk.video_output,
    }


def _build_file_template(
    folder_path: str | None,
    file_name_template: str | None,
    is_folder: bool,
) -> str | None:
    """Build the full output file template path from components.

    Combines the output folder path and file name template into a single
    path string, using the path separator found in the folder path.

    Args:
        folder_path: The output folder path from alas data.
        file_name_template: The file name template
            (e.g., ``[compName].[fileExtension]``).
        is_folder: Whether the alas path points to a folder.

    Returns:
        The complete file template path, or None if no folder path.
    """
    if not folder_path:
        return None

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
    - Utf8: Template settings JSON (usually "{}")
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
    # Parse include_source_xmp, post_render_action, and post_render_target_comp_id
    # from per-output-module ldat
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

    roou_chunk = find_by_type(chunks=chunks, chunk_type="Roou")
    settings = _parse_output_module_settings(
        roou_chunk, om_ldat_data, include_source_xmp, post_render_action
    )

    video_codec = roou_chunk.video_codec.strip("\x00") or None

    width = roou_chunk.width
    height = roou_chunk.height
    frame_rate = roou_chunk.frame_rate

    alas_data = parse_alas_data(chunks)
    folder_path = alas_data.get("fullpath")
    is_folder = alas_data.get("target_is_folder", False)

    utf8_chunks = filter_by_type(chunks, "Utf8")

    # Utf8[0] = ??
    # Utf8[1] = template/format name
    # Utf8[2] = file name template
    template_name = None
    file_name_template = None

    if len(utf8_chunks) >= 2:
        template_name = str_contents(utf8_chunks[1])
    if len(utf8_chunks) >= 3:
        file_name_template = str_contents(utf8_chunks[2])

    file_template = _build_file_template(folder_path, file_name_template, is_folder)

    return OutputModule(
        file_template=file_template,
        frame_rate=frame_rate,
        height=height,
        include_source_xmp=include_source_xmp,
        name=template_name,
        parent=render_queue_item,
        post_render_action=post_render_action,
        post_render_target_comp=post_render_target_comp,
        settings=settings,
        templates=[],  # Not available in binary format
        width=width,
        _video_codec=video_codec,
        _project_name=Path(project.file).stem if project.file else "Untitled Project",
        _project_color_depth=int(project.bits_per_channel),

    )

