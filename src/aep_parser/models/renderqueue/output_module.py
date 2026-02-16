from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..enums import OutputChannels, OutputColorDepth, PostRenderAction

if TYPE_CHECKING:
    from ..items.composition import CompItem
    from .render_queue_item import RenderQueueItem

_TEMPLATE_EXTENSIONS: dict[str, str] = {
    "H.264": "mp4",
    "H.264 - Match Render Settings - 15 Mbps": "mp4",
    "H.264 - Match Render Settings - 40 Mbps": "mp4",
    "H.264 - Match Render Settings - 50 Mbps": "mp4",
    "Lossless": "avi",
    "Lossless with Alpha": "avi",
    "AIFF 48kHz": "aif",
    "Apple ProRes 422": "mov",
    "Apple ProRes 422 HQ": "mov",
    "Apple ProRes 422 LT": "mov",
    "Apple ProRes 422 Proxy": "mov",
    "Apple ProRes 4444": "mov",
    "Multi-Machine Sequence": "psd",
}

_FIELD_ORDER_NAMES: dict[int, str] = {
    0: "Both",  # Off/Progressive - renders both fields
    1: "UFF",  # Upper field first
    2: "LFF",  # Lower field first
}

_PULLDOWN_PHASE_NAMES: dict[int, str] = {
    0: "",
    1: "WSSWW",
    2: "SSWWW",
    3: "SWWWS",
    4: "WWWSS",
    5: "WWSSW",
}

_OUTPUT_CHANNELS_NAMES: dict[OutputChannels, str] = {
    OutputChannels.RGB: "RGB",
    OutputChannels.RGBA: "RGBA",
    OutputChannels.ALPHA: "Alpha",
}

_OUTPUT_COLOR_DEPTH_NAMES: dict[OutputColorDepth, str] = {
    OutputColorDepth.MILLIONS_OF_COLORS: "Millions",
    OutputColorDepth.TRILLIONS_OF_COLORS: "Trillions",
    OutputColorDepth.FLOATING_POINT: "Float",
}

_PROJECT_COLOR_DEPTH_NAMES: dict[int, str] = {
    8: "8bit",
    16: "16bit",
    32: "32bit",
}

# Mapping of video codec FourCC codes to friendly names
_VIDEO_CODEC_NAMES: dict[str, str] = {
    "CTXF": "H.264",
    "FXTC": "H.264",
    "avc1": "H.264",
    "ap4h": "ProRes 4444",
    "apch": "ProRes 422 HQ",
    "apcn": "ProRes 422",
    "apcs": "ProRes 422 LT",
    "apco": "ProRes 422 Proxy",
}


def _calculate_aspect_ratio(width: int, height: int) -> str:
    """Calculate simplified aspect ratio string (e.g., '16x9').

    Args:
        width: Frame width in pixels.
        height: Frame height in pixels.

    Returns:
        Aspect ratio string like '16x9', '4x3', etc.
    """
    gcd = math.gcd(width, height)
    return f"{width // gcd}x{height // gcd}"


def _format_frame_number(frame: int, fps: float) -> str:
    """Format frame number in After Effects feet+frames format.

    AE uses a feet+frames format where each foot is 16 frames (like 35mm film).
    Format is FFFF+RR where FFFF is feet and RR is remaining frames.

    Args:
        frame: Frame number (0-based).
        fps: Frames per second (not used in this format).

    Returns:
        Formatted frame string like '0045+00' (45 feet, 0 frames).
    """
    frames_per_foot = 16  # Standard 35mm film: 16 frames per foot
    feet = frame // frames_per_foot
    remaining_frames = frame % frames_per_foot
    return f"{feet:04d}+{remaining_frames:02d}"


def _format_timecode(
    seconds: float, fps: float, drop_frame: bool = False, is_duration: bool = False
) -> str:
    """Format time as timecode string with dashes.

    Args:
        seconds: Time in seconds.
        fps: Frames per second.
        drop_frame: Whether to use drop-frame timecode (not implemented).
        is_duration: If True, uses ceiling for frame calculation (for durations).
                    If False, uses floor (for absolute times).

    Returns:
        Timecode string like '0-00-00-00' (hours-minutes-seconds-frames).
    """
    fps_int = int(fps) if fps else 1
    # Use ceiling for durations, floor for absolute times
    if is_duration:
        total_frames = math.ceil(seconds * fps_int)
    else:
        total_frames = int(seconds * fps_int)

    frames = total_frames % fps_int
    total_seconds = total_frames // fps_int
    secs = total_seconds % 60
    total_minutes = total_seconds // 60
    mins = total_minutes % 60
    hours = total_minutes // 60

    return f"{hours}-{mins:02d}-{secs:02d}-{frames:02d}"


