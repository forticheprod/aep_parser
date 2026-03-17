from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, cast

from ..enums import (
    ColorDepthSetting,
    DiskCacheSetting,
    EffectsSetting,
    FieldRender,
    FrameBlendingSetting,
    FrameRateSetting,
    GuideLayers,
    LogType,
    MotionBlurSetting,
    ProxyUseSetting,
    PulldownSetting,
    RenderQuality,
    RQItemStatus,
    SoloSwitchesSetting,
    TimeSpanSource,
)
from ..kaitai import Aep
from ..kaitai.utils import (
    find_by_list_type,
    find_by_type,
    split_on_type,
)
from ..models.items.composition import CompItem
from ..models.renderqueue.render_queue import RenderQueue
from ..models.renderqueue.render_queue_item import RenderQueueItem
from ..models.settings import RenderSettings
from .output_module import parse_output_module
from .utils import parse_ldat_items

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
                item = parse_render_queue_item(
                    list_chunk=list_chunk,
                    lom_chunk=chunk,
                    ldat_body=render_settings_chunks[item_index],
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
    comment: str,
    project: Project,
) -> RenderQueueItem:
    """
    Parse a single render queue item from its component chunks.

    Args:
        list_chunk: The LIST 'list' chunk containing item metadata.
        lom_chunk: The LIST 'LOm ' chunk containing output modules.
        ldat_body: The RenderSettingsLdatBody chunk for this item.
        comment: The comment for the render queue item (from RCom chunk).
        project: The Project object being constructed, used to link comp
            references in render queue items.
    """
    om_ldat_items: list[Aep.OutputModuleSettingsLdatBody] = parse_ldat_items(list_chunk)

    # comp_id is stored in the render settings ldat
    comp_id = ldat_body.comp_id
    comp = cast(CompItem, project.items[comp_id])

    settings = _parse_render_settings(ldat_body, comp)

    elapsed_seconds: int = ldat_body.elapsed_seconds
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

    status = RQItemStatus.from_binary(ldat_body.status)

    render_queue_item = RenderQueueItem(
        comment=comment,
        comp=comp,
        elapsed_seconds=elapsed_seconds,
        log_type=log_type_val,
        name=template_name,
        output_modules=[],
        queue_item_notify=queue_item_notify,
        render=status != RQItemStatus.UNQUEUED,
        settings=settings,
        skip_frames=0,  # to be calculated after parsing output module settings
        start_time=start_time_val,
        status=status,
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
        comp: The composition being rendered, used to resolve time span.

    Returns:
        Dict with ExtendScript-compatible keys.
    """
    time_span = TimeSpanSource.from_binary(ldat_body.time_span_source)

    if time_span == TimeSpanSource.LENGTH_OF_COMP:
        ts_start = 0.0
        ts_duration = comp.duration
    elif time_span == TimeSpanSource.WORK_AREA_ONLY:
        ts_start = comp.work_area_start
        ts_duration = comp.work_area_duration
    else:
        ts_start = ldat_body.time_span_start
        ts_duration = ldat_body.time_span_duration

    return {
        "3:2 Pulldown": PulldownSetting(ldat_body.pulldown),
        "Color Depth": ColorDepthSetting.from_binary(ldat_body.color_depth),
        "Disk Cache": DiskCacheSetting.from_binary(ldat_body.disk_cache),
        "Effects": EffectsSetting.from_binary(ldat_body.effects),
        "Field Render": FieldRender(ldat_body.field_render),
        "Frame Blending": FrameBlendingSetting.from_binary(ldat_body.frame_blending),
        "Frame Rate": FrameRateSetting(ldat_body.use_this_frame_rate),
        "Guide Layers": GuideLayers.from_binary(ldat_body.guide_layers),
        "Motion Blur": MotionBlurSetting.from_binary(ldat_body.motion_blur),
        "Proxy Use": ProxyUseSetting.from_binary(ldat_body.proxy_use),
        "Quality": RenderQuality.from_binary(ldat_body.quality),
        "Resolution": [ldat_body.resolution_x, ldat_body.resolution_y],
        "Skip Existing Files": bool(ldat_body.skip_existing_files),
        "Solo Switches": SoloSwitchesSetting.from_binary(ldat_body.solo_switches),
        "Time Span Duration": ts_duration,
        "Time Span End": ts_start + ts_duration,
        "Time Span Start": ts_start,
        "Time Span": time_span,
        "Use comp's frame rate": comp.frame_rate,
        "Use this frame rate": ldat_body.frame_rate,
    }
