class Marker(object):
    def __init__(self, name="", comment="", duration_frames=0, label_color=None, index=0):
        """
        Marker object of a layer
        """
        self.name = name
        self.comment = comment
        self.duration_frames = duration_frames
        self.label_color = label_color
        self.index = index

    def __repr__(self):
        return str(self.__dict__)
