from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .output_module_settings import OutputModuleSettings

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


def resolve_output_filename(
    file_template: str | None,
    comp_name: str | None = None,
    file_extension: str | None = None,
) -> str | None:
    """Resolve an After Effects output filename template to the actual filename.

    After Effects stores output paths with template variables like `[compName]`
    and `[fileextension]`. This function resolves those variables to produce
    the actual filename that would be rendered.

    Args:
        file_template: The file path containing template variables.
            e.g., `C:/Output/[compName].[fileextension]`
        comp_name: The composition name to substitute for `[compName]`.
        file_extension: The file extension to substitute for `[fileextension]`.

    Returns:
        The resolved file path, or None if file_template is None.
    """
    if file_template is None:
        return None

    result = file_template

    if comp_name is not None:
        result = re.sub(r"\[compName\]", comp_name, result, flags=re.IGNORECASE)

    if file_extension is not None:
        result = re.sub(
            r"\[fileextension\]", file_extension, result, flags=re.IGNORECASE
        )

    return result


@dataclass
class OutputModule:
    """
    An OutputModule object of a RenderQueueItem generates a single file or
    sequence via a render operation, and contains attributes and methods
    relating to the file to be rendered.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/outputmodule/

    Attributes:
        file_template: The raw file path template, may contain `[compName]` and
            `[fileextension]` variables.
        name: The name of the output module, as shown in the user interface.
        om_settings: Parsed output module settings from the binary AEP file,
            including video codec, audio settings, and color options.
        templates: The names of all output-module templates available in the
            local installation of After Effects.
        settings: Dictionary containing all output module settings.
            Retrieved via ExtendScript `OutputModule.getSettings(GetSettingsFormat.STRING)`.
        comp_name: The composition name, used to resolve `[compName]` in file path.
    """

    file_template: str | None = None
    name: str | None = None
    om_settings: OutputModuleSettings | None = None
    templates: list[str] = field(default_factory=list)
    settings: dict[str, Any] = field(default_factory=dict)
    comp_name: str | None = None

    @property
    def file(self) -> str | None:
        """The full path for the file this output module is set to render."""
        extension = _TEMPLATE_EXTENSIONS.get(self.name, None)
        return resolve_output_filename(self.file_template, self.comp_name, extension)
