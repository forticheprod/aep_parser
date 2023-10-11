class Marker(object):
    def __init__(self, time=0, name="", chapter="", url="", frame_target="",
                 flash_cue_point_name="", frame_duration=0, label=None, index=0,
                 protected=False, navigation=False, flash_cue_point_parameters=dict()):
        """
        Marker object of a layer
        """
        self.time = time
        self.name = name
        self.chapter = chapter
        self.url = url
        self.frame_target = frame_target
        self.flash_cue_point_name = flash_cue_point_name
        self.frame_duration = frame_duration
        self.label = label
        self.index = index
        self.protected = protected
        self.navigation = navigation
        self.flash_cue_point_parameters = flash_cue_point_parameters

    def __repr__(self):
        return str(self.__dict__)
