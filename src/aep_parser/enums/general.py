"""General After Effects enumerations.

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


class PlayMode(IntEnum):
    """Playback mode for preview.

    Not documented in AE scripting reference.
    """

    SPACEBAR = 8212
    RAM_PREVIEW = 8213


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
