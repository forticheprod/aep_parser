"""After Effects enumerations.

These enums match the values used in After Effects ExtendScript.
"""

from __future__ import annotations

from enum import IntEnum


class Label(IntEnum):
    """Label color for items, layers, keyframes and markers.

    Colors are represented by their number (0 for None, or 1 to 16 for one
    of the preset colors in the Labels preferences).

    See: https://ae-scripting.docsforadobe.dev/item/item/#itemlabel
    """

    NONE = 0
    RED = 1
    YELLOW = 2
    AQUA = 3
    PINK = 4
    LAVENDER = 5
    PEACH = 6
    SEA_FOAM = 7
    BLUE = 8
    GREEN = 9
    PURPLE = 10
    ORANGE = 11
    BROWN = 12
    FUCHSIA = 13
    CYAN = 14
    SANDSTONE = 15
    DARK_GREEN = 16


class PropertyControlType(IntEnum):
    """The type of effect control for a property.

    Describes the UI control type exposed in the After Effects effect panel
    (scalar slider, color picker, angle dial, checkbox, dropdown, etc.).
    """

    LAYER = 0
    INTEGER = 1
    SCALAR = 2
    ANGLE = 3
    BOOLEAN = 4
    COLOR = 5
    TWO_D = 6
    ENUM = 7
    PAINT_GROUP = 9
    SLIDER = 10
    CURVE = 11
    MASK = 12
    GROUP = 13
    UNKNOWN_14 = 14
    UNKNOWN = 15
    THREE_D = 18


class PropertyValueType(IntEnum):
    """The type of value stored in a property.

    Each type of data is stored and retrieved in a different kind of
    structure.  For example, a 3-D spatial property (such as a layer's
    position) is stored as an array of three floating-point values.

    See: https://ae-scripting.docsforadobe.dev/property/property/#propertypropertyvaluetype
    """

    UNKNOWN = 0
    NO_VALUE = 1
    THREE_D_SPATIAL = 2
    THREE_D = 3
    TWO_D_SPATIAL = 4
    TWO_D = 5
    ONE_D = 6
    COLOR = 7
    CUSTOM_VALUE = 8
    MARKER = 9
    LAYER_INDEX = 10
    MASK_INDEX = 11
    SHAPE = 12
    TEXT_DOCUMENT = 13
    LRDR = 14
    LITM = 15
    GIDE = 16
    ORIENTATION = 17


class AlphaMode(IntEnum):
    """Defines how alpha information in footage is interpreted.

    See: https://ae-scripting.docsforadobe.dev/sources/footagesource/#footagesourcealphamode
    """

    STRAIGHT = 5412
    IGNORE = 5413
    PREMULTIPLIED = 5414


class BitsPerChannel(IntEnum):
    """The color depth of the project.

    See: https://ae-scripting.docsforadobe.dev/general/project/#projectbitsperchannel
    """

    EIGHT = 8
    SIXTEEN = 16
    THIRTY_TWO = 32


class AutoOrientType(IntEnum):
    """Auto-orientation mode for a layer.

    See: https://ae-scripting.docsforadobe.dev/layer/layer/#layerautoorient
    """

    NO_AUTO_ORIENT = 4212
    ALONG_PATH = 4213
    CAMERA_OR_POINT_OF_INTEREST = 4214
    CHARACTERS_TOWARD_CAMERA = 4215


class BlendingMode(IntEnum):
    """Blending mode for a layer.

    See: https://ae-scripting.docsforadobe.dev/layer/avlayer/#avlayerblendingmode
    """

    NORMAL = 5212
    DISSOLVE = 5213
    DANCING_DISSOLVE = 5214
    DARKEN = 5215
    MULTIPLY = 5216
    LINEAR_BURN = 5217
    COLOR_BURN = 5218
    CLASSIC_COLOR_BURN = 5219
    ADD = 5220
    LIGHTEN = 5221
    SCREEN = 5222
    LINEAR_DODGE = 5223
    COLOR_DODGE = 5224
    CLASSIC_COLOR_DODGE = 5225
    OVERLAY = 5226
    SOFT_LIGHT = 5227
    HARD_LIGHT = 5228
    LINEAR_LIGHT = 5229
    VIVID_LIGHT = 5230
    PIN_LIGHT = 5231
    HARD_MIX = 5232
    DIFFERENCE = 5233
    CLASSIC_DIFFERENCE = 5234
    EXCLUSION = 5235
    HUE = 5236
    SATURATION = 5237
    COLOR = 5238
    LUMINOSITY = 5239
    STENCIL_ALPHA = 5240
    STENCIL_LUMA = 5241
    SILHOUETE_ALPHA = 5242  # The typo is in the ExtendScript API
    SILHOUETTE_LUMA = 5243
    ALPHA_ADD = 5244
    LUMINESCENT_PREMUL = 5245
    LIGHTER_COLOR = 5246
    DARKER_COLOR = 5247
    SUBTRACT = 5248
    DIVIDE = 5249


class ChannelType(IntEnum):
    """Channel display type for a viewer.

    See: https://ae-scripting.docsforadobe.dev/other/viewoptions/#attributes
    """

    CHANNEL_RGB = 7812
    CHANNEL_RED = 7813
    CHANNEL_GREEN = 7814
    CHANNEL_BLUE = 7815
    CHANNEL_ALPHA = 7816
    CHANNEL_RED_COLORIZE = 7817
    CHANNEL_GREEN_COLORIZE = 7818
    CHANNEL_BLUE_COLORIZE = 7819
    CHANNEL_RGB_STRAIGHT = 7820
    CHANNEL_ALPHA_OVERLAY = 7821
    CHANNEL_ALPHA_BOUNDARY = 7822

    @classmethod
    def from_binary(cls, value: int) -> ChannelType:
        """Convert binary value to ChannelType."""
        try:
            return cls(value + 7812)
        except ValueError:
            return cls.CHANNEL_RGB


class ColorManagementSystem(IntEnum):
    """Color management system for the project."""

    ADOBE = 0
    OCIO = 1


