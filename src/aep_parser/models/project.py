from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import xml.etree.ElementTree as ET
    from ..kaitai.aep import Aep
    from .items.composition import CompItem
    from .items.folder import Folder
    from .items.footage import FootageItem
    from .items.item import Item
    from .layers.layer import Layer


class Project:
    def __init__(
        self,
        bits_per_channel: Aep.BitsPerChannel,
        effect_names: list[str],
        expression_engine: str | None,
        file: str,
        footage_timecode_display_start_type: Aep.FootageTimecodeDisplayStartType,
        frame_rate: float,
        frames_count_type: Aep.FramesCountType,
        project_items: dict[int, Item],
        time_display_type: Aep.TimeDisplayType,
        ae_version: str | None = None,
        xmp_packet: ET.Element | None = None,
    ):
        """Object storing information about an After Effects project.

        Args:
            ae_version: The version of After Effects that created the project.
            bits_per_channel: The color depth of the current project, either
                8, 16, or 32 bits.
            effect_names: The names of all effects used in the project.
            expression_engine: The Expressions Engine setting in the Project
                Settings dialog box ("extendscript" or "javascript-1.0").
            file: The full path to the project file.
            footage_timecode_display_start_type: The Footage Start Time
                setting in the Project Settings dialog box, which is enabled
                when Timecode is selected as the time display style.
            frame_rate: The frame rate of the project.
            frames_count_type: The Frame Count menu setting in the Project
                Settings dialog box.
            project_items: All the items in the project.
            time_display_type: The time display style, corresponding to the
                Time Display Style section in the Project Settings dialog box.
            xmp_packet: The XMP packet for the project, containing metadata.
        """
        self.ae_version = ae_version
        self.bits_per_channel = bits_per_channel
        self.effect_names = effect_names
        self.expression_engine = expression_engine
        self.file = file
        self.footage_timecode_display_start_type = footage_timecode_display_start_type
        self.frame_rate = frame_rate
        self.frames_count_type = frames_count_type
        self.project_items = project_items
        self.time_display_type = time_display_type
        self.xmp_packet = xmp_packet

        self.display_start_frame = frames_count_type.value % 2
        self._layers_by_uid = None
        self._compositions = None
        self._folders = None
        self._footages = None

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return str(self.__dict__)

    def __iter__(self) -> typing.Iterator[Item]:
        """Return an iterator over the project's items."""
        return iter(self.project_items.values())

    def layer_by_id(self, layer_id: int) -> Layer:
        """Get a layer by its unique ID."""
        if self._layers_by_uid is None:
            self._layers_by_uid = {
                layer.layer_id: layer
                for comp in self.compositions
                for layer in comp.layers
            }
        return self._layers_by_uid[layer_id]

    @property
    def root_folder(self) -> Folder:
        """
        The root folder.

        This is a virtual folder that contains all items in the Project panel,
        but not items contained inside other folders in the Project panel.
        """
        return self.project_items[0]

    @property
    def compositions(self) -> list[CompItem]:
        """All the compositions in the project."""
        if self._compositions is None:
            self._compositions = [
                item for item in self.project_items.values() if item.is_composition
            ]
        return self._compositions

    def composition(self, name: str) -> CompItem | None:
        """Get a composition by name."""
        for comp in self.compositions:
            if comp.name == name:
                return comp

    @property
    def folders(self) -> list[Folder]:
        """All the folders in the project."""
        if self._folders is None:
            self._folders = [
                item for item in self.project_items.values() if item.is_folder
            ]
        return self._folders

    def folder(self, name: str) -> Folder | None:
        """Get a folder by name."""
        for folder in self.folders:
            if folder.name == name:
                return folder

    @property
    def footages(self) -> list[FootageItem]:
        """All the footages in the project."""
        if self._footages is None:
            self._footages = [
                item for item in self.project_items.values() if item.is_footage
            ]
        return self._footages

    def footage(self, name: str) -> FootageItem | None:
        """Get a footage by name."""
        for footage in self.footages:
            if footage.name == name:
                return footage