def resolve_output_filename(
    file_template: str | None,
    project_name: str | None = None,
    comp_name: str | None = None,
    render_settings_name: str | None = None,
    output_module_name: str | None = None,
    width: int | None = None,
    height: int | None = None,
    frame_rate: float | None = None,
    start_frame: int | None = None,
    end_frame: int | None = None,
    duration_frames: int | None = None,
    start_time: float | None = None,
    end_time: float | None = None,
    duration_time: float | None = None,
    channels: OutputChannels | None = None,
    project_color_depth: int | None = None,
    output_color_depth: OutputColorDepth | None = None,
    compressor: str | None = None,
    field_render: int | None = None,
    pulldown_phase: int | None = None,
    file_extension: str | None = None,
) -> str | None:
    """Resolve an After Effects output filename template to the actual filename.

    After Effects stores output paths with template variables like `[compName]`
    and `[fileExtension]`. This function resolves those variables to produce
    the actual filename that would be rendered.

    Args:
        file_template: The file path containing template variables.
            e.g., `C:/Output/[compName].[fileExtension]`
        project_name: The project name (without .aep extension) for `[projectName]`.
        comp_name: The composition name for `[compName]`.
        render_settings_name: The render settings template name for `[renderSettingsName]`.
        output_module_name: The output module name for `[outputModuleName]`.
        width: The composition width for `[width]`.
        height: The composition height for `[height]`.
        frame_rate: The frame rate for `[frameRate]` and timecodes.
        start_frame: The start frame for `[startFrame]}` (feet+frames format).
        end_frame: The end frame for `[endFrame]` (feet+frames format).
        duration_frames: The duration in frames for `[durationFrames]` (feet+frames format).
        start_time: The start time in seconds for `[startTimecode]}` (uses floor).
        end_time: The end time in seconds for `[endTimecode]` (uses floor).
        duration_time: The duration in seconds for `[durationTimecode]` (uses ceiling).
        channels: The output channels setting for `[channels]`.
        project_color_depth: The project bits per channel (8/16/32) for `[projectColorDepth]`.
        output_color_depth: The output color depth for `[outputColorDepth]`.
        compressor: The video codec/compressor name for `[compressor]`.
        field_render: The field render setting for `[fieldOrder]`.
        pulldown_phase: The 3:2 pulldown phase for `[pulldownPhase]`.
        file_extension: The file extension for `[fileExtension]`.

    Returns:
        The resolved file path, or None if file_template is None.
    """
    if file_template is None:
        return None

    result = file_template

    # Project name
    if project_name is not None:
        result = re.sub(r"\[projectName\]", project_name, result, flags=re.IGNORECASE)

    # Comp name
    if comp_name is not None:
        result = re.sub(r"\[compName\]", comp_name, result, flags=re.IGNORECASE)

    # Render settings name
    if render_settings_name is not None:
        result = re.sub(
            r"\[renderSettingsName\]",
            render_settings_name,
            result,
            flags=re.IGNORECASE,
        )

    # Output module name
    if output_module_name is not None:
        result = re.sub(
            r"\[outputModuleName\]",
            output_module_name,
            result,
            flags=re.IGNORECASE,
        )

    # Dimensions
    if width is not None:
        result = re.sub(r"\[width\]", str(width), result, flags=re.IGNORECASE)

    if height is not None:
        result = re.sub(r"\[height\]", str(height), result, flags=re.IGNORECASE)

    # Frame rate - display as integer if whole number, otherwise with decimals
    if frame_rate is not None:
        if frame_rate == int(frame_rate):
            frame_rate_str = str(int(frame_rate))
        else:
            frame_rate_str = str(frame_rate)
        result = re.sub(r"\[frameRate\]", frame_rate_str, result, flags=re.IGNORECASE)

    # Aspect ratio (computed from width and height)
    if width is not None and height is not None:
        aspect_ratio = _calculate_aspect_ratio(width, height)
        result = re.sub(r"\[aspectRatio\]", aspect_ratio, result, flags=re.IGNORECASE)

    # Frame numbers (formatted with fps)
    fps = frame_rate or 24.0
    if start_frame is not None:
        result = re.sub(
            r"\[startFrame\]",
            _format_frame_number(start_frame, fps),
            result,
            flags=re.IGNORECASE,
        )

    if end_frame is not None:
        result = re.sub(
            r"\[endFrame\]",
            _format_frame_number(end_frame, fps),
            result,
            flags=re.IGNORECASE,
        )

    if duration_frames is not None:
        result = re.sub(
            r"\[durationFrames\]",
            _format_frame_number(duration_frames, fps),
            result,
            flags=re.IGNORECASE,
        )

    # Timecodes
    if start_time is not None:
        result = re.sub(
            r"\[startTimecode\]",
            _format_timecode(start_time, fps, is_duration=False),
            result,
            flags=re.IGNORECASE,
        )

    if end_time is not None:
        result = re.sub(
            r"\[endTimecode\]",
            _format_timecode(end_time, fps, is_duration=False),
            result,
            flags=re.IGNORECASE,
        )

    if duration_time is not None:
        result = re.sub(
            r"\[durationTimecode\]",
            _format_timecode(duration_time, fps, is_duration=True),
            result,
            flags=re.IGNORECASE,
        )

    # Channels
    if channels is not None:
        channel_name = _OUTPUT_CHANNELS_NAMES.get(channels, "RGB")
        result = re.sub(r"\[channels\]", channel_name, result, flags=re.IGNORECASE)

    # Project color depth
    if project_color_depth is not None:
        depth_name = _PROJECT_COLOR_DEPTH_NAMES.get(project_color_depth, "8bit")
        result = re.sub(
            r"\[projectColorDepth\]", depth_name, result, flags=re.IGNORECASE
        )

    # Output color depth
    if output_color_depth is not None:
        depth_name = _OUTPUT_COLOR_DEPTH_NAMES.get(output_color_depth, "Millions")
        result = re.sub(
            r"\[outputColorDepth\]", depth_name, result, flags=re.IGNORECASE
        )

    # Compressor
    if compressor is not None:
        result = re.sub(r"\[compressor\]", compressor, result, flags=re.IGNORECASE)

    # Field order
    if field_render is not None:
        field_name = _FIELD_ORDER_NAMES.get(field_render, "Off")
        result = re.sub(r"\[fieldOrder\]", field_name, result, flags=re.IGNORECASE)

    # Pulldown phase (3:2 pulldown pattern)
    if pulldown_phase is not None:
        pulldown_name = _PULLDOWN_PHASE_NAMES.get(pulldown_phase, "Off")
        result = re.sub(
            r"\[pulldownPhase\]", pulldown_name, result, flags=re.IGNORECASE
        )

    # Project folder - resolves to empty string (AE removes this in resolved paths)
    result = re.sub(r"\[projectFolder\]", "", result, flags=re.IGNORECASE)

    # File extension
    if file_extension is not None:
        result = re.sub(
            r"\[fileExtension\]", file_extension, result, flags=re.IGNORECASE
        )

    return result


