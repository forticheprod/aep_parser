"""aep_parser - A .aep (After Effects Project) parser."""

from __future__ import annotations

import os

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import (  # type: ignore[import,no-redef]  # Python 3.7
        PackageNotFoundError,
        version,
    )

from .kaitai import Aep
from .models.app import App
from .models.enums import (
    AlphaMode,
    AutoOrientType,
    BlendingMode,
    ChannelType,
    CloseOptions,
    FastPreviewType,
    FeetFramesFilmType,
    FieldSeparationType,
    FillLightingCorrectionType,
    FillMethodType,
    FillOutputDepthType,
    FillRangeType,
    FootageTimecodeDisplayStartType,
    FrameBlendingType,
    FramesCountType,
    GetSettingsFormat,
    ImportAsType,
    KeyframeInterpolationType,
    Language,
    LayerQuality,
    LayerSamplingQuality,
    LightType,
    LogType,
    LoopMode,
    MaskFeatherFalloff,
    MaskMode,
    MaskMotionBlur,
    ParagraphJustification,
    PlayMode,
    PostRenderAction,
    PREFType,
    ProjectThread,
    PropertyType,
    PropertyValueType,
    PulldownMethod,
    PulldownPhase,
    PurgeTarget,
    ResolveType,
    RQItemStatus,
    TimeDisplayType,
    ToolType,
    TrackMatteType,
    ViewerType,
)
from .models.project import Project
from .models.viewer import View, Viewer, ViewOptions
from .parsers.app import parse_app
from .parsers.project import _parse_project, parse_project

try:
    __version__ = version("aep_parser")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "AlphaMode",
    "App",
    "AutoOrientType",
    "BlendingMode",
    "ChannelType",
    "CloseOptions",
    "FastPreviewType",
    "FeetFramesFilmType",
    "FieldSeparationType",
    "FillLightingCorrectionType",
    "FillMethodType",
    "FillOutputDepthType",
    "FillRangeType",
    "FootageTimecodeDisplayStartType",
    "FrameBlendingType",
    "FramesCountType",
    "GetSettingsFormat",
    "ImportAsType",
    "KeyframeInterpolationType",
    "Language",
    "LayerQuality",
    "LayerSamplingQuality",
    "LightType",
    "LogType",
    "LoopMode",
    "MaskFeatherFalloff",
    "MaskMode",
    "MaskMotionBlur",
    "ParagraphJustification",
    "parse",
    "parse_project",
    "PlayMode",
    "PostRenderAction",
    "PREFType",
    "Project",
    "ProjectThread",
    "PropertyType",
    "PropertyValueType",
    "PulldownMethod",
    "PulldownPhase",
    "PurgeTarget",
    "ResolveType",
    "RQItemStatus",
    "TimeDisplayType",
    "ToolType",
    "TrackMatteType",
    "View",
    "Viewer",
    "ViewerType",
    "ViewOptions",
]


def parse(aep_file_path: str | os.PathLike[str]) -> App:
    """Parse an After Effects (.aep) project file and return an [App][] instance.

    This is the main entry point for the library. It parses the binary
    RIFX data and returns an [App][] object whose
    [project][aep_parser.models.app.App.project] attribute
    holds the full project tree.

    Args:
        aep_file_path: Path to the ``.aep`` file.

    Example:
        ```
        import aep_parser

        app = aep_parser.parse("project.aep")
        project = app.project
        print(app.version)
        ```
    """
    file_path = os.fspath(aep_file_path)
    with Aep.from_file(file_path) as aep:
        project = _parse_project(aep, file_path)
        return parse_app(aep, project)
