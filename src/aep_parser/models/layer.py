class Layer(object):
    def __init__(self, index, name, source_id, quality, sampling_mode, frame_blend_mode, guide_enabled, solo_enabled, three_d_enabled, adjustment_layer_enabled, collapse_transform_enabled, shy_enabled, lock_enabled, frame_blend_enabled, motion_blur_enabled, effects_enabled, audio_enabled, video_enabled, effects=[], text):
        """
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
