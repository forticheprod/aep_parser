from .av_item import AVItem


class FootageItem(AVItem):
    def __init__(self,
                 main_source, asset_type, end_frame, start_frame,
                 *args, **kwargs):
        """
        Footage item.
        Args:
            main_source (Any[FileSource, SolidSource, PlaceholderSource]): The footage source.
            asset_type (str): The footage type (placeholder, solid, file).
            end_frame (int): The footage end frame.
            start_frame (int): The footage start frame.
        """
        super(FootageItem, self).__init__(*args, **kwargs)
        self.main_source = main_source
        self.asset_type = asset_type
        self.end_frame = end_frame
        self.start_frame = start_frame

    @property
    def file(self):
        """
        Returns:
            str: The footage file path if it's source is a FileSource, else None.
        """
        try:
            return self.main_source.file
        except AttributeError:
            return None

    @property
    def is_composition(self):
        """
        Returns:
            bool: False.
        """
        return False

    @property
    def is_folder(self):
        """
        Returns:
            bool: False.
        """
        return False

    @property
    def is_footage(self):
        """
        Returns:
            bool: True.
        """
        return True
