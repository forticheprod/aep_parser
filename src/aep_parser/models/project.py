from __future__ import annotations

import typing
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from .items.composition import CompItem
from .items.folder import FolderItem
from .items.footage import FootageItem

if typing.TYPE_CHECKING:
    import xml.etree.ElementTree as ET

    from .enums import (
        BitsPerChannel,
        ColorManagementSystem,
        FeetFramesFilmType,
        FootageTimecodeDisplayStartType,
        FramesCountType,
        LutInterpolationMethod,
        TimeDisplayType,
    )
    from .items.item import Item
    from .layers.layer import Layer
    from .renderqueue.render_queue import RenderQueue
    from .viewer.viewer import Viewer


@dataclass
class Project:
    """
    The `Project` object represents an After Effects project. Attributes
    provide access to specific objects within the project, such as imported
    files or footage and compositions, and also to project settings such as the
    timecode base.

    See: https://ae-scripting.docsforadobe.dev/general/project/
    """

    ae_version: str
    """
    The version of After Effects that created the project, formatted as
    "{major}.{minor}x{build}" (e.g., "25.2x26").
    """

    ae_build_number: int
    """The build number of After Effects that created the project."""

    bits_per_channel: BitsPerChannel
    """The color depth of the current project, either 8, 16, or 32 bits."""

    color_management_system: ColorManagementSystem
    """
    The color management system used by the project (Adobe or OCIO). Available
    in CC 2024 and later.
    """

    compensate_for_scene_referred_profiles: bool
    """
    When True, After Effects compensates for scene-referred profiles when
    rendering.
    """

    effect_names: list[str]
    """The names of all effects used in the project."""

    expression_engine: str
    """
    The Expressions Engine setting in the Project Settings dialog box
    ("extendscript" or "javascript-1.0").
    """

    feet_frames_film_type: FeetFramesFilmType
    """
    The film type for feet+frames timecode display, either MM16 (16mm) or MM35
    (35mm).
    """

    lut_interpolation_method: LutInterpolationMethod
    """
    The LUT interpolation method for the project (Trilinear or Tetrahedral).
    """

    ocio_configuration_file: str
    """
    The OCIO configuration file for the project. Only relevant when
    color_management_system is OCIO.
    """

    file: str
    """The full path to the project file."""

    footage_timecode_display_start_type: FootageTimecodeDisplayStartType
    """
    The Footage Start Time setting in the Project Settings dialog box, which
    is enabled when Timecode is selected as the time display style.
    """

    frame_rate: float
    """The frame rate of the project."""

    frames_count_type: FramesCountType
    """The Frame Count menu setting in the Project Settings dialog box."""

    frames_use_feet_frames: bool
    """When True, the Frames field in the UI is displayed as feet+frames."""

    linear_blending: bool
    """
    When True, linear blending is used for the project. When False, the
    standard blending mode is used.
    """

    linearize_working_space: bool
    """
    When True, the working color space is linearized for blending operations.
    """

    working_gamma: float
    """The gamma value used for the working color space, typically 2.2 or 2.4."""

    working_space: str
    """The name of the working color space (e.g., "sRGB IEC61966-2.1", "None")."""

    items: dict[int, Item] = field(repr=False)  # These items are in root_folder already
    """All the items in the project."""

    render_queue: RenderQueue | None
    """The Render Queue of the project."""

    time_display_type: TimeDisplayType
    """
    The time display style, corresponding to the Time Display Style section
    in the Project Settings dialog box.
    """

    transparency_grid_thumbnails: bool
    """
    When `True`, thumbnail views use the transparency checkerboard pattern.
    """

    xmp_packet: ET.Element
    """The XMP packet for the project, containing metadata."""

    active_item: Item | None = None
    """
    The item that is currently active and is to be acted upon, or `None` if no
    item is currently selected or if multiple items are selected.
    """

    active_viewer: Viewer | None = None
    """
    The currently focused Viewer panel, or `None` if no viewer is active.
    """

    display_start_frame: int = field(init=False)
    """The start frame number for the project display."""

    project_name: str = field(init=False)
    """The name of the project, derived from the file name."""

    root_folder: FolderItem | None = None
    """
    The root folder. This is a virtual folder that contains all items in the
    Project panel, but not items contained inside other folders in the Project
    panel.
    """
    _layers_by_uid: dict[int, Layer] | None = field(
        default=None, init=False, repr=False
    )
    _compositions: list[CompItem] | None = field(default=None, init=False, repr=False)
    _folders: list[FolderItem] | None = field(default=None, init=False, repr=False)
    _footages: list[FootageItem] | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Set computed fields after initialization."""
        self.display_start_frame = self.frames_count_type.value % 2
        self.project_name = Path(self.file).name

    def __iter__(self) -> typing.Iterator[Item]:
        """Return an iterator over the project's items."""
        return iter(self.items.values())

    def layer_by_id(self, layer_id: int) -> Layer:
        """Get a layer by its unique ID."""
        if self._layers_by_uid is None:
            self._layers_by_uid = {
                layer.id: layer
                for comp in self.compositions
                for layer in comp.layers
            }
        return self._layers_by_uid[layer_id]

    @property
    def compositions(self) -> list[CompItem]:
        """All the compositions in the project."""
        if self._compositions is None:
            self._compositions = [
                cast(CompItem, item)
                for item in self.items.values()
                if item.is_composition
            ]
        return self._compositions

    @property
    def folders(self) -> list[FolderItem]:
        """All the folders in the project."""
        if self._folders is None:
            self._folders = [
                cast(FolderItem, item)
                for item in self.items.values()
                if item.is_folder
            ]
        return self._folders

    @property
    def footages(self) -> list[FootageItem]:
        """All the footages in the project."""
        if self._footages is None:
            self._footages = [
                cast(FootageItem, item)
                for item in self.items.values()
                if item.is_footage
            ]
        return self._footages
