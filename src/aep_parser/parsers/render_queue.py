from __future__ import annotations

import os
import struct
import typing

from ..kaitai.utils import (
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.renderqueue.output_module import OutputModule
from ..models.renderqueue.output_module_settings import (
    AudioBitDepth,
    AudioChannels,
    OutputModuleSettings,
)
from ..models.renderqueue.render_queue import RenderQueue
from ..models.renderqueue.render_queue_item import RenderQueueItem
from ..models.renderqueue.render_settings import (
    ColorDepthSetting,
    EffectsSetting,
    FieldRender,
    FrameBlendingSetting,
    GuideLayers,
    MotionBlurSetting,
    ProxyUseSetting,
    Pulldown,
    RenderQuality,
    RenderSettings,
    SoloSwitchesSetting,
    TimeSpanSource,
)
from .utils import parse_alas_data, split_in_chunks

if typing.TYPE_CHECKING:
    from ..kaitai import Aep


def parse_render_queue(root_chunks: list[Aep.Chunk]) -> RenderQueue:
    """
    Parse the render queue from the top-level chunks.

    Args:
        root_chunks: The top-level chunks from the AEP file.
    """
    lrdr_chunk = find_by_list_type(chunks=root_chunks, list_type="LRdr")
    if lrdr_chunk is None:
        return RenderQueue(items=[])

    lrdr_child_chunks = lrdr_chunk.chunks

    # Parse global render settings from the first 'list' LIST directly under LRdr
    render_settings = _parse_global_render_settings(lrdr_child_chunks)

    # LItm chunk must be the RQItemCollection
    litm_chunk = find_by_list_type(chunks=lrdr_child_chunks, list_type="LItm")
    if litm_chunk is None:
        return RenderQueue(items=[], render_settings=render_settings)

    litm_child_chunks = litm_chunk.chunks

    items = []
    # Each render queue item is a pair: LIST 'list' + LIST 'LOm '
    # Parse items by iterating in pairs
    for list_chunk, lom_chunk in split_in_chunks(litm_child_chunks, 2):
        item = parse_render_queue_item(list_chunk, lom_chunk, render_settings)
        items.append(item)

    return RenderQueue(items=items, render_settings=render_settings)


def _parse_global_render_settings(
    lrdr_chunks: list[Aep.Chunk],
) -> RenderSettings | None:
    """Parse global render settings from the LRdr 'list' chunk.

    The render settings are stored in a LIST with list_type='list'
    directly under LRdr, containing lhd3 and ldat chunks.

    Args:
        lrdr_chunks: Child chunks of the LRdr LIST.

    Returns:
        RenderSettings if found, None otherwise.
    """
    # Find the 'list' LIST chunk (not LItm or LSIf)
    for chunk in lrdr_chunks:
        if chunk.chunk_type == "LIST" and chunk.data.list_type == "list":
            return _parse_render_settings_ldat(chunk.chunks)
    return None


def _parse_render_settings_ldat(
    list_chunks: list[Aep.Chunk],
) -> RenderSettings | None:
    """Parse RenderSettings from ldat chunk data.

    The ldat chunk is 2246 bytes and contains render settings at specific offsets.

    Args:
        list_chunks: Chunks from the LIST 'list' containing lhd3 and ldat.

    Returns:
        RenderSettings parsed from the ldat data.
    """
    ldat_chunk = find_by_type(chunks=list_chunks, chunk_type="ldat")
    if ldat_chunk is None:
        return None

    data = ldat_chunk._raw_data
    if len(data) < 2200:
        # Not the render settings ldat (might be item ldat at 128 bytes)
        return None

    # Parse fields from known offsets
    # Offset 44: frame_rate (u16)
    frame_rate = struct.unpack(">H", data[44:46])[0]

    # Offset 50: field_render (u16)
    field_render_val = struct.unpack(">H", data[50:52])[0]
    field_render = FieldRender(field_render_val) if field_render_val <= 2 else FieldRender.OFF

    # Offset 56: quality (u16)
    quality_val = struct.unpack(">H", data[56:58])[0]
    quality = RenderQuality(quality_val) if quality_val <= 2 else RenderQuality.BEST

    # Offset 58: resolution_x (u16)
    resolution_x = struct.unpack(">H", data[58:60])[0]

    # Offset 60: resolution_y (u16)
    resolution_y = struct.unpack(">H", data[60:62])[0]

    # Offset 64: effects (u16)
    effects_val = struct.unpack(">H", data[64:66])[0]
    effects = EffectsSetting(effects_val) if effects_val <= 2 else EffectsSetting.CURRENT_SETTINGS

    # Offset 68: proxy_use (u16)
    proxy_val = struct.unpack(">H", data[68:70])[0]
    proxy_use = ProxyUseSetting(proxy_val) if proxy_val in (0, 1, 3) else ProxyUseSetting.USE_NO_PROXIES

    # Offset 72: motion_blur (u16)
    motion_blur_val = struct.unpack(">H", data[72:74])[0]
    motion_blur = MotionBlurSetting(motion_blur_val) if motion_blur_val <= 2 else MotionBlurSetting.ON_FOR_CHECKED_LAYERS

    # Offset 76: frame_blending (u16)
    frame_blending_val = struct.unpack(">H", data[76:78])[0]
    frame_blending = FrameBlendingSetting(frame_blending_val) if frame_blending_val <= 2 else FrameBlendingSetting.ON_FOR_CHECKED_LAYERS

    # Offset 90: template_name (64-byte null-terminated string)
    template_name_bytes = data[90:154]
    null_idx = template_name_bytes.find(b"\x00")
    if null_idx >= 0:
        template_name_bytes = template_name_bytes[:null_idx]
    template_name = template_name_bytes.decode("ascii", errors="replace") if template_name_bytes else None

    # Offset 2144: use_this_frame_rate flag (u16)
    use_frame_rate_val = struct.unpack(">H", data[2144:2146])[0]
    use_this_frame_rate = use_frame_rate_val == 1

    # Offset 2148: time_span_source (u16) - high byte
    time_span_val = struct.unpack(">H", data[2148:2150])[0]
    if time_span_val == 0:
        time_span_source = TimeSpanSource.LENGTH_OF_COMP
    elif time_span_val == 1:
        time_span_source = TimeSpanSource.WORK_AREA_ONLY
    elif time_span_val == 2:
        time_span_source = TimeSpanSource.CUSTOM
    else:
        time_span_source = TimeSpanSource.WORK_AREA_ONLY

    # Offset 2164: solo_switches (u16)
    solo_val = struct.unpack(">H", data[2164:2166])[0]
    solo_switches = SoloSwitchesSetting(solo_val) if solo_val in (0, 2) else SoloSwitchesSetting.CURRENT_SETTINGS

    # Offset 2172: guide_layers (u16)
    guide_val = struct.unpack(">H", data[2172:2174])[0]
    guide_layers = GuideLayers(guide_val) if guide_val in (0, 2) else GuideLayers.ALL_OFF

    # Offset 2180: color_depth (u16)
    color_depth_val = struct.unpack(">H", data[2180:2182])[0]
    if color_depth_val == 0xFFFF:
        color_depth = ColorDepthSetting.CURRENT_SETTINGS
    elif color_depth_val == 0:
        color_depth = ColorDepthSetting.EIGHT_BITS_PER_CHANNEL
    elif color_depth_val == 1:
        color_depth = ColorDepthSetting.SIXTEEN_BITS_PER_CHANNEL
    elif color_depth_val == 2:
        color_depth = ColorDepthSetting.THIRTY_TWO_BITS_PER_CHANNEL
    else:
        color_depth = ColorDepthSetting.CURRENT_SETTINGS

    return RenderSettings(
        template_name=template_name if template_name else None,
        quality=quality,
        resolution_x=resolution_x,
        resolution_y=resolution_y,
        field_render=field_render,
        pulldown=Pulldown.OFF,  # TODO: Parse pulldown
        motion_blur=motion_blur,
        frame_blending=frame_blending,
        effects=effects,
        proxy_use=proxy_use,
        solo_switches=solo_switches,
        guide_layers=guide_layers,
        color_depth=color_depth,
        time_span_source=time_span_source,
        frame_rate=float(frame_rate),
        use_this_frame_rate=use_this_frame_rate,
    )


def parse_render_queue_item(
    list_chunk: Aep.Chunk | None,
    lom_chunk: Aep.Chunk | None,
    render_settings: RenderSettings | None = None,
) -> RenderQueueItem:
    """
    Parse a single render queue item from its component chunks.

    Args:
        list_chunk: The LIST 'list' chunk containing item metadata.
        lom_chunk: The LIST 'LOm ' chunk containing output modules.
        render_settings: Global render settings to attach to the item.
    """

    # TODO: Parse item metadata from list_chunk (lhd3, ldat)
    # This would include comp_id, status, etc.

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

    output_modules = []
    for group in om_groups:
        output_module = parse_output_module(group)
        output_modules.append(output_module)

    return RenderQueueItem(
        output_modules=output_modules,
        render_settings=render_settings,
    )


def _parse_output_module_settings(roou_data: Aep.RoouBody) -> OutputModuleSettings:
    """Parse OutputModuleSettings from Roou chunk data.

    The Roou chunk is 154 bytes and contains output module settings.

    Args:
        roou_data: Parsed RoouBody from the Roou chunk.

    Returns:
        OutputModuleSettings parsed from the data.
    """
    video_codec = roou_data.video_codec.strip("\x00")

    # Parse audio bit depth
    if roou_data.audio_bit_depth == 1:
        audio_bit_depth = AudioBitDepth.EIGHT_BIT
    elif roou_data.audio_bit_depth == 3:
        audio_bit_depth = AudioBitDepth.TWENTY_FOUR_BIT
    elif roou_data.audio_bit_depth == 4:
        audio_bit_depth = AudioBitDepth.THIRTY_TWO_BIT
    else:
        audio_bit_depth = AudioBitDepth.SIXTEEN_BIT

    # Parse audio channels
    audio_channels_val = roou_data.audio_channels
    audio_channels = (
        AudioChannels(audio_channels_val)
        if audio_channels_val in (1, 2)
        else AudioChannels.STEREO
    )

    return OutputModuleSettings(
        video_codec=video_codec if video_codec else None,
        has_video=True,  # TODO: Determine video enable flag
        has_audio=roou_data.has_audio,
        width=roou_data.width,
        height=roou_data.height,
        frame_rate=float(roou_data.frame_rate),
        color_premultiplied=roou_data.color_premultiplied == 1,
        color_matted=roou_data.color_matted == 1,
        audio_bit_depth=audio_bit_depth,
        audio_channels=audio_channels,
    )


def parse_output_module(chunks: list[Aep.Chunk]) -> OutputModule:
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

    Returns:
        OutputModule with parsed attributes.
    """
    # Parse output module settings from Roou chunk
    roou_chunk = find_by_type(chunks=chunks, chunk_type="Roou")
    om_settings = None
    if roou_chunk is not None:
        om_settings = _parse_output_module_settings(roou_chunk.data)

    # Get output file from LIST Als2 > alas
    file_path = None
    alas_data = parse_alas_data(chunks)
    folder_path = alas_data.get("fullpath")
    is_folder = alas_data.get("target_is_folder", False)

    # Get Utf8 chunks for template/format name and file name
    utf8_chunks = [c for c in chunks if c.chunk_type == "Utf8"]

    # Utf8[0] = settings JSON (usually "{}")
    # Utf8[1] = template/format name
    # Utf8[2] = file name template
    template_name = None
    file_name_template = None

    if len(utf8_chunks) >= 2:
        template_name = str_contents(utf8_chunks[1])
    if len(utf8_chunks) >= 3:
        file_name_template = str_contents(utf8_chunks[2])

    # Construct full file path
    if folder_path and file_name_template:
        if is_folder:
            # Combine folder path with filename
            file_path = os.path.join(folder_path, file_name_template)
        else:
            # fullpath already contains the file
            file_path = folder_path
    elif folder_path:
        file_path = folder_path

    return OutputModule(
        file_template=file_path,
        name=template_name,
        templates=[],  # Not available in binary format
        settings={},  # Deprecated, use om_settings
        om_settings=om_settings,
    )
