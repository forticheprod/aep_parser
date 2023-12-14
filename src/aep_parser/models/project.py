from __future__ import absolute_import, unicode_literals, division
from builtins import str


class Project(object):
    def __init__(
        self,
        bits_per_channel,
        effect_names,
        expression_engine,
        file,
        footage_timecode_display_start_type,
        frame_rate,
        frames_count_type,
        project_items,
        time_display_type,
        ae_version=None,
        xmp_packet=None,
    ):
        """
        Args:
            ae_version (str): The version of After Effects that created the project.
            bits_per_channel (Aep.BitsPerChannel): The color depth of the current
                                                   project, either 8, 16, or 32 bits.
            effect_names (list[str]): The names of all effects used in the project.
            expression_engine (str): The Expressions Engine setting in the Project
                                     Settings dialog box ("extendscript" or
                                     "javascript-1.0")
            file (str): The full path to the project file.
            footage_timecode_display_start_type (Aep.FootageTimecodeDisplayStartType):
                The Footage Start Time setting in the Project Settings dialog box, which
                is enabled when Timecode is selected as the time display style.
            frame_rate (float): The frame rate of the project.
            frames_count_type (Aep.FramesCountType): The Frame Count menu setting in the
                                                     Project Settings dialog box.
            project_items (dict[int, Item]): All the items in the project.
            time_display_type (Aep.TimeDisplayType): The time display style,
                                                     corresponding to the Time Display
                                                     Style section in the Project
                                                     Settings dialog box.
            xmp_packet (xml.etree.ElementTree.Element): The XMP packet for the project,
                                                        containing some metadata.
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

    def __repr__(self):
        """
        Returns:
            str: A string representation of the object.
        """
        return str(self.__dict__)

    def __iter__(self):
        """
        Returns:
            iter: An iterator over the project's items (compositions, footages, folders).
        """
        return iter(self.project_items.values())

    def layer_by_id(self, layer_id):
        """
        Args:
            layer_id (int): The layer's ID.
        Returns:
            models.layers.Layer: The layer whose unique ID is `layer_id`.
        """
        if self._layers_by_uid is None:
            self._layers_by_uid = {
                layer.layer_id: layer
                for comp in self.compositions
                for layer in comp.layers
            }
        return self._layers_by_uid[layer_id]

    @property
    def root_folder(self):
        """
        Returns:
            Folder: The root folder. This is a virtual folder that contains all items in
                    the Project panel, but not items contained inside other folders in
                    the Project panel.
        """
        return self.project_items[0]

    @property
    def compositions(self):
        """
        Returns:
            list[CompItem]: All the compositions in the project.
        """
        if self._compositions is None:
            self._compositions = [
                item for item in self.project_items.values() if item.is_composition
            ]
        return self._compositions

    def composition(self, name):
        """
        Args:
            name (str): The name of the composition.
        Returns:
            CompItem: The composition whose name is `name`.
        """
        for comp in self.compositions:
            if comp.name == name:
                return comp

    @property
    def folders(self):
        """
        Returns:
            list[Folder]: All the folders in the project.
        """
        if self._folders is None:
            self._folders = [
                item for item in self.project_items.values() if item.is_folder
            ]
        return self._folders

    def folder(self, name):
        """
        Args:
            name (str): The name of the folder.
        Returns:
            Folder: The folder whose name is `name`.
        """
        for folder in self.folders:
            if folder.name == name:
                return folder

    @property
    def footages(self):
        """
        Returns:
            list[FootageItem]: All the footages in the project.
        """
        if self._footages is None:
            self._footages = [
                item for item in self.project_items.values() if item.is_footage
            ]
        return self._footages

    def footage(self, name):
        """
        Args:
            name (str): The name of the footage.
        Returns:
            FootageItem: The footage whose name is `name`.
        """
        for footage in self.footages:
            if footage.name == name:
                return footage