class LutInterpolationMethod(IntEnum):
    """LUT interpolation method for the project."""

    TRILINEAR = 0
    TETRAHEDRAL = 1


class CloseOptions(IntEnum):
    """Options for closing a project.

    See: https://ae-scripting.docsforadobe.dev/general/project/#projectclose
    """

    DO_NOT_SAVE_CHANGES = 1212
    PROMPT_TO_SAVE_CHANGES = 1213
    SAVE_CHANGES = 1214


class FastPreviewType(IntEnum):
    """Fast preview mode for a composition.

    See: https://ae-scripting.docsforadobe.dev/other/viewoptions/#viewoptionsfastpreview
    """

    FP_OFF = 8012
    FP_ADAPTIVE_RESOLUTION = 8013
    FP_DRAFT = 8014
    FP_FAST_DRAFT = 8015
    FP_WIREFRAME = 8016


class FeetFramesFilmType(IntEnum):
    """Film type for feet+frames timecode display.

    See: https://ae-scripting.docsforadobe.dev/general/project/#projectfeetframesfilmtype
    """

    MM16 = 2412
    MM35 = 2413

    @classmethod
    def from_binary(cls, value: int) -> FeetFramesFilmType:
        """Convert binary value (0-1) to FeetFramesFilmType."""
        # Binary 0 = MM35 (2413), Binary 1 = MM16 (2412)
        return cls(2413 - value)


class FieldSeparationType(IntEnum):
    """How fields are separated in interlaced footage.

    See: https://ae-scripting.docsforadobe.dev/sources/footagesource/#footagesourcefieldseparationtype
    """

    UPPER_FIELD_FIRST = 5612
    OFF = 5613
    LOWER_FIELD_FIRST = 5614


class FootageTimecodeDisplayStartType(IntEnum):
    """How timecode is displayed for footage.

    See: https://ae-scripting.docsforadobe.dev/general/project/#projectfootagetimecodedisplaystarttype
    """

    FTCS_USE_SOURCE_MEDIA = 2212
    FTCS_START_0 = 2213


class FrameBlendingType(IntEnum):
    """Frame blending mode for a layer.

    See: https://ae-scripting.docsforadobe.dev/layer/avlayer/#avlayerframeblendingtype
    """

    NO_FRAME_BLEND = 4012
    FRAME_MIX = 4013
    PIXEL_MOTION = 4014


class FramesCountType(IntEnum):
    """How frames are counted in the project.

    See: https://ae-scripting.docsforadobe.dev/general/project/#projectframescounttype
    """

    FC_START_0 = 2612
    FC_START_1 = 2613
    FC_TIMECODE_CONVERSION = 2614

    @classmethod
    def from_binary(cls, value: int) -> FramesCountType:
        """Convert binary value to FramesCountType."""
        try:
            return cls(value + 2612)
        except ValueError:
            return cls.FC_START_0


class GetSettingsFormat(IntEnum):
    """Format for getting render settings.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/outputmodule/#outputmodulegetsettings
    """

    SPEC = 3412
    NUMBER = 3413
    NUMBER_SETTABLE = 3414
    STRING = 3415
    STRING_SETTABLE = 3416


class GpuAccelType(IntEnum):
    """GPU acceleration type.

    See: https://ae-scripting.docsforadobe.dev/general/project/#projectgpuacceltype
    """

    OPENCL = 1812
    CUDA = 1813
    METAL = 1814
    VULKAN = 1815
    SOFTWARE = 1816


class ImportAsType(IntEnum):
    """How to import a file.

    See: https://ae-scripting.docsforadobe.dev/other/importoptions/#importoptionsimportas
    """

    COMP_CROPPED_LAYERS = 3812
    FOOTAGE = 3813
    COMP = 3814
    PROJECT = 3815


class KeyframeInterpolationType(IntEnum):
    """Interpolation type for keyframes.

    See: https://ae-scripting.docsforadobe.dev/property/property/#propertysetinterpolationtypeatkey
    """

    LINEAR = 6612
    BEZIER = 6613
    HOLD = 6614

    @classmethod
    def from_binary(cls, value: int) -> KeyframeInterpolationType:
        """Convert binary value to KeyframeInterpolationType."""
        try:
            return cls(value + 6611)
        except ValueError:
            return cls.LINEAR


class Language(IntEnum):
    """Application language.

    See: https://ae-scripting.docsforadobe.dev/general/application/#appisolanguage
    """

    ENGLISH = 1612
    JAPANESE = 1613
    GERMAN = 1614
    FRENCH = 1615
    ITALIAN = 1616
    SPANISH = 1617
    KOREAN = 1618
    CHINESE = 1619
    RUSSIAN = 1620
    PORTUGUESE = 1621


class LayerQuality(IntEnum):
    """Render quality for a layer.

    See: https://ae-scripting.docsforadobe.dev/layer/avlayer/#avlayerquality
    """

    WIREFRAME = 4612
    DRAFT = 4613
    BEST = 4614

    @classmethod
    def from_binary(cls, value: int) -> LayerQuality:
        """Convert binary value to LayerQuality."""
        try:
            return cls(value + 4612)
        except ValueError:
            return cls.BEST


class LayerSamplingQuality(IntEnum):
    """Sampling quality for a layer.

    See: https://ae-scripting.docsforadobe.dev/layer/avlayer/#avlayersamplingquality
    """

    BILINEAR = 4812
    BICUBIC = 4813

    @classmethod
    def from_binary(cls, value: int) -> LayerSamplingQuality:
        """Convert binary value to LayerSamplingQuality."""
        try:
            return cls(value + 4812)
        except ValueError:
            return cls.BILINEAR


class LightType(IntEnum):
    """Type of light layer.

    See: https://ae-scripting.docsforadobe.dev/layer/lightlayer/#lightlayerlighttype
    """

    PARALLEL = 4412
    SPOT = 4413
    POINT = 4414
    AMBIENT = 4415

    @classmethod
    def from_binary(cls, value: int) -> LightType:
        """Convert binary value to LightType."""
        try:
            return cls(value + 4412)
        except ValueError:
            return cls.PARALLEL


