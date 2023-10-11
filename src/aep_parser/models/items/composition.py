from .av_item import AVItem


class CompItem(AVItem):
    def __init__(self,
            asset_height=0,
            asset_width=0,
            background_color=[],
            composition_layers=[],
            duration_frames=0,
            duration_sec=0.0,
            frame_blend_enabled=False,
            framerate=0.0,
            height=0,
            in_time_frames=0,
            in_time_sec=0.0,
            markers=[],
            motion_blur_enabled=False,
            out_time_frames=0,
            out_time_sec=0.0,
            pixel_ratio=0,
            playhead_frames=0,
            playhead_sec=0.0,
            preserve_framerate=False,
            preserve_resolution=False,
            samples_limit=0,
            samples_per_frame=0,
            shutter_angle=0,
            shutter_phase=0,
            shy_enabled=False,
            time_scale=0,
            width=0,
            x_resolution=1,
            y_resolution=1,
            *args,
            **kwargs):
        super(CompItem, self).__init__(*args, **kwargs)
        self.x_resolution = x_resolution
        self.y_resolution = y_resolution
        self.time_scale = time_scale
        self.width = width
        self.height = height
        self.framerate = framerate
        self.playhead_sec = playhead_sec
        self.playhead_frames = playhead_frames
        self.in_time_sec = in_time_sec
        self.in_time_frames = in_time_frames
        self.out_time_frames = out_time_frames
        self.in_time_frames = in_time_frames
        self.duration_sec = duration_sec
        self.duration_frames = duration_frames
        self.background_color = background_color
        self.shy_enabled = shy_enabled
        self.motion_blur_enabled = motion_blur_enabled
        self.frame_blend_enabled = frame_blend_enabled
        self.preserve_framerate = preserve_framerate
        self.preserve_resolution = preserve_resolution
        self.asset_width = asset_width
        self.asset_height = asset_height
        self.pixel_ratio = pixel_ratio
        self.shutter_angle = shutter_angle
        self.shutter_phase = shutter_phase
        self.samples_limit = samples_limit
        self.samples_per_frame = samples_per_frame
        self.composition_layers = composition_layers
        self.markers = markers
