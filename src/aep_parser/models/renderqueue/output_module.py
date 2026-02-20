from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ...resolvers.output import (
    TEMPLATE_EXTENSIONS,
    VIDEO_CODEC_NAMES,
    resolve_effective_dimensions,
    resolve_effective_frame_rate,
    resolve_output_filename,
    resolve_time_span,
)
from ..enums import GetSettingsFormat, PostRenderAction
from ..settings import (
    OutputModuleSettings,
    settings_to_number,
    settings_to_string,
)

if TYPE_CHECKING:
    from ..items.composition import CompItem
    from .render_queue_item import RenderQueueItem


@dataclass
class OutputModule:
    """
    An `OutputModule` object of a [RenderQueueItem][] generates a single file or
    sequence via a render operation, and contains attributes and methods
    relating to the file to be rendered.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/outputmodule/
    """

    file_template: str
    """
    The raw file path template, may contain `[compName]` and `[fileExtension]`
    variables.
    """

    frame_rate: float
    """The output frame rate for this output module."""

    include_source_xmp: bool
    """When `True`, writes all source footage XMP metadata to the output file."""

    output_color_space: str | None
    """The output color space."""

    preserve_rgb: bool
    """
    When `True`, disable color management conversions for this output module.

    Note:
        Not exposed in ExtendScript.
    """

    name: str
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

    settings: OutputModuleSettings
    """
    [OutputModuleSettings][aep_parser.models.settings.OutputModuleSettings]
    dict with ExtendScript-compatible keys. Includes "Video Output",
    "Audio Bit Depth", "Audio Channels", "Color", etc. Matches the
    format from ``OutputModule.getSettings(GetSettingsFormat.NUMBER)``.
    """

    templates: list[str]
    """
    The names of all output-module templates available in the local
    installation of After Effects.
    """

    _project_color_depth: int = field(repr=False)
    _project_name: str = field(repr=False)
    _video_codec: str | None = field(default=None, repr=False)

    @property
    def file(self) -> str:
        """The full path for the file this output module is set to render.

        Resolves template variables like `[compName]`, `[width]`, `[frameRate]`,
        etc. to their actual values based on the composition and render settings.
        """
        comp = self.parent.comp
        rq_settings = self.parent.settings

        extension = TEMPLATE_EXTENSIONS.get(self.name, None) if self.name else None
        om_channels = self.settings["Channels"]
        om_depth = self.settings["Depth"]
        compressor = (
            VIDEO_CODEC_NAMES.get(self._video_codec, self._video_codec)
            if self._video_codec
            else None
        )

        effective_width, effective_height = resolve_effective_dimensions(
            comp, rq_settings
        )
        effective_frame_rate = resolve_effective_frame_rate(comp, rq_settings)
        time_span = resolve_time_span(comp, rq_settings, effective_frame_rate)

        return resolve_output_filename(
            self.file_template,
            project_name=self._project_name,
            comp_name=comp.name,
            render_settings_name=self.parent.name,
            output_module_name=self.name,
            width=effective_width,
            height=effective_height,
            frame_rate=effective_frame_rate,
            start_frame=time_span["start_frame"],
            end_frame=time_span["end_frame"],
            duration_frames=time_span["duration_frames"],
            start_time=time_span["start_time"],
            end_time=time_span["end_time"],
            duration_time=time_span["duration_time"],
            channels=om_channels,
            project_color_depth=self._project_color_depth,
            output_color_depth=om_depth,
            compressor=compressor,
            field_render=rq_settings["Field Render"],
            pulldown_phase=rq_settings["3:2 Pulldown"],
            file_extension=extension,
        )

    def get_settings(
        self,
        format: GetSettingsFormat = GetSettingsFormat.STRING,
    ) -> dict[str, Any]:
        """Return output module settings in the specified format.

        Args:
            format: The output format.
                ``GetSettingsFormat.NUMBER`` returns numeric values (enums unwrapped to ints).
                ``GetSettingsFormat.STRING`` returns all values as strings
        """
        if format == GetSettingsFormat.STRING:
            return settings_to_string(self.settings)
        if format == GetSettingsFormat.NUMBER:
            return settings_to_number(self.settings)
        raise ValueError(f"Unsupported format: {format!r}")

    def get_setting(
        self,
        key: str,
        format: GetSettingsFormat = GetSettingsFormat.STRING,
    ) -> Any:
        """Return a single output module setting in the specified format.

        Args:
            key: The setting key (e.g. ``"Video Output"``, ``"Audio Bit Depth"``).
            format: The output format.
        """
        return self.get_settings(format)[key]
