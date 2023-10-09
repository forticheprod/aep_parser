class Marker(object):
    def __init__(self, name="", chapter="", url="", frame_target="",
                 flash_cue_point_name="", duration_frames=0, label_color=None, index=0,
                 protected=False, navigation=False, flash_cue_point_parameters=dict()):
        """
        Marker object of a layer
        """
        self.name = name
        self.chapter = chapter
        self.url = url
        self.frame_target = frame_target
        self.flash_cue_point_name = flash_cue_point_name
        self.duration_frames = duration_frames
        self.label_color = label_color
        self.index = index
        self.protected = protected
        self.navigation = navigation
        self.flash_cue_point_parameters = flash_cue_point_parameters

    def __repr__(self):
        return str(self.__dict__)
