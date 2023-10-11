class Keyframe(object):
    def __init__(self, index=0, time=0, ease_mode=None, label_color=None,
                 continuous_bezier=False, auto_bezier=False, roving_across_time=False):
        """
        Keyframe of a property.
        """
        self.index = index
        self.time = time
        self.ease_mode = ease_mode
        self.label_color = label_color
        self.continuous_bezier = continuous_bezier
        self.auto_bezier = auto_bezier
        self.roving_across_time = roving_across_time

    def __repr__(self):
        return str(self.__dict__)
