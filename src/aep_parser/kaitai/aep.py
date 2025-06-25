# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Aep(KaitaiStruct):

    class TimeDisplayType(Enum):
        timecode = 0
        frames = 1

    class PropertyControlType(Enum):
        layer = 0
        scalar = 2
        angle = 3
        boolean = 4
        color = 5
        two_d = 6
        enum = 7
        paint_group = 9
        slider = 10
        curve = 11
        group = 13
        unknown = 15
        three_d = 18

    class FootageTimecodeDisplayStartType(Enum):
        ftcs_start_0 = 0
        ftcs_use_source_media = 1

    class BlendingMode(Enum):
        normal = 2
        dissolve = 3
        add = 4
        multiply = 5
        screen = 6
        overlay = 7
        soft_light = 8
        hard_light = 9
        darken = 10
        lighten = 11
        classic_difference = 12
        hue = 13
        saturation = 14
        color = 15
        luminosity = 16
        stencil_alpha = 17
        stencil_luma = 18
        silhouette_alpha = 19
        silhouette_luma = 20
        luminescent_premul = 21
        alpha_add = 22
        classic_color_dodge = 23
        classic_color_burn = 24
        exclusion = 25
        difference = 26
        color_dodge = 27
        color_burn = 28
        linear_dodge = 29
        linear_burn = 30
        linear_light = 31
        vivid_light = 32
        pin_light = 33
        hard_mix = 34
        lighter_color = 35
        darker_color = 36
        subtract = 37
        divide = 38

    class Label(Enum):
        none = 0
        red = 1
        yellow = 2
        aqua = 3
        pink = 4
        lavender = 5
        peach = 6
        sea_foam = 7
        blue = 8
        green = 9
        purple = 10
        orange = 11
        brown = 12
        fuchsia = 13
        cyan = 14
        sandstone = 15
        dark_green = 16

    class BitsPerChannel(Enum):
        bpc_8 = 0
        bpc_16 = 1
        bpc_32 = 2

    class AssetType(Enum):
        placeholder = 2
        solid = 9

    class TrackMatteType(Enum):
        none = 0
        no_track_matte = 1
        alpha = 2
        alpha_inverted = 3
        luma = 4
        luma_inverted = 5

    class LayerType(Enum):
        footage = 0
        light = 1
        camera = 2
        text = 3
        shape = 4

    class FramesCountType(Enum):
        fc_start_0 = 0
        fc_start_1 = 1
        fc_timecode_conversion = 2

    class KeyframeInterpolationType(Enum):
        linear = 1
        bezier = 2
        hold = 3

    class FrameBlendingType(Enum):
        frame_mix = 0
        pixel_motion = 1
        no_frame_blend = 2

    class PropertyValueType(Enum):
        unknown = 0
        no_value = 1
        three_d_spatial = 2
        three_d = 3
        two_d_spatial = 4
        two_d = 5
        one_d = 6
        color = 7
        custom_value = 8
        marker = 9
        layer_index = 10
        mask_index = 11
        shape = 12
        text_document = 13
        lrdr = 14
        litm = 15
        gide = 16
        orientation = 17

    class SamplingQuality(Enum):
        bilinear = 0
        bicubic = 1

    class ItemType(Enum):
        folder = 1
        composition = 4
        footage = 7

    class LayerQuality(Enum):
        wireframe = 0
        draft = 1
        best = 2
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header = self._io.read_bytes(4)
        if not self.header == b"\x52\x49\x46\x58":
            raise kaitaistruct.ValidationNotEqualError(b"\x52\x49\x46\x58", self.header, self._io, u"/seq/0")
        self.len_data = self._io.read_u4be()
        self.format = self._io.read_bytes(4)
        if not self.format == b"\x45\x67\x67\x21":
            raise kaitaistruct.ValidationNotEqualError(b"\x45\x67\x67\x21", self.format, self._io, u"/seq/2")
        self._raw_data = self._io.read_bytes((self.len_data - 4))
        _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
        self.data = Aep.Chunks(_io__raw_data, self, self._root)
        self.xmp_packet = (self._io.read_bytes_full()).decode(u"utf8")

    class Keyframe(KaitaiStruct):
        def __init__(self, key_type, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.key_type = key_type
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(1)
            self.time_raw = self._io.read_u2be()
            self._unnamed2 = self._io.read_bytes(2)
            self.keyframe_interpolation_type = KaitaiStream.resolve_enum(Aep.KeyframeInterpolationType, self._io.read_u1())
            self.label = KaitaiStream.resolve_enum(Aep.Label, self._io.read_u1())
            self._unnamed5 = self._io.read_bits_int_be(2)
            self.roving_across_time = self._io.read_bits_int_be(1) != 0
            self.auto_bezier = self._io.read_bits_int_be(1) != 0
            self.continuous_bezier = self._io.read_bits_int_be(1) != 0
            self._unnamed9 = self._io.read_bits_int_be(3)
            self._io.align_to_byte()
            _on = self.key_type
            if _on == Aep.PropertyValueType.marker:
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
            elif _on == Aep.PropertyValueType.unknown:
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
            elif _on == Aep.PropertyValueType.no_value:
                self.kf_data = Aep.KfNoValue(self._io, self, self._root)
            elif _on == Aep.PropertyValueType.three_d:
                self.kf_data = Aep.KfMultiDimensional(3, self._io, self, self._root)
            elif _on == Aep.PropertyValueType.litm:
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
            elif _on == Aep.PropertyValueType.three_d_spatial:
                self.kf_data = Aep.KfPosition(3, self._io, self, self._root)
            elif _on == Aep.PropertyValueType.orientation:
                self.kf_data = Aep.KfMultiDimensional(1, self._io, self, self._root)
            elif _on == Aep.PropertyValueType.two_d_spatial:
                self.kf_data = Aep.KfPosition(2, self._io, self, self._root)
            elif _on == Aep.PropertyValueType.lrdr:
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
            elif _on == Aep.PropertyValueType.one_d:
                self.kf_data = Aep.KfMultiDimensional(1, self._io, self, self._root)
            elif _on == Aep.PropertyValueType.gide:
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
            elif _on == Aep.PropertyValueType.two_d:
                self.kf_data = Aep.KfMultiDimensional(2, self._io, self, self._root)
            elif _on == Aep.PropertyValueType.color:
                self.kf_data = Aep.KfColor(self._io, self, self._root)


    class ChildUtf8Body(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.chunk = Aep.Chunk(self._io, self, self._root)


    class Chunk(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.chunk_type = (self._io.read_bytes(4)).decode(u"ascii")
            self.len_data = self._io.read_u4be()
            _on = self.chunk_type
            if _on == u"head":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.HeadBody(_io__raw_data, self, self._root)
            elif _on == u"cdat":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.CdatBody(_io__raw_data, self, self._root)
            elif _on == u"pard":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.PardBody(_io__raw_data, self, self._root)
            elif _on == u"Utf8":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"nnhd":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.NnhdBody(_io__raw_data, self, self._root)
            elif _on == u"ldta":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.LdtaBody(_io__raw_data, self, self._root)
            elif _on == u"NmHd":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.NmhdBody(_io__raw_data, self, self._root)
            elif _on == u"alas":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"idta":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.IdtaBody(_io__raw_data, self, self._root)
            elif _on == u"tdmn":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"LIST":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ListBody(_io__raw_data, self, self._root)
            elif _on == u"fnam":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
            elif _on == u"tdsb":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.TdsbBody(_io__raw_data, self, self._root)
            elif _on == u"fdta":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.FdtaBody(_io__raw_data, self, self._root)
            elif _on == u"lhd3":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Lhd3Body(_io__raw_data, self, self._root)
            elif _on == u"tdsn":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
            elif _on == u"cdta":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.CdtaBody(_io__raw_data, self, self._root)
            elif _on == u"tdb4":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Tdb4Body(_io__raw_data, self, self._root)
            elif _on == u"pjef":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"cmta":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"sspc":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.SspcBody(_io__raw_data, self, self._root)
            elif _on == u"pdnm":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
            elif _on == u"opti":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.OptiBody(_io__raw_data, self, self._root)
            elif _on == u"ldat":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.LdatBody(_io__raw_data, self, self._root)
            else:
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.AsciiBody(_io__raw_data, self, self._root)
            if (self.len_data % 2) != 0:
                self.padding = self._io.read_bytes(1)



    class Lhd3Body(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(10)
            self.nb_keyframes = self._io.read_u2be()
            self._unnamed2 = self._io.read_bytes(6)
            self.len_keyframe = self._io.read_u2be()
            self._unnamed4 = self._io.read_bytes(3)
            self.keyframes_type_raw = self._io.read_u1()

        @property
        def keyframes_type(self):
            if hasattr(self, '_m_keyframes_type'):
                return self._m_keyframes_type

            self._m_keyframes_type = (Aep.PropertyValueType.lrdr if  ((self.keyframes_type_raw == 1) and (self.len_keyframe == 2246))  else (Aep.PropertyValueType.litm if  ((self.keyframes_type_raw == 1) and (self.len_keyframe == 128))  else (Aep.PropertyValueType.gide if  ((self.keyframes_type_raw == 2) and (self.len_keyframe == 1))  else (Aep.PropertyValueType.color if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 152))  else (Aep.PropertyValueType.three_d if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 128))  else (Aep.PropertyValueType.two_d_spatial if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 104))  else (Aep.PropertyValueType.two_d if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 88))  else (Aep.PropertyValueType.orientation if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 80))  else (Aep.PropertyValueType.no_value if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 64))  else (Aep.PropertyValueType.one_d if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 48))  else (Aep.PropertyValueType.marker if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 16))  else Aep.PropertyValueType.unknown)))))))))))
            return getattr(self, '_m_keyframes_type', None)


    class ListBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.list_type = (self._io.read_bytes(4)).decode(u"cp1250")
            if self.list_type != u"btdk":
                self.chunks = []
                i = 0
                while not self._io.is_eof():
                    self.chunks.append(Aep.Chunk(self._io, self, self._root))
                    i += 1


            if self.list_type == u"btdk":
                self.binary_data = self._io.read_bytes_full()



    class CdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.resolution_factor = []
            for i in range(2):
                self.resolution_factor.append(self._io.read_u2be())

            self._unnamed1 = self._io.read_bytes(1)
            self.time_scale = self._io.read_u2be()
            self._unnamed3 = self._io.read_bytes(2)
            self.frame_rate_dividend = self._io.read_u2be()
            self._unnamed5 = self._io.read_bytes(10)
            self.time_raw = self._io.read_u2be()
            self._unnamed7 = self._io.read_bytes(6)
            self.in_point_raw = self._io.read_u2be()
            self._unnamed9 = self._io.read_bytes(6)
            self.out_point_raw = self._io.read_u2be()
            self._unnamed11 = self._io.read_bytes(5)
            self.duration_dividend = self._io.read_u4be()
            self.duration_divisor = self._io.read_u4be()
            self.bg_color = []
            for i in range(3):
                self.bg_color.append(self._io.read_u1())

            self._unnamed15 = self._io.read_bytes(84)
            self.preserve_nested_resolution = self._io.read_bits_int_be(1) != 0
            self._unnamed17 = self._io.read_bits_int_be(1) != 0
            self.preserve_nested_frame_rate = self._io.read_bits_int_be(1) != 0
            self.frame_blending = self._io.read_bits_int_be(1) != 0
            self.motion_blur = self._io.read_bits_int_be(1) != 0
            self._unnamed21 = self._io.read_bits_int_be(2)
            self.hide_shy_layers = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.width = self._io.read_u2be()
            self.height = self._io.read_u2be()
            self.pixel_ratio_width = self._io.read_u4be()
            self.pixel_ratio_height = self._io.read_u4be()
            self._unnamed27 = self._io.read_bytes(4)
            self.frame_rate_integer = self._io.read_u2be()
            self._unnamed29 = self._io.read_bytes(6)
            self.display_start_time_dividend = self._io.read_u4be()
            self.display_start_time_divisor = self._io.read_u4be()
            self._unnamed32 = self._io.read_bytes(2)
            self.shutter_angle = self._io.read_u2be()
            self.shutter_phase = self._io.read_u4be()
            self._unnamed35 = self._io.read_bytes(16)
            self.motion_blur_adaptive_sample_limit = self._io.read_s4be()
            self.motion_blur_samples_per_frame = self._io.read_s4be()

        @property
        def pixel_aspect(self):
            if hasattr(self, '_m_pixel_aspect'):
                return self._m_pixel_aspect

            self._m_pixel_aspect = (self.pixel_ratio_width / self.pixel_ratio_height)
            return getattr(self, '_m_pixel_aspect', None)

        @property
        def out_point(self):
            if hasattr(self, '_m_out_point'):
                return self._m_out_point

            self._m_out_point = (self.frame_out_point / self.frame_rate)
            return getattr(self, '_m_out_point', None)

        @property
        def frame_out_point(self):
            if hasattr(self, '_m_frame_out_point'):
                return self._m_frame_out_point

            self._m_frame_out_point = (self.display_start_frame + (self.frame_duration if self.out_point_raw == 65535 else self.out_point_raw // self.time_scale))
            return getattr(self, '_m_frame_out_point', None)

        @property
        def frame_duration(self):
            if hasattr(self, '_m_frame_duration'):
                return self._m_frame_duration

            self._m_frame_duration = (self.duration * self.frame_rate)
            return getattr(self, '_m_frame_duration', None)

        @property
        def frame_rate(self):
            if hasattr(self, '_m_frame_rate'):
                return self._m_frame_rate

            self._m_frame_rate = (self.frame_rate_dividend / self.time_scale)
            return getattr(self, '_m_frame_rate', None)

        @property
        def display_start_time(self):
            if hasattr(self, '_m_display_start_time'):
                return self._m_display_start_time

            self._m_display_start_time = (self.display_start_time_dividend / self.display_start_time_divisor)
            return getattr(self, '_m_display_start_time', None)

        @property
        def duration(self):
            if hasattr(self, '_m_duration'):
                return self._m_duration

            self._m_duration = (self.duration_dividend / self.duration_divisor)
            return getattr(self, '_m_duration', None)

        @property
        def time(self):
            if hasattr(self, '_m_time'):
                return self._m_time

            self._m_time = (self.frame_time / self.frame_rate)
            return getattr(self, '_m_time', None)

        @property
        def in_point(self):
            if hasattr(self, '_m_in_point'):
                return self._m_in_point

            self._m_in_point = (self.frame_in_point / self.frame_rate)
            return getattr(self, '_m_in_point', None)

        @property
        def frame_time(self):
            if hasattr(self, '_m_frame_time'):
                return self._m_frame_time

            self._m_frame_time = self.time_raw // self.time_scale
            return getattr(self, '_m_frame_time', None)

        @property
        def display_start_frame(self):
            if hasattr(self, '_m_display_start_frame'):
                return self._m_display_start_frame

            self._m_display_start_frame = (self.display_start_time * self.frame_rate)
            return getattr(self, '_m_display_start_frame', None)

        @property
        def frame_in_point(self):
            if hasattr(self, '_m_frame_in_point'):
                return self._m_frame_in_point

            self._m_frame_in_point = (self.display_start_frame + self.in_point_raw // self.time_scale)
            return getattr(self, '_m_frame_in_point', None)


    class Tdb4Body(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(2)
            self.dimensions = self._io.read_u2be()
            self.attributes = self._io.read_bytes(2)
            self._unnamed3 = self._io.read_bytes(1)
            self._unnamed4 = self._io.read_bytes(1)
            self._unnamed5 = self._io.read_bytes(2)
            self._unnamed6 = self._io.read_bytes(2)
            self._unnamed7 = self._io.read_bytes(2)
            self._unnamed8 = self._io.read_bytes(2)
            self._unnamed9 = self._io.read_f8be()
            self._unnamed10 = self._io.read_f8be()
            self._unnamed11 = self._io.read_f8be()
            self._unnamed12 = self._io.read_f8be()
            self._unnamed13 = self._io.read_f8be()
            self.property_control_type = self._io.read_bytes(4)
            self._unnamed15 = self._io.read_bytes(1)
            self._unnamed16 = self._io.read_bytes(7)
            self.animated = self._io.read_u1()
            self._unnamed18 = self._io.read_bytes(7)
            self._unnamed19 = self._io.read_bytes(4)
            self._unnamed20 = self._io.read_bytes(4)
            self._unnamed21 = self._io.read_f8be()
            self._unnamed22 = self._io.read_f8be()
            self._unnamed23 = self._io.read_f8be()
            self._unnamed24 = self._io.read_f8be()
            self.expression_flags = self._io.read_bytes(4)
            self._unnamed26 = self._io.read_bytes(4)

        @property
        def integer(self):
            if hasattr(self, '_m_integer'):
                return self._m_integer

            self._m_integer = (KaitaiStream.byte_array_index(self.property_control_type, 3) & (1 << 2)) != 0
            return getattr(self, '_m_integer', None)

        @property
        def is_spatial(self):
            if hasattr(self, '_m_is_spatial'):
                return self._m_is_spatial

            self._m_is_spatial = (KaitaiStream.byte_array_index(self.attributes, 1) & (1 << 3)) != 0
            return getattr(self, '_m_is_spatial', None)

        @property
        def vector(self):
            if hasattr(self, '_m_vector'):
                return self._m_vector

            self._m_vector = (KaitaiStream.byte_array_index(self.property_control_type, 3) & (1 << 3)) != 0
            return getattr(self, '_m_vector', None)

        @property
        def static(self):
            if hasattr(self, '_m_static'):
                return self._m_static

            self._m_static = (KaitaiStream.byte_array_index(self.attributes, 1) & 1) != 0
            return getattr(self, '_m_static', None)

        @property
        def no_value(self):
            if hasattr(self, '_m_no_value'):
                return self._m_no_value

            self._m_no_value = (KaitaiStream.byte_array_index(self.property_control_type, 1) & 1) != 0
            return getattr(self, '_m_no_value', None)

        @property
        def color(self):
            if hasattr(self, '_m_color'):
                return self._m_color

            self._m_color = (KaitaiStream.byte_array_index(self.property_control_type, 3) & 1) != 0
            return getattr(self, '_m_color', None)

        @property
        def expression_enabled(self):
            if hasattr(self, '_m_expression_enabled'):
                return self._m_expression_enabled

            self._m_expression_enabled = (KaitaiStream.byte_array_index(self.expression_flags, 3) & 1) == 0
            return getattr(self, '_m_expression_enabled', None)


    class LdatBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.keyframes = self._io.read_bytes_full()


    class NnhdBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(8)
            self.time_display_type = KaitaiStream.resolve_enum(Aep.TimeDisplayType, self._io.read_u1())
            self.footage_timecode_display_start_type = KaitaiStream.resolve_enum(Aep.FootageTimecodeDisplayStartType, self._io.read_u1())
            self._unnamed3 = self._io.read_bytes(4)
            self.frame_rate = self._io.read_u2be()
            self._unnamed5 = self._io.read_bytes(4)
            self.frames_count_type = KaitaiStream.resolve_enum(Aep.FramesCountType, self._io.read_u1())
            self._unnamed7 = self._io.read_bytes(3)
            self.bits_per_channel = KaitaiStream.resolve_enum(Aep.BitsPerChannel, self._io.read_u1())
            self._unnamed9 = self._io.read_bytes(15)


    class KfColor(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_u8be()
            self._unnamed1 = self._io.read_f8be()
            self.in_speed = self._io.read_f8be()
            self.in_influence = self._io.read_f8be()
            self.out_speed = self._io.read_f8be()
            self.out_influence = self._io.read_f8be()
            self.value = []
            for i in range(4):
                self.value.append(self._io.read_f8be())

            self._unnamed7 = []
            for i in range(8):
                self._unnamed7.append(self._io.read_f8be())



    class FdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(1)


    class KfMultiDimensional(KaitaiStruct):
        def __init__(self, nb_dimensions, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.nb_dimensions = nb_dimensions
            self._read()

        def _read(self):
            self.value = []
            for i in range(self.nb_dimensions):
                self.value.append(self._io.read_f8be())

            self.in_speed = []
            for i in range(self.nb_dimensions):
                self.in_speed.append(self._io.read_f8be())

            self.in_influence = []
            for i in range(self.nb_dimensions):
                self.in_influence.append(self._io.read_f8be())

            self.out_speed = []
            for i in range(self.nb_dimensions):
                self.out_speed.append(self._io.read_f8be())

            self.out_influence = []
            for i in range(self.nb_dimensions):
                self.out_influence.append(self._io.read_f8be())



    class Chunks(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.chunks = []
            i = 0
            while not self._io.is_eof():
                self.chunks.append(Aep.Chunk(self._io, self, self._root))
                i += 1



    class Utf8Body(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = (self._io.read_bytes_full()).decode(u"utf8")


    class IdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.item_type = KaitaiStream.resolve_enum(Aep.ItemType, self._io.read_u2be())
            self._unnamed1 = self._io.read_bytes(14)
            self.item_id = self._io.read_u4be()
            self._unnamed3 = self._io.read_bytes(38)
            self.label = KaitaiStream.resolve_enum(Aep.Label, self._io.read_u1())


    class KfPosition(KaitaiStruct):
        def __init__(self, nb_dimensions, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.nb_dimensions = nb_dimensions
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_u8be()
            self._unnamed1 = self._io.read_f8be()
            self.in_speed = self._io.read_f8be()
            self.in_influence = self._io.read_f8be()
            self.out_speed = self._io.read_f8be()
            self.out_influence = self._io.read_f8be()
            self.value = []
            for i in range(self.nb_dimensions):
                self.value.append(self._io.read_f8be())

            self.tan_in = []
            for i in range(self.nb_dimensions):
                self.tan_in.append(self._io.read_f8be())

            self.tan_out = []
            for i in range(self.nb_dimensions):
                self.tan_out.append(self._io.read_f8be())



    class NmhdBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(3)
            self._unnamed1 = self._io.read_bits_int_be(5)
            self.unknown = self._io.read_bits_int_be(1) != 0
            self.protected_region = self._io.read_bits_int_be(1) != 0
            self.navigation = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self._unnamed5 = self._io.read_bytes(4)
            self.frame_duration = self._io.read_u4be()
            self._unnamed7 = self._io.read_bytes(4)
            self.label = KaitaiStream.resolve_enum(Aep.Label, self._io.read_u1())


    class SspcBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(32)
            self.width = self._io.read_u2be()
            self._unnamed2 = self._io.read_bytes(2)
            self.height = self._io.read_u2be()
            self.duration_dividend = self._io.read_u4be()
            self.duration_divisor = self._io.read_u4be()
            self._unnamed6 = self._io.read_bytes(10)
            self.frame_rate_base = self._io.read_u4be()
            self.frame_rate_dividend = self._io.read_u2be()
            self._unnamed9 = self._io.read_bytes(110)
            self.start_frame = self._io.read_u4be()
            self.end_frame = self._io.read_u4be()

        @property
        def duration(self):
            if hasattr(self, '_m_duration'):
                return self._m_duration

            self._m_duration = (self.duration_dividend / self.duration_divisor)
            return getattr(self, '_m_duration', None)

        @property
        def frame_rate(self):
            if hasattr(self, '_m_frame_rate'):
                return self._m_frame_rate

            self._m_frame_rate = (self.frame_rate_base + (self.frame_rate_dividend / (1 << 16)))
            return getattr(self, '_m_frame_rate', None)

        @property
        def frame_duration(self):
            if hasattr(self, '_m_frame_duration'):
                return self._m_frame_duration

            self._m_frame_duration = (self.duration * self.frame_rate)
            return getattr(self, '_m_frame_duration', None)


    class OptiBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.asset_type = (KaitaiStream.bytes_terminate(self._io.read_bytes(4), 0, False)).decode(u"ascii")
            self.asset_type_int = self._io.read_u2be()
            if self.asset_type == u"Soli":
                self._unnamed2 = self._io.read_bytes(4)

            if self.asset_type == u"Soli":
                self.color = []
                for i in range(4):
                    self.color.append(self._io.read_f4be())


            if self.asset_type == u"Soli":
                self.solid_name = (KaitaiStream.bytes_terminate(self._io.read_bytes(256), 0, False)).decode(u"cp1250")

            if self.asset_type_int == 2:
                self._unnamed5 = self._io.read_bytes(4)

            if self.asset_type_int == 2:
                self.placeholder_name = (KaitaiStream.bytes_terminate(self._io.read_bytes_full(), 0, False)).decode(u"cp1250")


        @property
        def red(self):
            if hasattr(self, '_m_red'):
                return self._m_red

            if self.asset_type == u"Soli":
                self._m_red = self.color[1]

            return getattr(self, '_m_red', None)

        @property
        def green(self):
            if hasattr(self, '_m_green'):
                return self._m_green

            if self.asset_type == u"Soli":
                self._m_green = self.color[2]

            return getattr(self, '_m_green', None)

        @property
        def blue(self):
            if hasattr(self, '_m_blue'):
                return self._m_blue

            if self.asset_type == u"Soli":
                self._m_blue = self.color[3]

            return getattr(self, '_m_blue', None)

        @property
        def alpha(self):
            if hasattr(self, '_m_alpha'):
                return self._m_alpha

            if self.asset_type == u"Soli":
                self._m_alpha = self.color[0]

            return getattr(self, '_m_alpha', None)


    class HeadBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ae_version = self._io.read_bytes(6)
            self._unnamed1 = self._io.read_bytes(12)
            self.file_revision = self._io.read_u2be()


    class AlasBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.contents = (self._io.read_bytes_full()).decode(u"ascii")


    class KfUnknownData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_bytes_full()


    class CdatBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.value = []
            for i in range(self._parent.len_data // 8):
                self.value.append(self._io.read_f8be())



    class KfNoValue(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_u8be()
            self._unnamed1 = self._io.read_f8be()
            self.in_speed = self._io.read_f8be()
            self.in_influence = self._io.read_f8be()
            self.out_speed = self._io.read_f8be()
            self.out_influence = self._io.read_f8be()


    class AsciiBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_bytes_full()


    class PardBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(15)
            self.property_control_type = KaitaiStream.resolve_enum(Aep.PropertyControlType, self._io.read_u1())
            self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(32), 0, False)).decode(u"cp1250")
            self._unnamed3 = self._io.read_bytes(8)
            if self.property_control_type == Aep.PropertyControlType.color:
                self.last_color = []
                for i in range(4):
                    self.last_color.append(self._io.read_u1())


            if self.property_control_type == Aep.PropertyControlType.color:
                self.default_color = []
                for i in range(4):
                    self.default_color.append(self._io.read_u1())


            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.angle) or (self.property_control_type == Aep.PropertyControlType.boolean) or (self.property_control_type == Aep.PropertyControlType.enum) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.boolean:
                    self.last_value = self._io.read_u4be()
                elif _on == Aep.PropertyControlType.angle:
                    self.last_value = self._io.read_s4be()
                elif _on == Aep.PropertyControlType.scalar:
                    self.last_value = self._io.read_s4be()
                elif _on == Aep.PropertyControlType.slider:
                    self.last_value = self._io.read_f8be()
                elif _on == Aep.PropertyControlType.enum:
                    self.last_value = self._io.read_u4be()

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.two_d:
                    self.last_value_x_raw = self._io.read_s4be()
                elif _on == Aep.PropertyControlType.three_d:
                    self.last_value_x_raw = self._io.read_f8be()

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.two_d:
                    self.last_value_y_raw = self._io.read_s4be()
                elif _on == Aep.PropertyControlType.three_d:
                    self.last_value_y_raw = self._io.read_f8be()

            if self.property_control_type == Aep.PropertyControlType.three_d:
                self.last_value_z_raw = self._io.read_f8be()

            if self.property_control_type == Aep.PropertyControlType.enum:
                self.nb_options = self._io.read_s4be()

            if  ((self.property_control_type == Aep.PropertyControlType.boolean) or (self.property_control_type == Aep.PropertyControlType.enum)) :
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.boolean:
                    self.default = self._io.read_u1()
                elif _on == Aep.PropertyControlType.enum:
                    self.default = self._io.read_s4be()

            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.color) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                self._unnamed12 = self._io.read_bytes((72 if self.property_control_type == Aep.PropertyControlType.scalar else (64 if self.property_control_type == Aep.PropertyControlType.color else 52)))

            if self.property_control_type == Aep.PropertyControlType.scalar:
                self.min_value = self._io.read_s2be()

            if self.property_control_type == Aep.PropertyControlType.scalar:
                self._unnamed14 = self._io.read_bytes(2)

            if self.property_control_type == Aep.PropertyControlType.color:
                self.max_color = []
                for i in range(4):
                    self.max_color.append(self._io.read_u1())


            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.scalar:
                    self.max_value = self._io.read_s2be()
                elif _on == Aep.PropertyControlType.slider:
                    self.max_value = self._io.read_f4be()


        @property
        def last_value_x(self):
            if hasattr(self, '_m_last_value_x'):
                return self._m_last_value_x

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                self._m_last_value_x = (self.last_value_x_raw * (1 // 128 if self.property_control_type == Aep.PropertyControlType.two_d else 512))

            return getattr(self, '_m_last_value_x', None)

        @property
        def last_value_y(self):
            if hasattr(self, '_m_last_value_y'):
                return self._m_last_value_y

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                self._m_last_value_y = (self.last_value_y_raw * (1 // 128 if self.property_control_type == Aep.PropertyControlType.two_d else 512))

            return getattr(self, '_m_last_value_y', None)

        @property
        def last_value_z(self):
            if hasattr(self, '_m_last_value_z'):
                return self._m_last_value_z

            if self.property_control_type == Aep.PropertyControlType.three_d:
                self._m_last_value_z = (self.last_value_z_raw * 512)

            return getattr(self, '_m_last_value_z', None)


    class TdsbBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(2)
            self._unnamed1 = self._io.read_bits_int_be(3)
            self.locked_ratio = self._io.read_bits_int_be(1) != 0
            self._unnamed3 = self._io.read_bits_int_be(4)
            self._unnamed4 = self._io.read_bits_int_be(6)
            self.dimensions_separated = self._io.read_bits_int_be(1) != 0
            self.enabled = self._io.read_bits_int_be(1) != 0


    class LdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.layer_id = self._io.read_u4be()
            self.quality = KaitaiStream.resolve_enum(Aep.LayerQuality, self._io.read_u2be())
            self._unnamed2 = self._io.read_bytes(4)
            self.stretch_dividend = self._io.read_u2be()
            self.start_time_dividend = self._io.read_u4be()
            self.start_time_divisor = self._io.read_u4be()
            self.in_point_dividend = self._io.read_u4be()
            self.in_point_divisor = self._io.read_u4be()
            self.out_point_dividend = self._io.read_u4be()
            self.out_point_divisor = self._io.read_u4be()
            self._unnamed10 = self._io.read_bytes(1)
            self.attributes = self._io.read_bytes(3)
            self.source_id = self._io.read_u4be()
            self._unnamed13 = self._io.read_bytes(17)
            self.label = KaitaiStream.resolve_enum(Aep.Label, self._io.read_u1())
            self._unnamed15 = self._io.read_bytes(2)
            self.layer_name = (self._io.read_bytes(32)).decode(u"cp1250")
            self._unnamed17 = self._io.read_bytes(3)
            self.blending_mode = KaitaiStream.resolve_enum(Aep.BlendingMode, self._io.read_u1())
            self._unnamed19 = self._io.read_bytes(3)
            self.preserve_transparency = self._io.read_u1()
            self._unnamed21 = self._io.read_bytes(3)
            self.track_matte_type = KaitaiStream.resolve_enum(Aep.TrackMatteType, self._io.read_u1())
            self._unnamed23 = self._io.read_bytes(2)
            self.stretch_divisor = self._io.read_u2be()
            self._unnamed25 = self._io.read_bytes(19)
            self.layer_type = KaitaiStream.resolve_enum(Aep.LayerType, self._io.read_u1())
            self.parent_id = self._io.read_u4be()
            self._unnamed28 = self._io.read_bytes(24)

        @property
        def null_layer(self):
            if hasattr(self, '_m_null_layer'):
                return self._m_null_layer

            self._m_null_layer = (KaitaiStream.byte_array_index(self.attributes, 1) & (1 << 7)) != 0
            return getattr(self, '_m_null_layer', None)

        @property
        def three_d_layer(self):
            if hasattr(self, '_m_three_d_layer'):
                return self._m_three_d_layer

            self._m_three_d_layer = (KaitaiStream.byte_array_index(self.attributes, 1) & (1 << 2)) != 0
            return getattr(self, '_m_three_d_layer', None)

        @property
        def shy(self):
            if hasattr(self, '_m_shy'):
                return self._m_shy

            self._m_shy = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 6)) != 0
            return getattr(self, '_m_shy', None)

        @property
        def auto_orient(self):
            if hasattr(self, '_m_auto_orient'):
                return self._m_auto_orient

            self._m_auto_orient = (KaitaiStream.byte_array_index(self.attributes, 1) & 1) != 0
            return getattr(self, '_m_auto_orient', None)

        @property
        def motion_blur(self):
            if hasattr(self, '_m_motion_blur'):
                return self._m_motion_blur

            self._m_motion_blur = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 3)) != 0
            return getattr(self, '_m_motion_blur', None)

        @property
        def adjustment_layer(self):
            if hasattr(self, '_m_adjustment_layer'):
                return self._m_adjustment_layer

            self._m_adjustment_layer = (KaitaiStream.byte_array_index(self.attributes, 1) & (1 << 1)) != 0
            return getattr(self, '_m_adjustment_layer', None)

        @property
        def out_point(self):
            if hasattr(self, '_m_out_point'):
                return self._m_out_point

            self._m_out_point = (self.out_point_dividend / self.out_point_divisor)
            return getattr(self, '_m_out_point', None)

        @property
        def frame_blending_type(self):
            if hasattr(self, '_m_frame_blending_type'):
                return self._m_frame_blending_type

            self._m_frame_blending_type = KaitaiStream.resolve_enum(Aep.FrameBlendingType, ((KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 2)) >> 2))
            return getattr(self, '_m_frame_blending_type', None)

        @property
        def effects_active(self):
            if hasattr(self, '_m_effects_active'):
                return self._m_effects_active

            self._m_effects_active = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 2)) != 0
            return getattr(self, '_m_effects_active', None)

        @property
        def frame_blending(self):
            if hasattr(self, '_m_frame_blending'):
                return self._m_frame_blending

            self._m_frame_blending = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 4)) != 0
            return getattr(self, '_m_frame_blending', None)

        @property
        def collapse_transformation(self):
            if hasattr(self, '_m_collapse_transformation'):
                return self._m_collapse_transformation

            self._m_collapse_transformation = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 7)) != 0
            return getattr(self, '_m_collapse_transformation', None)

        @property
        def markers_locked(self):
            if hasattr(self, '_m_markers_locked'):
                return self._m_markers_locked

            self._m_markers_locked = (KaitaiStream.byte_array_index(self.attributes, 1) & (1 << 4)) != 0
            return getattr(self, '_m_markers_locked', None)

        @property
        def locked(self):
            if hasattr(self, '_m_locked'):
                return self._m_locked

            self._m_locked = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 5)) != 0
            return getattr(self, '_m_locked', None)

        @property
        def sampling_quality(self):
            if hasattr(self, '_m_sampling_quality'):
                return self._m_sampling_quality

            self._m_sampling_quality = KaitaiStream.resolve_enum(Aep.SamplingQuality, ((KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 6)) >> 6))
            return getattr(self, '_m_sampling_quality', None)

        @property
        def guide_layer(self):
            if hasattr(self, '_m_guide_layer'):
                return self._m_guide_layer

            self._m_guide_layer = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 1)) != 0
            return getattr(self, '_m_guide_layer', None)

        @property
        def in_point(self):
            if hasattr(self, '_m_in_point'):
                return self._m_in_point

            self._m_in_point = (self.in_point_dividend / self.in_point_divisor)
            return getattr(self, '_m_in_point', None)

        @property
        def start_time(self):
            if hasattr(self, '_m_start_time'):
                return self._m_start_time

            self._m_start_time = (self.start_time_dividend / self.start_time_divisor)
            return getattr(self, '_m_start_time', None)

        @property
        def environment_layer(self):
            if hasattr(self, '_m_environment_layer'):
                return self._m_environment_layer

            self._m_environment_layer = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 5)) != 0
            return getattr(self, '_m_environment_layer', None)

        @property
        def enabled(self):
            if hasattr(self, '_m_enabled'):
                return self._m_enabled

            self._m_enabled = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 0)) != 0
            return getattr(self, '_m_enabled', None)

        @property
        def solo(self):
            if hasattr(self, '_m_solo'):
                return self._m_solo

            self._m_solo = (KaitaiStream.byte_array_index(self.attributes, 1) & (1 << 3)) != 0
            return getattr(self, '_m_solo', None)

        @property
        def audio_enabled(self):
            if hasattr(self, '_m_audio_enabled'):
                return self._m_audio_enabled

            self._m_audio_enabled = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 1)) != 0
            return getattr(self, '_m_audio_enabled', None)