@dataclass
class OutputModule:
    """
    An `OutputModule` object of a [RenderQueueItem][] generates a single file or
    sequence via a render operation, and contains attributes and methods
    relating to the file to be rendered.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/outputmodule/
    """

    crop: bool
    """When `True`, the Crop checkbox is enabled for this output module."""

    file_template: str | None
    """
    The raw file path template, may contain `[compName]` and `[fileExtension]`
    variables.
    """

    include_source_xmp: bool
    """When `True`, writes all source footage XMP metadata to the output file."""

    name: str | None
    """The name of the output module, as shown in the user interface."""

    parent: RenderQueueItem = field(repr=False)
    """
    Reference to parent RenderQueueItem, used for resolving file paths and
    accessing comp and render settings.
    """

    post_render_action: PostRenderAction
    """
    An action to perform when rendering is complete. Only used when
    `post_render_action` is `IMPORT_AND_REPLACE` or `SET_PROXY`. When 0 or
    `None`, uses the render queue item's comp.
    """

    post_render_target_comp: CompItem = field(repr=False)
    """
    The [CompItem][] to use for post-render actions that require a comp. Only
    used when `post_render_action` is `IMPORT_AND_REPLACE` or `SET_PROXY`.
    """

    settings: dict[str, Any]
    """
    Dictionary containing all output module settings with ExtendScript keys.
    Includes "Video Output", "Audio Bit Depth", "Audio Channels", "Color",
    etc. Matches the format from `OutputModule.getSettings(GetSettingsFormat.NUMBER)`.
    """

    templates: list[str]
    """
    The names of all output-module templates available in the local
    installation of After Effects.
    """
    _project_name: str | None = field(default=None, repr=False)
    _project_color_depth: int | None = field(default=None, repr=False)

    @property
    def comp_name(self) -> str:
        """The composition name, resolved from parent RenderQueueItem."""
        return self.parent.comp_name

    @property
    def file(self) -> str | None:
        """The full path for the file this output module is set to render.

        Resolves template variables like `[compName]`, `[width]`, `[frameRate]`,
        etc. to their actual values based on the composition and render settings.
        """
        comp = self.parent.comp
        rq_settings = self.parent.settings

        # Get file extension from template lookup
        extension = _TEMPLATE_EXTENSIONS.get(self.name, None) if self.name else None

        # Get output module settings with defaults
        # Default to RGB channels if not specified
        om_channels = self.settings.get("Channels", OutputChannels.RGB)
        # Default to Millions of Colors (8 bpc) if not specified
        om_depth = self.settings.get("Depth", OutputColorDepth.MILLIONS_OF_COLORS)
        # Map codec FourCC to friendly name
        codec = self.settings.get("Video Codec")
        compressor = _VIDEO_CODEC_NAMES.get(codec, codec) if codec else None

        # Calculate effective dimensions applying resolution factor
        # Resolution is stored as [x_factor, y_factor] e.g., [7, 1]
        # means 1/7 width resolution and 1/1 height resolution
        resolution = rq_settings.get("Resolution", [1, 1])
        if resolution and len(resolution) >= 2:
            x_factor = resolution[0] if resolution[0] > 0 else 1
            y_factor = resolution[1] if resolution[1] > 0 else 1
            # AE uses ceiling for dimension calculations
            effective_width = math.ceil(comp.width / x_factor)
            effective_height = math.ceil(comp.height / y_factor)
        else:
            effective_width = comp.width
            effective_height = comp.height

        # Determine effective frame rate
        # "Frame Rate" indicates if custom frame rate is used (True = use custom)
        use_custom_frame_rate = rq_settings.get("Frame Rate", False)
        if use_custom_frame_rate:
            effective_frame_rate = rq_settings.get(
                "Use this frame rate", comp.frame_rate
            )
        else:
            effective_frame_rate = comp.frame_rate

        # Determine time span values based on Time Span mode
        # 0 = Work Area, 1 = Length of Comp, 2 = Custom
        time_span_mode = rq_settings.get("Time Span", 1)

        # Compute starting frame number from comp's display_start_time and render timeSpanStart
        # Formula: Starting # = int(displayStartTime * fps) + int(timeSpanStart * fps)
        # This accounts for both the comp's display offset and the render time span offset
        if time_span_mode == 1:  # LENGTH_OF_COMP
            # Use comp's full duration at effective frame rate
            time_span_start = 0.0
            duration_time = comp.duration
            time_span_end = comp.duration
            # Use round() for duration frames to match AE behavior
            duration_frames = round(comp.duration * effective_frame_rate)
            # Starting frame is based on display_start_time only
            starting_number = int(comp.display_start_time * effective_frame_rate)
        else:
            # Use values from render settings (Work Area or Custom)
            time_span_start = rq_settings.get("Time Span Start", 0.0)
            duration_time = rq_settings.get("Time Span Duration", 0.0)
            time_span_end = rq_settings.get("Time Span End", 0.0)
            # Use round() for duration frames to match AE behavior
            duration_frames = round(duration_time * effective_frame_rate)
            # Starting frame combines display_start_time and time_span_start
            starting_number = int(comp.display_start_time * effective_frame_rate) + int(
                time_span_start * effective_frame_rate
            )

        # Frame numbers use computed starting number
        start_frame = starting_number
        end_frame = starting_number + duration_frames

        # Timecodes include display_start_time offset for absolute positioning
        start_time_for_tc = comp.display_start_time + time_span_start
        end_time_for_tc = comp.display_start_time + time_span_end

        return resolve_output_filename(
            self.file_template,
            project_name=self._project_name,
            comp_name=comp.name,
            render_settings_name=rq_settings.get("Template Name"),
            output_module_name=self.name,
            width=effective_width,
            height=effective_height,
            frame_rate=effective_frame_rate,
            start_frame=start_frame,
            end_frame=end_frame,
            duration_frames=duration_frames,
            start_time=start_time_for_tc,
            end_time=end_time_for_tc,
            duration_time=duration_time,
            channels=om_channels,
            project_color_depth=self._project_color_depth,
            output_color_depth=om_depth,
            compressor=compressor,
            field_render=rq_settings.get("Field Render"),
            pulldown_phase=rq_settings.get("3:2 Pulldown"),
            file_extension=extension,
        )
