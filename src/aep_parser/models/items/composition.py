from .av_item import AVItem


class CompItem(AVItem):
    def __init__(self,
                 bg_color, display_start_frame, display_start_time, frame_blending,
                 hide_shy_layers, layers, markers, motion_blur,
                 motion_blur_adaptive_sample_limit, motion_blur_samples_per_frame,
                 preserve_nested_frame_rate, preserve_nested_resolution, shutter_angle,
                 shutter_phase, resolution_factor, time_scale,
                 in_point, frame_in_point, out_point, frame_out_point, frame_time, time,
                 *args, **kwargs):
        super(CompItem, self).__init__(*args, **kwargs)
        self.bg_color = bg_color
        self.display_start_frame = display_start_frame
        self.display_start_time = display_start_time
        self.frame_blending = frame_blending
        self.hide_shy_layers = hide_shy_layers
        self.layers = layers
        self.markers = markers
        self.motion_blur = motion_blur
        self.motion_blur_adaptive_sample_limit = motion_blur_adaptive_sample_limit
        self.motion_blur_samples_per_frame = motion_blur_samples_per_frame
        self.preserve_nested_frame_rate = preserve_nested_frame_rate
        self.preserve_nested_resolution = preserve_nested_resolution
        self.resolution_factor = resolution_factor
        self.shutter_angle = shutter_angle
        self.shutter_phase = shutter_phase
        self.time_scale = time_scale
        self.in_point = in_point
        self.work_area_start = in_point
        self.frame_in_point = frame_in_point
        self.work_area_start_frame = frame_in_point
        self.out_point = out_point
        self.frame_out_point = frame_out_point
        self.time = time
        self.frame_time = frame_time
        # TODO remove float stuff from kaitai instances and do it here ?
        # duration, in_point, display_start_time, time, frame_rate, work_area_start, out_point, pixel_aspect
        # same for other classes\
        self.work_area_duration = self.out_point - self.in_point
        self.work_area_duration_frame = self.frame_out_point - self.frame_in_point
        self.is_composition = True
        self.is_folder = False
        self.is_footage = False

    def __iter__(self):
        return iter(self.layers)

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

