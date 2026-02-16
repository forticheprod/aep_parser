"""aep_parser - A .aep (After Effects Project) parser."""

from __future__ import annotations

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import (  # type: ignore[import,no-redef]  # Python 3.7
        PackageNotFoundError,
        version,
    )

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
from .parsers.project import parse_project

try:
    __version__ = version("aep_parser")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "AlphaMode",
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
