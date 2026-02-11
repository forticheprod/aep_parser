from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from ..kaitai import Aep
from ..kaitai.utils import (
    find_by_list_type,
    find_by_type,
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
from .utils import parse_alas_data, parse_ldat_items

if TYPE_CHECKING:
    from ..models.project import Project


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

    # Get item count from lhd3 header
    settings_lhd3 = find_by_type(chunks=list_settings_chunk.chunks, chunk_type="lhd3")
    num_items = settings_lhd3.count
    if num_items == 0:
        return []

    render_settings_chunks: list[Aep.RenderSettingsLdatBody] = parse_ldat_items(
        list_settings_chunk
    )

    # Parse Rout chunk for per-item render flags
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
    # Parse output module data from ldat
    om_ldat_items: list[Aep.OutputModuleSettingsLdatBody] = parse_ldat_items(list_chunk)

    # comp_id is stored in the render settings ldat
    comp_id = ldat_body.comp_id
    comp = cast(CompItem, project.items[comp_id])

    settings = _parse_render_settings(ldat_body, comp)

    lom_child_chunks = lom_chunk.chunks

    # Group chunks by Roou - each Roou starts a new output module
    om_groups: list[list[Aep.Chunk]] = []
    current_group: list[Aep.Chunk] = []

    for chunk in lom_child_chunks:
        if chunk.chunk_type == "Roou" and current_group:
            om_groups.append(current_group)
            current_group = []
        current_group.append(chunk)
    if current_group:
        om_groups.append(current_group)

    render_queue_item = RenderQueueItem(
        comment=comment,
        comp=comp,
        output_modules=[],
        render=render_enabled,
        settings=settings,
        skip_frames=0,  # to be calculated after parsing output module settings
        status=RQItemStatus.from_binary(ldat_body.status),
    )

    output_modules = []
    for om_index, group in enumerate(om_groups):
        output_module = parse_output_module(group, om_ldat_items[om_index], project, render_queue_item)
        # Set project-level data for template resolution
        output_module._project_name = Path(project.file).stem if project.file else None
        output_module._project_color_depth = int(project.bits_per_channel)
        output_modules.append(output_module)

    # Calculate skip_frames from frame rate ratio
    # skip_frames = (comp_frame_rate / output_frame_rate) - 1
    # e.g., 24 fps comp with 6 fps output = skip_frames of 3 (render every 4th frame)
    output_frame_rate = output_modules[0].settings.get("Frame Rate", 0)
    if output_frame_rate and output_frame_rate > 0:
        render_queue_item.skip_frames = round(comp.frame_rate / output_frame_rate) - 1

    render_queue_item.output_modules = output_modules

    return render_queue_item


def _parse_render_settings(
    ldat_body: Aep.RenderSettingsLdatBody, comp: CompItem
) -> dict[str, Any]:
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
        "Elapsed Seconds": ldat_body.elapsed_seconds,
        "Field Render": ldat_body.field_render,
        "Frame Blending": FrameBlendingSetting.from_binary(ldat_body.frame_blending),
        "Frame Rate": bool(ldat_body.use_this_frame_rate),
        "Guide Layers": GuideLayers.from_binary(ldat_body.guide_layers),
        "Log Type": LogType.from_binary(ldat_body.log_type),
        "Motion Blur": MotionBlurSetting.from_binary(ldat_body.motion_blur),
        "Proxy Use": ProxyUseSetting.from_binary(ldat_body.proxy_use),
        "Quality": RenderQuality.from_binary(ldat_body.quality),
        "Queue Item Notify": ldat_body.queue_item_notify,
        "Resolution": [ldat_body.resolution_x, ldat_body.resolution_y],
        "Skip Existing Files": bool(ldat_body.skip_existing_files),
        "Solo Switches": SoloSwitchesSetting.from_binary(ldat_body.solo_switches),
        "Start Time:": ldat_body.start_time,
        "Template Name": ldat_body.template_name.rstrip("\x00"),
        "Time Span Duration Frames": ldat_body.time_span_duration_frames,
        "Time Span Duration": ldat_body.time_span_duration,
        "Time Span End Frames": ldat_body.time_span_start_frames
        + ldat_body.time_span_duration_frames,
        "Time Span End": ldat_body.time_span_start + ldat_body.time_span_duration,
        "Time Span Start Frames": ldat_body.time_span_start_frames,
        "Time Span Start": ldat_body.time_span_start,
        "Time Span": TimeSpanSource.from_binary(ldat_body.time_span_source),
        "Use comp's frame rate": comp.frame_rate,
        "Use this frame rate": ldat_body.frame_rate,
    }


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
    # Parse crop, include_source_xmp, post_render_action, and post_render_target_comp_id
    # from per-output-module ldat
    crop = om_ldat_data.crop
    include_source_xmp = om_ldat_data.include_source_xmp
    post_render_action = PostRenderAction.from_binary(om_ldat_data.post_render_action)
    post_render_target_comp_id = om_ldat_data.post_render_target_comp_id or None
    if post_render_target_comp_id is None:
        post_render_target_comp = render_queue_item.comp
    else:
        post_render_target_comp = cast(CompItem, project.items[post_render_target_comp_id])

    # Parse output module settings from Roou chunk
    roou_chunk = find_by_type(chunks=chunks, chunk_type="Roou")

    settings = _parse_output_module_settings(roou_chunk)

    # Add crop values to settings from ldat
    settings["Crop Top"] = om_ldat_data.crop_top
    settings["Crop Left"] = om_ldat_data.crop_left
    settings["Crop Bottom"] = om_ldat_data.crop_bottom
    settings["Crop Right"] = om_ldat_data.crop_right

    # Get output file from LIST Als2 > alas
    alas_data = parse_alas_data(chunks)
    folder_path = alas_data.get("fullpath")
    is_folder = alas_data.get("target_is_folder", False)

    # Get Utf8 chunks for template/format name and file name
    utf8_chunks = [c for c in chunks if c.chunk_type == "Utf8"]

    # Utf8[0] = ??
    # Utf8[1] = template/format name
    # Utf8[2] = file name template
    template_name = None
    file_name_template = None

    if len(utf8_chunks) >= 2:
        template_name = str_contents(utf8_chunks[1])
    if len(utf8_chunks) >= 3:
        file_name_template = str_contents(utf8_chunks[2])

    # Construct full file template
    file_template = None
    if folder_path:
        if file_name_template:
            if is_folder:
                # Get separator from path to keep consistency with Windows vs.
                # Mac paths in samples. The separator is not always the same
                # as os.path.sep since the AEP file can contain paths from a
                # different OS than the one running the parser.
                path_sep = "\\" if "\\" in folder_path else "/"
                cleaned_path = folder_path.rstrip(path_sep)
                file_template = f"{cleaned_path}{path_sep}{file_name_template}"
            else:
                file_template = folder_path
        else:
            file_template = folder_path

    return OutputModule(
        crop=crop,
        file_template=file_template,
        include_source_xmp=include_source_xmp,
        name=template_name,
        parent=render_queue_item,
        post_render_action=post_render_action,
        post_render_target_comp=post_render_target_comp,
        settings=settings,
        templates=[],  # Not available in binary format
    )


def _parse_output_module_settings(roou_chunk: Aep.Chunk) -> dict[str, Any]:
    """Parse output module settings from Roou chunk data.

    The Roou chunk is 154 bytes and contains output module settings.
    Returns a dict with ExtendScript-compatible keys.

    Args:
        roou_chunk: The Roou chunk.

    Returns:
        Dict with ExtendScript keys like "Video Output", "Audio Bit Depth", etc.
    """
    video_codec = roou_chunk.video_codec.strip("\x00") or None
    audio_bit_depth = AudioBitDepth.from_binary(roou_chunk.audio_bit_depth)

    audio_channels = AudioChannels.from_binary(roou_chunk.audio_channels)
    color = OutputColorMode(roou_chunk.color_premultiplied)

    return {
        "Video Codec": video_codec,
        "Video Output": roou_chunk.video_output,
        "Output Audio": roou_chunk.output_audio,
        "Width": roou_chunk.width,
        "Height": roou_chunk.height,
        "Color": color,
        "Audio Bit Depth": audio_bit_depth,
        "Audio Channels": audio_channels,
        "Frame Rate": roou_chunk.frame_rate,
    }
