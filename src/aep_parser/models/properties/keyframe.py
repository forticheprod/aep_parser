class Keyframe(object):
    def __init__(self, time=0, ease_mode=None, label_color=None, index=0,
                 continuous_bezier=False, auto_bezier=False, roving_across_time=False):
        """
        Keyframe of a property.
        """
        self.time = time
        self.ease_mode = ease_mode
        self.label_color = label_color
        self.index = index
        self.continuous_bezier = continuous_bezier
        self.auto_bezier = auto_bezier
        self.roving_across_time = roving_across_time

    def __repr__(self):
        return str(self.__dict__)