class LogType(IntEnum):
    """Logging level for rendering.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/renderqueueitem/#renderqueueitemlogtype
    """

    ERRORS_ONLY = 3212
    ERRORS_AND_SETTINGS = 3213
    ERRORS_AND_PER_FRAME_INFO = 3214

    @classmethod
    def from_binary(cls, value: int) -> LogType:
        """Convert binary value to LogType."""
        try:
            return cls(value + 3212)
        except ValueError:
            return cls.ERRORS_ONLY


class LoopMode(IntEnum):
    """Loop mode for preview playback."""

    LOOP = 8412
    PLAY_ONCE = 8413
    PING_PONG = 8414


class MaskFeatherFalloff(IntEnum):
    """Feather falloff type for masks.

    See: https://ae-scripting.docsforadobe.dev/property/maskpropertygroup/#maskpropertygroupmaskfeatherfalloff
    """

    FFO_SMOOTH = 7212
    FFO_LINEAR = 7213


class MaskMode(IntEnum):
    """Blending mode for masks.

    See: https://ae-scripting.docsforadobe.dev/property/maskpropertygroup/#maskpropertygroupmaskmode
    """

    NONE = 6812
    ADD = 6813
    SUBTRACT = 6814
    INTERSECT = 6815
    LIGHTEN = 6816
    DARKEN = 6817
    DIFFERENCE = 6818


class MaskMotionBlur(IntEnum):
    """Motion blur setting for masks.

    See: https://ae-scripting.docsforadobe.dev/property/maskpropertygroup/#maskpropertygroupmaskmotionblur
    """

    SAME_AS_LAYER = 7012
    ON = 7013
    OFF = 7014


class ParagraphJustification(IntEnum):
    """Paragraph justification for text layers.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentjustification
    """

    MULTIPLE_JUSTIFICATIONS = 7412
    LEFT_JUSTIFY = 7413
    RIGHT_JUSTIFY = 7414
    CENTER_JUSTIFY = 7415
    FULL_JUSTIFY_LASTLINE_LEFT = 7416
    FULL_JUSTIFY_LASTLINE_RIGHT = 7417
    FULL_JUSTIFY_LASTLINE_CENTER = 7418
    FULL_JUSTIFY_LASTLINE_FULL = 7419


class PlayMode(IntEnum):
    """Playback mode for preview.

    Not documented in AE scripting reference.
    """

    SPACEBAR = 8212
    RAM_PREVIEW = 8213


class PostRenderAction(IntEnum):
    """Action after rendering completes.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/outputmodule/#outputmodulepostrenderaction
    """

    NONE = 3612
    IMPORT = 3613
    IMPORT_AND_REPLACE_USAGE = 3614
    SET_PROXY = 3615

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _POST_RENDER_ACTION_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> PostRenderAction:
        """Convert binary value to PostRenderAction."""
        try:
            return cls(value + 3612)
        except ValueError:
            return cls.NONE


_POST_RENDER_ACTION_LABELS: dict[int, str] = {
    3612: "None",
    3613: "Import",
    3614: "Import & Replace Usage",
    3615: "Set Proxy",
}


class PREFType(IntEnum):
    """Preference file types.

    See: https://ae-scripting.docsforadobe.dev/other/preferences/#preferences-object
    """

    PREF_Type_MACHINE_SPECIFIC = 8812
    PREF_Type_MACHINE_INDEPENDENT = 8813
    PREF_Type_MACHINE_INDEPENDENT_RENDER = 8814
    PREF_Type_MACHINE_INDEPENDENT_OUTPUT = 8815
    PREF_Type_MACHINE_INDEPENDENT_COMPOSITION = 8816
    PREF_Type_MACHINE_SPECIFIC_TEXT = 8817
    PREF_Type_MACHINE_SPECIFIC_PAINT = 8818


class PropertyType(IntEnum):
    """Type of a property.

    See: https://ae-scripting.docsforadobe.dev/property/propertybase/#propertybasepropertytype
    """

    PROPERTY = 6212
    NAMED_GROUP = 6213
    INDEXED_GROUP = 6214


class PulldownMethod(IntEnum):
    """Pulldown method for footage.

    See: https://ae-scripting.docsforadobe.dev/sources/footagesource/#footagesourceguesspulldown
    """

    PULLDOWN_3_2 = 6012
    ADVANCE_24P = 6013


class PulldownPhase(IntEnum):
    """Pulldown phase for footage.

    See: https://ae-scripting.docsforadobe.dev/sources/footagesource/#footagesourceremovepulldown
    """

    WSSWW = 5812
    OFF = 5813
    SSWWW = 5814
    SWWWS = 5815
    WWWSS = 5816
    WWSSW = 5817
    WWWSW_24P_ADVANCE = 5818
    WWSWW_24P_ADVANCE = 5819
    WSWWW_24P_ADVANCE = 5820
    SWWWW_24P_ADVANCE = 5821
    WWWWS_24P_ADVANCE = 5822


class PurgeTarget(IntEnum):
    """Target for purging caches.

    See: https://ae-scripting.docsforadobe.dev/general/application/#apppurge
    """

    ALL_CACHES = 1412
    UNDO_CACHES = 1413
    SNAPSHOT_CACHES = 1414
    IMAGE_CACHES = 1415


class ResolveType(IntEnum):
    """Conflict resolution type for team projects.

    See: https://ae-scripting.docsforadobe.dev/general/project/#projectresolveconflict
    """

    ACCEPT_THEIRS = 8612
    ACCEPT_THEIRS_AND_COPY = 8613
    ACCEPT_YOURS = 8614


class RQItemStatus(IntEnum):
    """Status of a render queue item.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/renderqueueitem/#renderqueueitemstatus
    """

    WILL_CONTINUE = 3012
    NEEDS_OUTPUT = 3013
    UNQUEUED = 3014
    QUEUED = 3015
    RENDERING = 3016
    USER_STOPPED = 3017
    ERR_STOPPED = 3018
    DONE = 3019

    @classmethod
    def from_binary(cls, value: int) -> RQItemStatus:
        """Convert binary value to RQItemStatus."""
        try:
            return cls(value + 3013)
        except ValueError:
            return cls.UNQUEUED


