class Layer(object):
    def __init__(
            self,
            name="",
            layer_id=None,
            index=0,
            quality=None,
            stretch_numerator=0,
            start_time_sec=None,
            in_time_sec=None,
            out_time_sec=None,
            source_id=0,
            label_color=0,
            matte_mode=0,
            stretch_denominator=0,
            layer_type=0,
            parent_id=0,
            guide_enabled=False,
            frame_blend_mode=None,
            sampling_mode=None,
            auto_orient=False,
            adjustment_layer_enabled=False,
            three_d_enabled=False,
            solo_enabled=False,
            null_layer=False,
            video_enabled=False,
            audio_enabled=False,
            effects_enabled=False,
            motion_blur_enabled=False,
            frame_blend_enabled=False,
            lock_enabled=False,
            shy_enabled=False,
            collapse_transform_enabled=False,
            text=None,
            effects=[],
            markers=[],
            transform=[]):
        """
        A single layer in a composition
        """
        self.name = name
        self.layer_id = layer_id
        self.index = index
        self.quality = quality
        self.stretch_numerator = stretch_numerator
        self.start_time_sec = start_time_sec
        self.in_time_sec = in_time_sec
        self.out_time_sec = out_time_sec
        self.source_id = source_id
        self.label_color = label_color
        self.matte_mode = matte_mode
        self.stretch_denominator = stretch_denominator
        self.layer_type = layer_type
        self.parent_id = parent_id
        self.guide_enabled = guide_enabled
        self.frame_blend_mode = frame_blend_mode
        self.sampling_mode = sampling_mode
        self.auto_orient = auto_orient
        self.adjustment_layer_enabled = adjustment_layer_enabled
        self.three_d_enabled = three_d_enabled
        self.solo_enabled = solo_enabled
        self.null_layer = null_layer
        self.video_enabled = video_enabled
        self.audio_enabled = audio_enabled
        self.effects_enabled = effects_enabled
        self.motion_blur_enabled = motion_blur_enabled
        self.frame_blend_enabled = frame_blend_enabled
        self.lock_enabled = lock_enabled
        self.shy_enabled = shy_enabled
        self.collapse_transform_enabled = collapse_transform_enabled
        self.text = text
        self.effects = effects
        self.markers = markers
        self.transform = transform

    def __repr__(self):
        return str(self.__dict__)
