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
        """
        Object storing information about a composition.
        Args:
            bg_color (list[float]): The background color of the composition. The three
                                    array values specify the red, green, and blue
                                    components of the color.
            display_start_frame (int): The frame value of the beginning of the
                                       composition.
            display_start_time (float): The time set as the beginning of the
                                        composition, in seconds. This is the equivalent
                                        of the Start Timecode or Start Frame setting in
                                        the Composition Settings dialog box.
            frame_blending (bool): When true, frame blending is enabled for this
                                   Composition. Corresponds to the value of the Frame
                                   Blending button in the Composition panel.
            hide_shy_layers (bool): When true, only layers with shy set to false are
                                    shown in the Timeline panel. When false, all layers
                                    are visible, including those whose shy value is
                                    true. Corresponds to the value of the Hide All Shy
                                    Layers button in the Composition panel.
            layers (list[Layer]): All the Layer objects for layers in this composition.
            markers (list[Marker]): All the composition's markers.
            motion_blur (bool): When true, motion blur is enabled for the composition.
                                Corresponds to the value of the Motion Blur button in
                                the Composition panel.
            motion_blur_adaptive_sample_limit (int): The maximum number of motion blur
                                                     samples of 2D layer motion. This
                                                     corresponds to the Adaptive Sample
                                                     Limit setting in the Advanced tab
                                                     of the Composition Settings dialog
                                                     box.
            motion_blur_samples_per_frame (int): The minimum number of motion blur
                                                 samples per frame for Classic 3D
                                                 layers, shape layers, and certain
                                                 effects. This corresponds to the
                                                 Samples Per Frame setting in the
                                                 Advanced tab of the Composition
                                                 Settings dialog box.
            preserve_nested_frame_rate (bool): When true, the frame rate of nested
                                               compositions is preserved in the current
                                               composition. Corresponds to the value of
                                               the “Preserve frame rate when nested or
                                               in render queue” option in the Advanced
                                               tab of the Composition Settings dialog
                                               box.
            preserve_nested_resolution (bool): When true, the resolution of nested
                                               compositions is preserved in the current
                                               composition. Corresponds to the value of
                                               the “Preserve Resolution When Nested”
                                               option in the Advanced tab of the
                                               Composition Settings dialog box.
            shutter_angle (int): The shutter angle setting for the composition. This
                                 corresponds to the Shutter Angle setting in the
                                 Advanced tab of the Composition Settings dialog box.
            shutter_phase (int): The shutter phase setting for the composition. This
                                 corresponds to the Shutter Phase setting in the
                                 Advanced tab of the Composition Settings dialog box.
            resolution_factor (list[int]): The x and y downsample resolution factors for
                                           rendering the composition. The two values in
                                           the array specify how many pixels to skip
                                           when sampling; the first number controls
                                           horizontal sampling, the second controls
                                           vertical sampling. Full resolution is [1, 1],
                                           half resolution is [2, 2], and quarter
                                           resolution is [4, 4]. The default is [1, 1].
            time_scale (int): The time scale, used as a divisor for some time values.
            in_point (float): The composition "in point" (seconds).  # TODO find a better definition
            frame_in_point (int): The composition "in point" (frames).  # TODO find a better definition
            out_point (float): The composition "out point" (seconds).  # TODO find a better definition
            frame_out_point (int): The composition "out point" (frames).  # TODO find a better definition
            frame_time (int): The playhead timestamp, in composition time (frame).
            time (float): The playhead timestamp, in composition time (seconds).
        """
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
        self.work_area_start = in_point - display_start_time
        self.frame_in_point = frame_in_point
        self.work_area_start_frame = frame_in_point - display_start_frame
        self.out_point = out_point
        self.frame_out_point = frame_out_point
        self.time = time
        self.frame_time = frame_time
        # TODO remove float stuff from kaitai instances and do it here ?
        # duration, in_point, display_start_time, time, frame_rate, work_area_start, out_point, pixel_aspect
        # same for other classes
        self.work_area_duration = self.out_point - self.in_point
        self.work_area_duration_frame = self.frame_out_point - self.frame_in_point

    def __iter__(self):
        """
        Returns:
            iter: An iterator over the composition's layers.
        """
        return iter(self.layers)

    def layer(self, name=None, index=None, other_layer=None, rel_index=None):
        """
        Args:
            name (str): The name of the layer to return.
            index (int): The index position of the layer to return.
            other_layer (Layer): A Layer object to use as a reference for the relative
                                 index position of the layer to return.
            rel_index (int): The index position of the layer relative to the other_layer
                             to return.
        Returns:
            Layer: The Layer object, which can be specified by name, an index position in
                   this composition, or an index position relative to another layer.
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