class TimeDisplayType(IntEnum):
    """How time is displayed in the project.

    See: https://ae-scripting.docsforadobe.dev/general/project/#projecttimedisplaytype
    """

    TIMECODE = 2012
    FRAMES = 2013

    @classmethod
    def from_binary(cls, value: int) -> TimeDisplayType:
        """Convert binary value to TimeDisplayType."""
        try:
            return cls(value + 2012)
        except ValueError:
            return cls.TIMECODE


class ToolType(IntEnum):
    """Tool type in the application.

    See: https://ae-scripting.docsforadobe.dev/general/project/#projecttooltype
    """

    Tool_Arrow = 9012
    Tool_Rotate = 9013
    Tool_CameraMaya = 9014
    Tool_CameraOrbit = 9015
    Tool_CameraOrbitCamera = 9015
    Tool_CameraPanCamera = 9016
    Tool_CameraTrackXY = 9016
    Tool_CameraDollyCamera = 9017
    Tool_CameraTrackZ = 9017
    Tool_Paintbrush = 9018
    Tool_CloneStamp = 9019
    Tool_Eraser = 9020
    Tool_Hand = 9021
    Tool_Magnify = 9022
    Tool_PanBehind = 9023
    Tool_Rect = 9024
    Tool_RoundedRect = 9025
    Tool_Oval = 9026
    Tool_Polygon = 9027
    Tool_Star = 9028
    Tool_TextH = 9029
    Tool_TextV = 9030
    Tool_Pen = 9031
    Tool_Feather = 9032
    Tool_PenPlus = 9033
    Tool_PenMinus = 9034
    Tool_PenConvert = 9035
    Tool_Pin = 9036
    Tool_PinStarch = 9037
    Tool_PinBend = 9038
    Tool_PinDepth = 9040
    Tool_Quickselect = 9041
    Tool_Hairbrush = 9042
    Tool_PinAdvanced = 9043
    Tool_CameraOrbitCursor = 9044
    Tool_CameraOrbitScene = 9045
    Tool_CameraPanCursor = 9046
    Tool_CameraDollyTowardsCursor = 9047
    Tool_CameraDollyToCursor = 9048


class TrackMatteType(IntEnum):
    """Track matte type for a layer.

    See: https://ae-scripting.docsforadobe.dev/layer/avlayer/#avlayertrackmattetype
    """

    NO_TRACK_MATTE = 5012
    ALPHA = 5013
    ALPHA_INVERTED = 5014
    LUMA = 5015
    LUMA_INVERTED = 5016

    @classmethod
    def from_binary(cls, value: int) -> TrackMatteType:
        """Convert binary value to TrackMatteType."""
        try:
            return cls(value + 5012)
        except ValueError:
            return cls.NO_TRACK_MATTE


class ViewerType(IntEnum):
    """Type of viewer panel.

    See: https://ae-scripting.docsforadobe.dev/other/viewer/#viewertype
    """

    VIEWER_COMPOSITION = 7612
    VIEWER_LAYER = 7613
    VIEWER_FOOTAGE = 7614


class FillLightingCorrectionType(IntEnum):
    """Lighting correction for Content-Aware Fill.

    Not documented in AE scripting reference.
    """

    LightingCorrection_NONE = 9812
    LightingCorrection_SUBTLE = 9813
    LightingCorrection_MODERATE = 9814
    LightingCorrection_STRONG = 9815


class FillMethodType(IntEnum):
    """Fill method for Content-Aware Fill.

    Not documented in AE scripting reference.
    """

    Method_OBJECT = 9412
    Method_SURFACE = 9413
    Method_EDGEBLEND = 9414


class FillOutputDepthType(IntEnum):
    """Output depth for Content-Aware Fill.

    Not documented in AE scripting reference.
    """

    OutputDepth_PROJECT = 9612
    OutputDepth_EIGHT = 9613
    OutputDepth_SIXTEEN = 9614
    OutputDepth_FLOAT = 9615


class FillRangeType(IntEnum):
    """Range for Content-Aware Fill.

    Not documented in AE scripting reference.
    """

    Range_ENTIRE = 9212
    Range_WORKAREA = 9213


class ProjectThread(IntEnum):
    """Thread type for project operations.

    Not documented in AE scripting reference.
    """

    MainThread = 2812
    RQThread = 2813
    WorkQueueThread = 2814


# =============================================================================
# Render Queue Enums
# =============================================================================


class FrameRateSetting(IntEnum):
    """Frame rate source setting for rendering.

    Determines whether the render uses the composition's own frame rate
    or a custom frame rate specified in the render settings.

    Used in RenderQueueItem Settings > Frame Rate

    Not documented in AE scripting reference.
    """

    USE_COMP_FRAME_RATE = 0
    USE_THIS_FRAME_RATE = 1

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _FRAME_RATE_SETTING_LABELS[self.value]


_FRAME_RATE_SETTING_LABELS: dict[int, str] = {
    0: "Use comp's frame rate",
    1: "Use this frame rate",
}


