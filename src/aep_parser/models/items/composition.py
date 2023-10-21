from .av_item import AVItem


class CompItem(AVItem):
    def __init__(self,
                 bg_color, frame_blending, layers, markers, motion_blur,
                 motion_blur_adaptive_sample_limit, motion_blur_samples_per_frame,
                 preserve_nested_frame_rate, preserve_nested_resolution, shutter_angle,
                 shutter_phase, resolution_factor, time_scale,
                 # in_point_frames, in_point, out_point_frames, out_point,
                 # playhead_frames, playhead_sec, shy,
            *args, **kwargs):
        super(CompItem, self).__init__(*args, **kwargs)
        self.bg_color = bg_color
        self.layers = layers
        # TODO displayStartFrame
        # TODO displayStartTime
        self.frame_blending = frame_blending
        # TODO hideShyLayers (== shy ?)
        # self.in_point_frames = in_point_frames
        # self.in_point = in_point
        self.markers = markers
        self.motion_blur = motion_blur
        # self.out_point_frames = out_point_frames
        # self.playhead_frames = playhead_frames
        # self.playhead_sec = playhead_sec
        self.preserve_nested_frame_rate = preserve_nested_frame_rate
        self.preserve_nested_resolution = preserve_nested_resolution
        self.motion_blur_adaptive_sample_limit = motion_blur_adaptive_sample_limit
        self.motion_blur_samples_per_frame = motion_blur_samples_per_frame
        self.shutter_angle = shutter_angle
        self.shutter_phase = shutter_phase
        # self.shy = shy
        self.resolution_factor = resolution_factor
        self.time_scale = time_scale
        # TODO workAreaDuration (== out - in + 1 ?)
        # TODO workAreaStart (== in_point ?)

    def layer(self, name=None, index=None, other_layer=None, rel_index=None):
        """
        Returns a Layer object, which can be specified by name, an index position in
        this layer, or an index position relative to another layer.
        """
        if name:
            for layer in self.layers:
                if layer.name == name:
                    return layer
            return None
        elif index:
            return self.layers[index]
        elif other_layer and rel_index:
            return self.layers[self.layers.index(other_layer) + rel_index]
        else:
            return None

