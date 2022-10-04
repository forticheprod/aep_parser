class Layer(object):
    def __init__(self, index=0, name="", source_id=0, quality=None, sampling_mode=None,
                 frame_blend_mode=None, guide_enabled=False, solo_enabled=False,
                 three_d_enabled=False, adjustment_layer_enabled=False,
                 collapse_transform_enabled=False, shy_enabled=False,
                 lock_enabled=False, frame_blend_enabled=False,
                 motion_blur_enabled=False, effects_enabled=False, audio_enabled=False,
                 video_enabled=False, text=None, effects=[]):
        """
        A single layer in a composition
        """
        self.index = index
        self.name = name
        self.source_id = source_id
        self.quality = quality
        self.sampling_mode = sampling_mode
        self.frame_blend_mode = frame_blend_mode
        self.guide_enabled = guide_enabled
        self.solo_enabled = solo_enabled
        self.three_d_enabled = three_d_enabled
        self.adjustment_layer_enabled = adjustment_layer_enabled
        self.collapse_transform_enabled = collapse_transform_enabled
        self.shy_enabled = shy_enabled
        self.lock_enabled = lock_enabled
        self.frame_blend_enabled = frame_blend_enabled
        self.motion_blur_enabled = motion_blur_enabled
        self.effects_enabled = effects_enabled
        self.audio_enabled = audio_enabled
        self.video_enabled = video_enabled
        self.effects = effects
        self.text = text

    def __repr__(self):
        return str(self.__dict__)