class RenderQuality(IntEnum):
    """Quality setting for rendering.

    Used in RenderQueueItem Settings > Quality

    Not documented in AE scripting reference.
    """

    CURRENT_SETTINGS = -1
    WIREFRAME = 0
    DRAFT = 1
    BEST = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _RENDER_QUALITY_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> RenderQuality:
        """Convert binary value to RenderQuality (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_RENDER_QUALITY_LABELS: dict[int, str] = {
    -1: "Current Settings",
    0: "Wireframe",
    1: "Draft",
    2: "Best",
}


class FieldRender(IntEnum):
    """Field rendering option.

    Used in RenderQueueItem Settings > Field Render

    Not documented in AE scripting reference.
    """

    OFF = 0
    UPPER_FIELD_FIRST = 1
    LOWER_FIELD_FIRST = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _FIELD_RENDER_LABELS[self.value]


_FIELD_RENDER_LABELS: dict[int, str] = {
    0: "Off",
    1: "Upper Field First",
    2: "Lower Field First",
}


class PulldownSetting(IntEnum):
    """3:2 Pulldown phase for field rendering.

    Used in RenderQueueItem Settings > 3:2 Pulldown

    Not documented in AE scripting reference.
    """

    OFF = 0
    WSSWW = 1
    SSWWW = 2
    SWWWS = 3
    WWWSS = 4
    WWSSW = 5

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _PULLDOWN_SETTING_LABELS[self.value]


_PULLDOWN_SETTING_LABELS: dict[int, str] = {
    0: "Off",
    1: "WSSWW",
    2: "SSWWW",
    3: "SWWWS",
    4: "WWWSS",
    5: "WWSSW",
}


class MotionBlurSetting(IntEnum):
    """Motion blur render setting.

    Used in RenderQueueItem Settings > Motion Blur

    Not documented in AE scripting reference.
    """

    OFF_FOR_ALL_LAYERS = 0
    ON_FOR_CHECKED_LAYERS = 1
    CURRENT_SETTINGS = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _MOTION_BLUR_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> MotionBlurSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_MOTION_BLUR_SETTING_LABELS: dict[int, str] = {
    0: "Off for All Layers",
    1: "On for Checked Layers",
    2: "Current Settings",
}


class FrameBlendingSetting(IntEnum):
    """Frame blending render setting.

    Used in RenderQueueItem Settings > Frame Blending

    Not documented in AE scripting reference.
    """

    OFF_FOR_ALL_LAYERS = 0
    ON_FOR_CHECKED_LAYERS = 1
    CURRENT_SETTINGS = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _FRAME_BLENDING_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> FrameBlendingSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_FRAME_BLENDING_SETTING_LABELS: dict[int, str] = {
    0: "Off for All Layers",
    1: "On for Checked Layers",
    2: "Current Settings",
}


class EffectsSetting(IntEnum):
    """Effects render setting.

    Used in RenderQueueItem Settings > Effects

    Not documented in AE scripting reference.
    """

    ALL_OFF = 0
    ALL_ON = 1
    CURRENT_SETTINGS = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _EFFECTS_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> EffectsSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_EFFECTS_SETTING_LABELS: dict[int, str] = {
    0: "All Off",
    1: "All On",
    2: "Current Settings",
}


class ProxyUseSetting(IntEnum):
    """Proxy usage render setting.

    Used in RenderQueueItem Settings > Proxy Use

    Not documented in AE scripting reference.
    """

    USE_NO_PROXIES = 0
    USE_ALL_PROXIES = 1
    CURRENT_SETTINGS = 2
    USE_COMP_PROXIES_ONLY = 3

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _PROXY_USE_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> ProxyUseSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_PROXY_USE_SETTING_LABELS: dict[int, str] = {
    0: "Use No Proxies",
    1: "Use All Proxies",
    2: "Current Settings",
    3: "Use Comp Proxies Only",
}


class SoloSwitchesSetting(IntEnum):
    """Solo switches render setting.

    Used in RenderQueueItem Settings > Solo Switches

    Not documented in AE scripting reference.
    """

    ALL_OFF = 0
    CURRENT_SETTINGS = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _SOLO_SWITCHES_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> SoloSwitchesSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_SOLO_SWITCHES_SETTING_LABELS: dict[int, str] = {
    0: "All Off",
    2: "Current Settings",
}


class GuideLayers(IntEnum):
    """Guide layers render setting.

    Used in RenderQueueItem Settings > Guide Layers

    Not documented in AE scripting reference.
    """

    ALL_OFF = 0
    CURRENT_SETTINGS = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _GUIDE_LAYERS_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> GuideLayers:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_GUIDE_LAYERS_LABELS: dict[int, str] = {
    0: "All Off",
    2: "Current Settings",
}


class DiskCacheSetting(IntEnum):
    """Disk cache render setting.

    Used in RenderQueueItem Settings > Disk Cache

    Not documented in AE scripting reference.
    """

    READ_ONLY = 0
    CURRENT_SETTINGS = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _DISK_CACHE_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> DiskCacheSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_DISK_CACHE_SETTING_LABELS: dict[int, str] = {
    0: "Read Only",
    2: "Current Settings",
}


class ColorDepthSetting(IntEnum):
    """Color depth render setting.

    Used in RenderQueueItem Settings > Color Depth

    Not documented in AE scripting reference.
    """

    CURRENT_SETTINGS = -1
    EIGHT_BITS_PER_CHANNEL = 0
    SIXTEEN_BITS_PER_CHANNEL = 1
    THIRTY_TWO_BITS_PER_CHANNEL = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _COLOR_DEPTH_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> ColorDepthSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_COLOR_DEPTH_SETTING_LABELS: dict[int, str] = {
    -1: "Current Settings",
    0: "8 bits per channel",
    1: "16 bits per channel",
    2: "32 bits per channel",
}


class TimeSpanSource(IntEnum):
    """Time span source setting.

    Used in RenderQueueItem Settings > Time Span

    Not documented in AE scripting reference.
    """

    LENGTH_OF_COMP = 0
    WORK_AREA_ONLY = 1
    CUSTOM = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _TIME_SPAN_SOURCE_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> TimeSpanSource:
        """Convert binary value (0xFFFF = CUSTOM)."""
        return cls.CUSTOM if value == 0xFFFF else cls(value)


_TIME_SPAN_SOURCE_LABELS: dict[int, str] = {
    0: "Length of Comp",
    1: "Work Area Only",
    2: "Custom",
}


# =============================================================================
# Output Module Enums
# =============================================================================


class OutputChannels(IntEnum):
    """Output channels setting.

    Used in OutputModule Settings > Channels

    Not documented in AE scripting reference.
    """

    RGB = 0
    RGBA = 1
    ALPHA = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _OUTPUT_CHANNELS_LABELS[self.value]


_OUTPUT_CHANNELS_LABELS: dict[int, str] = {
    0: "RGB",
    1: "RGB + Alpha",
    2: "Alpha",
}


class OutputColorDepth(IntEnum):
    """Output color depth in total bits per pixel.

    The value represents total bits per pixel: 24 or 32 for 8 bpc
    (with/without alpha), 48 or 64 for 16 bpc, 96 or 128 for 32 bpc
    (floating point). The ``+`` label suffix indicates alpha is included.

    Used in OutputModule Settings > Depth

    Not documented in AE scripting reference.
    """

    FLOATING_POINT_GRAY = -32      # 32 bpc gray (single channel float)
    COLORS_256 = 8                 # 8 bpc indexed (256 colors)
    MILLIONS_OF_COLORS = 24        # 8 bpc RGB (24 bpp)
    MILLIONS_OF_COLORS_PLUS = 32   # 8 bpc RGBA (32 bpp)
    GRAYS_256 = 40                 # 8 bpc grayscale (256 grays)
    TRILLIONS_OF_COLORS = 48       # 16 bpc RGB (48 bpp)
    TRILLIONS_OF_COLORS_PLUS = 64  # 16 bpc RGBA (64 bpp)
    FLOATING_POINT = 96            # 32 bpc RGB (96 bpp)
    FLOATING_POINT_PLUS = 128      # 32 bpc RGBA (128 bpp)

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _OUTPUT_COLOR_DEPTH_LABELS[self.value]


_OUTPUT_COLOR_DEPTH_LABELS: dict[int, str] = {
    -32: "Floating Point Gray",
    8: "256 Colors",
    24: "Millions of Colors",
    32: "Millions of Colors+",
    40: "256 Grays",
    48: "Trillions of Colors",
    64: "Trillions of Colors+",
    96: "Floating Point",
    128: "Floating Point+",
}


class OutputColorMode(IntEnum):
    """Output color mode (premultiplied vs straight).

    Used in OutputModule Settings > Color

    Not documented in AE scripting reference.
    """

    STRAIGHT_UNMATTED = 0
    PREMULTIPLIED = 1

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _OUTPUT_COLOR_MODE_LABELS[self.value]


_OUTPUT_COLOR_MODE_LABELS: dict[int, str] = {
    0: "Straight (Unmatted)",
    1: "Premultiplied (Matted)",
}


class OutputAudio(IntEnum):
    """Audio output mode.

    Used in OutputModule Settings > Output Audio

    Not documented in AE scripting reference.
    """

    OFF = 1
    ON = 2
    AUTO = 3

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _OUTPUT_AUDIO_LABELS[self.value]


_OUTPUT_AUDIO_LABELS: dict[int, str] = {
    1: "Off",
    2: "On",
    3: "Auto",
}


class OutputFormat(IntEnum):
    """Output file format.

    Used in OutputModule Settings > Format

    Not documented in AE scripting reference.
    """

    AIFF = 0
    AVI = 1
    DPX_CINEON_SEQUENCE = 2
    H264 = 3
    IFF_SEQUENCE = 4
    JPEG_SEQUENCE = 5
    MP3 = 6
    OPENEXR_SEQUENCE = 7
    PNG_SEQUENCE = 8
    PHOTOSHOP_SEQUENCE = 9
    QUICKTIME = 10
    RADIANCE_SEQUENCE = 11
    SGI_SEQUENCE = 12
    TIFF_SEQUENCE = 13
    TARGA_SEQUENCE = 14
    WAV = 15

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _OUTPUT_FORMAT_LABELS[self.value]

    @classmethod
    def from_format_id(cls, format_id: str) -> OutputFormat:
        """Convert a Roou 4-char format identifier to OutputFormat.

        Args:
            format_id: The 4-char format identifier from the Roou chunk
                (e.g. ``"H264"``, ``"TIF "``, ``"png!"``).

        Raises:
            ValueError: If the format identifier is not recognised.
        """
        try:
            return _FORMAT_ID_TO_OUTPUT_FORMAT[format_id]
        except KeyError:
            raise ValueError(
                f"Unknown output format identifier: {format_id!r}"
            ) from None


_OUTPUT_FORMAT_LABELS: dict[int, str] = {
    0: "AIFF",
    1: "AVI",
    2: "DPX/Cineon Sequence",
    3: "H.264",
    4: "IFF Sequence",
    5: "JPEG Sequence",
    6: "MP3",
    7: "OpenEXR Sequence",
    8: "PNG Sequence",
    9: "Photoshop Sequence",
    10: "QuickTime",
    11: "Radiance Sequence",
    12: "SGI Sequence",
    13: "TIFF Sequence",
    14: "Targa Sequence",
    15: "WAV",
}


_FORMAT_ID_TO_OUTPUT_FORMAT: dict[str, OutputFormat] = {
    "AIFF": OutputFormat.AIFF,
    ".AVI": OutputFormat.AVI,
    "sDPX": OutputFormat.DPX_CINEON_SEQUENCE,
    "H264": OutputFormat.H264,
    "IFF ": OutputFormat.IFF_SEQUENCE,
    "JPEG": OutputFormat.JPEG_SEQUENCE,
    "Mp3 ": OutputFormat.MP3,
    "oEXR": OutputFormat.OPENEXR_SEQUENCE,
    "png!": OutputFormat.PNG_SEQUENCE,
    "8BPS": OutputFormat.PHOTOSHOP_SEQUENCE,
    "MooV": OutputFormat.QUICKTIME,
    "RHDR": OutputFormat.RADIANCE_SEQUENCE,
    "SGI ": OutputFormat.SGI_SEQUENCE,
    "TIF ": OutputFormat.TIFF_SEQUENCE,
    "TPIC": OutputFormat.TARGA_SEQUENCE,
    "wao_": OutputFormat.WAV,
}


class AudioBitDepth(IntEnum):
    """Audio bit depth.

    Used in OutputModule Settings > Audio > Format

    Not documented in AE scripting reference.
    """

    EIGHT_BIT = 1
    SIXTEEN_BIT = 2
    TWENTY_FOUR_BIT = 3
    THIRTY_TWO_BIT = 4

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _AUDIO_BIT_DEPTH_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> AudioBitDepth:
        """Convert binary value to AudioBitDepth (defaults to SIXTEEN_BIT)."""
        if value in cls._value2member_map_:
            return cls(value)
        return cls.SIXTEEN_BIT


_AUDIO_BIT_DEPTH_LABELS: dict[int, str] = {
    1: "8 Bit",
    2: "16 Bit",
    3: "24 Bit",
    4: "32 Bit",
}


class AudioChannels(IntEnum):
    """Audio channels.

    Used in OutputModule Settings > Audio > Channels

    Not documented in AE scripting reference.
    """

    MONO = 1
    STEREO = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _AUDIO_CHANNELS_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> AudioChannels:
        """Convert binary value to AudioChannels (0 or unknown defaults to STEREO)."""
        if value == 1:
            return cls.MONO
        return cls.STEREO


_AUDIO_CHANNELS_LABELS: dict[int, str] = {
    1: "Mono",
    2: "Stereo",
}


class ResizeQuality(IntEnum):
    """Resize quality setting.

    Used in OutputModule Settings > Stretch > Quality

    Not documented in AE scripting reference.
    """

    LOW = 0
    HIGH = 1

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _RESIZE_QUALITY_LABELS[self.value]


_RESIZE_QUALITY_LABELS: dict[int, str] = {
    0: "Low",
    1: "High",
}


class AudioSampleRate(IntEnum):
    """Audio sample rate in Hz.

    Standard sample rates available in After Effects output module
    audio settings.

    Used in OutputModule Settings > Audio > Sample Rate

    Not documented in AE scripting reference.
    """

    OFF = 0
    RATE_8000 = 8000
    RATE_11025 = 11025
    RATE_16000 = 16000
    RATE_22050 = 22050
    RATE_24000 = 24000
    RATE_32000 = 32000
    RATE_44100 = 44100
    RATE_48000 = 48000
    RATE_88200 = 88200
    RATE_96000 = 96000

    @property
    def label(self) -> str:
        """ExtendScript STRING format label (e.g. ``"48.000 kHz"``)."""
        if self.value == 0:
            return ""
        return f"{self.value / 1000:.3f} kHz"

    @classmethod
    def from_binary(cls, value: int) -> AudioSampleRate:
        """Convert binary audio sample rate value.

        Unknown or negative values (e.g. ``-1`` when audio is disabled)
        are mapped to ``OFF``.
        """
        if value in cls._value2member_map_:
            return cls(value)
        return cls.OFF

# =============================================================================
# Text Document Enums
# =============================================================================


class AutoKernType(IntEnum):
    """Auto kerning type option for text characters.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentautokerntype
    """

    NO_AUTO_KERN = 0
    METRIC_KERN = 1
    OPTICAL_KERN = 2


class BaselineDirection(IntEnum):
    """Baseline direction option for text characters.

    This is significant for Japanese language in vertical texts.
    ``BASELINE_VERTICAL_CROSS_STREAM`` is also known as Tate-Chu-Yoko.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentbaselinedirection
    """

    BASELINE_WITH_STREAM = 0
    BASELINE_VERTICAL_ROTATED = 1
    BASELINE_VERTICAL_CROSS_STREAM = 2


class BoxAutoFitPolicy(IntEnum):
    """Box auto fit policy for paragraph text boxes.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentboxautofitpolicy
    """

    NONE = 0
    HEIGHT_CURSOR = 1
    HEIGHT_PRECISE_BOUNDS = 2
    HEIGHT_BASELINE = 3


class BoxFirstBaselineAlignment(IntEnum):
    """First baseline alignment for paragraph text boxes.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentboxfirstbaselinealignment
    """

    ASCENT = 0
    CAP_HEIGHT = 1
    EM_BOX = 2
    LEADING = 3
    LEGACY_METRIC = 4
    MINIMUM_VALUE_ASIAN = 5
    MINIMUM_VALUE_ROMAN = 6
    TYPO_ASCENT = 7
    X_HEIGHT = 8


class BoxVerticalAlignment(IntEnum):
    """Vertical alignment for paragraph text boxes.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentboxverticalalignment
    """

    TOP = 0
    CENTER = 1
    BOTTOM = 2
    JUSTIFY = 3


class ComposerEngine(IntEnum):
    """Text composer engine type.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentcomposerengine
    """

    LATIN_CJK_ENGINE = 0
    UNIVERSAL_TYPE_ENGINE = 1


class DigitSet(IntEnum):
    """Digit set option for text characters.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentdigitset
    """

    DEFAULT_DIGITS = 0
    ARABIC_DIGITS = 1
    HINDI_DIGITS = 2
    FARSI_DIGITS = 3
    ARABIC_DIGITS_RTL = 4


class FontBaselineOption(IntEnum):
    """Font baseline option for superscript and subscript.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentfontbaselineoption
    """

    FONT_NORMAL_BASELINE = 0
    FONT_FAUXED_SUPERSCRIPT = 1
    FONT_FAUXED_SUBSCRIPT = 2


class FontCapsOption(IntEnum):
    """Font caps option for text characters.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentfontcapsoption
    """

    FONT_NORMAL_CAPS = 0
    FONT_SMALL_CAPS = 1
    FONT_ALL_CAPS = 2
    FONT_ALL_SMALL_CAPS = 3


class LeadingType(IntEnum):
    """Paragraph leading type.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentleadingtype
    """

    ROMAN_LEADING_TYPE = 0
    JAPANESE_LEADING_TYPE = 1


class LineJoinType(IntEnum):
    """Line join type for text stroke.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentlinejointype
    """

    LINE_JOIN_MITER = 0
    LINE_JOIN_ROUND = 1
    LINE_JOIN_BEVEL = 2


class LineOrientation(IntEnum):
    """Line orientation for text layers.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentlineorientation
    """

    HORIZONTAL = 0
    VERTICAL_RIGHT_TO_LEFT = 1
    VERTICAL_LEFT_TO_RIGHT = 2


class ParagraphDirection(IntEnum):
    """Paragraph direction for text layers.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentdirection
    """

    DIRECTION_LEFT_TO_RIGHT = 0
    DIRECTION_RIGHT_TO_LEFT = 1


# =============================================================================
# Font Object Enums
# =============================================================================


class CTFontTechnology(IntEnum):
    """Font technology type.

    See: https://ae-scripting.docsforadobe.dev/text/fontobject/#fontobjecttechnology
    """

    CT_TYPE1_FONT = 0
    CT_TRUETYPE_FONT = 1
    CT_CID_FONT = 2
    CT_BITMAP_FONT = 3
    CT_ATC_FONT = 4
    CT_TYPE3_FONT = 5
    CT_SVG_FONT = 6
    CT_ANYTECHNOLOGY = 7


class CTFontType(IntEnum):
    """Font type.

    See: https://ae-scripting.docsforadobe.dev/text/fontobject/#fontobjecttype
    """

    CT_TYPE1_FONTTYPE = 0
    CT_TRUETYPE_FONTTYPE = 1
    CT_CID_FONTTYPE = 2
    CT_ATC_FONTTYPE = 3
    CT_BITMAP_FONTTYPE = 4
    CT_OPENTYPE_CFF_FONTTYPE = 5
    CT_OPENTYPE_CID_FONTTYPE = 6
    CT_OPENTYPE_TT_FONTTYPE = 7
    CT_TYPE3_FONTTYPE = 8
    CT_SVG_FONTTYPE = 9


class CTScript(IntEnum):
    """Character script/writing system.

    See: https://ae-scripting.docsforadobe.dev/text/fontobject/#fontobjectwritingscripts
    """

    CT_ROMAN_SCRIPT = 0
    CT_JAPANESE_SCRIPT = 1
    CT_TRADITIONALCHINESE_SCRIPT = 2
    CT_KOREAN_SCRIPT = 3
    CT_ARABIC_SCRIPT = 4
    CT_HEBREW_SCRIPT = 5
    CT_GREEK_SCRIPT = 6
    CT_CYRILLIC_SCRIPT = 7
    CT_RIGHTLEFT_SCRIPT = 8
    CT_DEVANAGARI_SCRIPT = 9
    CT_GURMUKHI_SCRIPT = 10
    CT_GUJARATI_SCRIPT = 11
    CT_ORIYA_SCRIPT = 12
    CT_BENGALI_SCRIPT = 13
    CT_TAMIL_SCRIPT = 14
    CT_TELUGU_SCRIPT = 15
    CT_KANNADA_SCRIPT = 16
    CT_MALAYALAM_SCRIPT = 17
    CT_SINHALESE_SCRIPT = 18
    CT_BURMESE_SCRIPT = 19
    CT_KHMER_SCRIPT = 20
    CT_THAI_SCRIPT = 21
    CT_LAOTIAN_SCRIPT = 22
    CT_GEORGIAN_SCRIPT = 23
    CT_ARMENIAN_SCRIPT = 24
    CT_SIMPLIFIEDCHINESE_SCRIPT = 25
    CT_TIBETAN_SCRIPT = 26
    CT_MONGOLIAN_SCRIPT = 27
    CT_GEEZ_SCRIPT = 28
    CT_EASTEUROPEANROMAN_SCRIPT = 29
    CT_VIETNAMESE_SCRIPT = 30
    CT_EXTENDEDARABIC_SCRIPT = 31
    CT_KLINGON_SCRIPT = 32
    CT_EMOJI_SCRIPT = 33
    CT_ROHINGYA_SCRIPT = 34
    CT_JAVANESE_SCRIPT = 35
    CT_SUNDANESE_SCRIPT = 36
    CT_LONTARA_SCRIPT = 37
    CT_SYRIAC_SCRIPT = 38
    CT_TAITHAM_SCRIPT = 39
    CT_BUGINESE_SCRIPT = 40
    CT_BALINESE_SCRIPT = 41
    CT_CHEROKEE_SCRIPT = 42
    CT_MANDAIC_SCRIPT = 43
    CT_VAI_SCRIPT = 44
    CT_THAANA_SCRIPT = 45
    CT_BRAVANESE_SCRIPT = 46
    CT_BRAHMI_SCRIPT = 47
    CT_CARIAN_SCRIPT = 48
    CT_CYPRIOT_SCRIPT = 49
    CT_EGYPTIAN_SCRIPT = 50
    CT_IMPERIALARAMAIC_SCRIPT = 51
    CT_PAHLAVI_SCRIPT = 52
    CT_PARTHIAN_SCRIPT = 53
    CT_KHAROSHTHI_SCRIPT = 54
    CT_LYCIAN_SCRIPT = 55
    CT_LYDIAN_SCRIPT = 56
    CT_PHOENICIAN_SCRIPT = 57
    CT_PERSIAN_SCRIPT = 58
    CT_SHAVIAN_SCRIPT = 59
    CT_SUMAKKCUNEIFORM_SCRIPT = 60
    CT_UGARITIC_SCRIPT = 61
    CT_GLAGOLITIC_SCRIPT = 62
    CT_GOTHIC_SCRIPT = 63
    CT_OGHAM_SCRIPT = 64
    CT_OLDITALIC_SCRIPT = 65
    CT_ORKHON_SCRIPT = 66
    CT_RUNIC_SCRIPT = 67
    CT_MEROITICCURSIVE_SCRIPT = 68
    CT_COPTIC_SCRIPT = 69
    CT_OLCHIKI_SCRIPT = 70
    CT_SORASOMPENG_SCRIPT = 71
    CT_OLDHANGUL_SCRIPT = 72
    CT_LISU_SCRIPT = 73
    CT_NKO_SCRIPT = 74
    CT_ADLAM_SCRIPT = 75
    CT_BAMUM_SCRIPT = 76
    CT_BASSAVAH_SCRIPT = 77
    CT_NEWA_SCRIPT = 78
    CT_NEWTAILU_SCRIPT = 79
    CT_SCRIPT = 80
    CT_OSAGE_SCRIPT = 81
    CT_UCAS_SCRIPT = 82
    CT_TIFINAGH_SCRIPT = 83
    CT_KAYAHLI_SCRIPT = 84
    CT_LAO_SCRIPT = 85
    CT_TAILE_SCRIPT = 86
    CT_TAIVIET_SCRIPT = 87
    CT_DONTKNOW_SCRIPT = 88
