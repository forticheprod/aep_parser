# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Aep(KaitaiStruct):

    class LayerFrameBlendMode(Enum):
        frame_mix = 0
        pixel_motion = 1

    class PropertyType(Enum):
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

    class MatteMode(Enum):
        none = 0
        no_matte = 1
        alpha = 2
        inverted_alpha = 3
        luma = 4
        inverted_luma = 5

    class LayerType(Enum):
        footage = 0
        light = 1
        camera = 2
        text = 3
        shape = 4

    class EaseMode(Enum):
        linear = 1
        ease = 2
        hold = 3

    class KeyframeType(Enum):
        unknown = 0
        lrdr = 1
        litm = 2
        gide = 3
        color = 4
        three_d_pos = 5
        three_d = 6
        two_d_pos = 7
        two_d = 8
        orientation = 9
        no_value = 10
        one_d = 11
        marker = 12

    class LayerSamplingMode(Enum):
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
            self.time_raw = self._io.read_u4be()
            self._unnamed1 = self._io.read_bytes(1)
            self.ease_mode = KaitaiStream.resolve_enum(Aep.EaseMode, self._io.read_u1())
            self.label = KaitaiStream.resolve_enum(Aep.Label, self._io.read_u1())
            self.attributes = self._io.read_bytes(1)
            _on = self.key_type
            if _on == Aep.KeyframeType.lrdr:
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
            elif _on == Aep.KeyframeType.one_d:
                self.kf_data = Aep.KfMultiDimensional(1, self._io, self, self._root)
            elif _on == Aep.KeyframeType.color:
                self.kf_data = Aep.KfColor(self._io, self, self._root)
            elif _on == Aep.KeyframeType.marker:
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
            elif _on == Aep.KeyframeType.two_d:
                self.kf_data = Aep.KfMultiDimensional(2, self._io, self, self._root)
            elif _on == Aep.KeyframeType.gide:
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
            elif _on == Aep.KeyframeType.three_d:
                self.kf_data = Aep.KfMultiDimensional(3, self._io, self, self._root)
            elif _on == Aep.KeyframeType.unknown:
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
            elif _on == Aep.KeyframeType.no_value:
                self.kf_data = Aep.KfNoValue(self._io, self, self._root)
            elif _on == Aep.KeyframeType.two_d_pos:
                self.kf_data = Aep.KfPosition(2, self._io, self, self._root)
            elif _on == Aep.KeyframeType.litm:
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
            elif _on == Aep.KeyframeType.orientation:
                self.kf_data = Aep.KfMultiDimensional(1, self._io, self, self._root)
            elif _on == Aep.KeyframeType.three_d_pos:
                self.kf_data = Aep.KfPosition(3, self._io, self, self._root)

        @property
        def continuous_bezier(self):
            if hasattr(self, '_m_continuous_bezier'):
                return self._m_continuous_bezier

            self._m_continuous_bezier = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 3)) != 0
            return getattr(self, '_m_continuous_bezier', None)

        @property
        def auto_bezier(self):
            if hasattr(self, '_m_auto_bezier'):
                return self._m_auto_bezier

            self._m_auto_bezier = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 4)) != 0
            return getattr(self, '_m_auto_bezier', None)

        @property
        def roving_across_time(self):
            if hasattr(self, '_m_roving_across_time'):
                return self._m_roving_across_time

            self._m_roving_across_time = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 5)) != 0
            return getattr(self, '_m_roving_across_time', None)


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
            elif _on == u"nhed":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.len_data > (self._io.size() - self._io.pos()) else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.NhedBody(_io__raw_data, self, self._root)
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

            self._m_keyframes_type = (Aep.KeyframeType.lrdr if  ((self.keyframes_type_raw == 1) and (self.len_keyframe == 2246))  else (Aep.KeyframeType.litm if  ((self.keyframes_type_raw == 1) and (self.len_keyframe == 128))  else (Aep.KeyframeType.gide if  ((self.keyframes_type_raw == 2) and (self.len_keyframe == 1))  else (Aep.KeyframeType.color if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 152))  else (Aep.KeyframeType.three_d if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 128))  else (Aep.KeyframeType.two_d_pos if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 104))  else (Aep.KeyframeType.two_d if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 88))  else (Aep.KeyframeType.orientation if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 80))  else (Aep.KeyframeType.no_value if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 64))  else (Aep.KeyframeType.one_d if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 48))  else (Aep.KeyframeType.marker if  ((self.keyframes_type_raw == 4) and (self.len_keyframe == 16))  else Aep.KeyframeType.unknown)))))))))))
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

            self._unnamed1 = self._io.read_bytes(2)
            self.time_scale = self._io.read_u2be()
            self._unnamed3 = self._io.read_bytes(2)
            self.frame_rate_dividend = self._io.read_u2be()
            self._unnamed5 = self._io.read_bytes(10)
            self.playhead = self._io.read_u2be()
            self._unnamed7 = self._io.read_bytes(5)
            self.in_time = self._io.read_u2be()
            self._unnamed9 = self._io.read_bytes(6)
            self.out_time_raw = self._io.read_u2be()
            self._unnamed11 = self._io.read_bytes(5)
            self.duration_dividend = self._io.read_u4be()
            self.duration_divisor = self._io.read_u4be()
            self.bg_color = []
            for i in range(3):
                self.bg_color.append(self._io.read_u1())

            self._unnamed15 = self._io.read_bytes(84)
            self.attributes = self._io.read_bytes(1)
            self.width = self._io.read_u2be()
            self.height = self._io.read_u2be()
            self.pixel_ratio_width = self._io.read_u4be()
            self.pixel_ratio_height = self._io.read_u4be()
            self._unnamed21 = self._io.read_bytes(4)
            self.frame_rate_integer = self._io.read_u2be()
            self._unnamed23 = self._io.read_bytes(16)
            self.shutter_angle = self._io.read_u2be()
            self.shutter_phase = self._io.read_u4be()
            self._unnamed26 = self._io.read_bytes(16)
            self.motion_blur_adaptive_sample_limit = self._io.read_s4be()
            self.motion_blur_samples_per_frame = self._io.read_s4be()

        @property
        def out_time_frames(self):
            if hasattr(self, '_m_out_time_frames'):
                return self._m_out_time_frames

            self._m_out_time_frames = (self.out_time * self.frame_rate)
            return getattr(self, '_m_out_time_frames', None)

        @property
        def motion_blur(self):
            if hasattr(self, '_m_motion_blur'):
                return self._m_motion_blur

            self._m_motion_blur = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 3)) != 0
            return getattr(self, '_m_motion_blur', None)

        @property
        def pixel_aspect(self):
            if hasattr(self, '_m_pixel_aspect'):
                return self._m_pixel_aspect

            self._m_pixel_aspect = (self.pixel_ratio_width / self.pixel_ratio_height)
            return getattr(self, '_m_pixel_aspect', None)

        @property
        def preserve_nested_frame_rate(self):
            if hasattr(self, '_m_preserve_nested_frame_rate'):
                return self._m_preserve_nested_frame_rate

            self._m_preserve_nested_frame_rate = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 5)) != 0
            return getattr(self, '_m_preserve_nested_frame_rate', None)

        @property
        def frame_blending(self):
            if hasattr(self, '_m_frame_blending'):
                return self._m_frame_blending

            self._m_frame_blending = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 4)) != 0
            return getattr(self, '_m_frame_blending', None)

        @property
        def preserve_nested_resolution(self):
            if hasattr(self, '_m_preserve_nested_resolution'):
                return self._m_preserve_nested_resolution

            self._m_preserve_nested_resolution = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 7)) != 0
            return getattr(self, '_m_preserve_nested_resolution', None)

        @property
        def out_time(self):
            if hasattr(self, '_m_out_time'):
                return self._m_out_time

            self._m_out_time = (self.duration if self.out_time_raw == 65535 else self.out_time_raw)
            return getattr(self, '_m_out_time', None)

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
        def playhead_frames(self):
            if hasattr(self, '_m_playhead_frames'):
                return self._m_playhead_frames

            self._m_playhead_frames = self.playhead // self.time_scale
            return getattr(self, '_m_playhead_frames', None)

        @property
        def in_time_frames(self):
            if hasattr(self, '_m_in_time_frames'):
                return self._m_in_time_frames

            self._m_in_time_frames = (self.in_time * self.frame_rate)
            return getattr(self, '_m_in_time_frames', None)

        @property
        def duration(self):
            if hasattr(self, '_m_duration'):
                return self._m_duration

            self._m_duration = (self.duration_dividend / self.duration_divisor)
            return getattr(self, '_m_duration', None)

        @property
        def shy_enabled(self):
            if hasattr(self, '_m_shy_enabled'):
                return self._m_shy_enabled

            self._m_shy_enabled = (KaitaiStream.byte_array_index(self.attributes, 0) & 1) != 0
            return getattr(self, '_m_shy_enabled', None)


    class Tdb4Body(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(2)
            self.components = self._io.read_u2be()
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
            self.property_type = self._io.read_bytes(4)
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
            self._unnamed25 = self._io.read_bytes(4)
            self._unnamed26 = self._io.read_bytes(4)

        @property
        def integer(self):
            if hasattr(self, '_m_integer'):
                return self._m_integer

            self._m_integer = (KaitaiStream.byte_array_index(self.property_type, 3) & (1 << 2)) != 0
            return getattr(self, '_m_integer', None)

        @property
        def position(self):
            if hasattr(self, '_m_position'):
                return self._m_position

            self._m_position = (KaitaiStream.byte_array_index(self.attributes, 1) & (1 << 3)) != 0
            return getattr(self, '_m_position', None)

        @property
        def vector(self):
            if hasattr(self, '_m_vector'):
                return self._m_vector

            self._m_vector = (KaitaiStream.byte_array_index(self.property_type, 3) & (1 << 3)) != 0
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

            self._m_no_value = (KaitaiStream.byte_array_index(self.property_type, 1) & 1) != 0
            return getattr(self, '_m_no_value', None)

        @property
        def color(self):
            if hasattr(self, '_m_color'):
                return self._m_color

            self._m_color = (KaitaiStream.byte_array_index(self.property_type, 3) & 1) != 0
            return getattr(self, '_m_color', None)


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
            self._unnamed0 = self._io.read_bytes(14)
            self.frame_rate = self._io.read_u2be()
            self._unnamed2 = self._io.read_bytes(24)


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
            self.attributes = self._io.read_bytes(1)
            self._unnamed2 = self._io.read_bytes(4)
            self.frame_duration = self._io.read_u4be()
            self._unnamed4 = self._io.read_bytes(4)
            self.label = KaitaiStream.resolve_enum(Aep.Label, self._io.read_u1())

        @property
        def navigation(self):
            if hasattr(self, '_m_navigation'):
                return self._m_navigation

            self._m_navigation = (KaitaiStream.byte_array_index(self.attributes, 0) & 1) != 0
            return getattr(self, '_m_navigation', None)

        @property
        def protected(self):
            if hasattr(self, '_m_protected'):
                return self._m_protected

            self._m_protected = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 1)) != 0
            return getattr(self, '_m_protected', None)

        @property
        def unknown(self):
            if hasattr(self, '_m_unknown'):
                return self._m_unknown

            self._m_unknown = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 2)) != 0
            return getattr(self, '_m_unknown', None)


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
            self.asset_type = (self._io.read_bytes(4)).decode(u"ascii")
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


    class NhedBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(15)
            self.bits_per_channel = KaitaiStream.resolve_enum(Aep.BitsPerChannel, self._io.read_u1())


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
            self.property_type = KaitaiStream.resolve_enum(Aep.PropertyType, self._io.read_u1())
            self.name = (self._io.read_bytes(32)).decode(u"cp1250")
            self._unnamed3 = self._io.read_bytes(8)
            if self.property_type == Aep.PropertyType.color:
                self.last_color = []
                for i in range(4):
                    self.last_color.append(self._io.read_u1())


            if self.property_type == Aep.PropertyType.color:
                self.default_color = []
                for i in range(4):
                    self.default_color.append(self._io.read_u1())


            if  ((self.property_type == Aep.PropertyType.scalar) or (self.property_type == Aep.PropertyType.angle) or (self.property_type == Aep.PropertyType.boolean) or (self.property_type == Aep.PropertyType.enum) or (self.property_type == Aep.PropertyType.slider)) :
                _on = self.property_type
                if _on == Aep.PropertyType.slider:
                    self.last_value = self._io.read_f8be()
                elif _on == Aep.PropertyType.angle:
                    self.last_value = self._io.read_s4be()
                elif _on == Aep.PropertyType.scalar:
                    self.last_value = self._io.read_s4be()
                elif _on == Aep.PropertyType.enum:
                    self.last_value = self._io.read_u4be()
                elif _on == Aep.PropertyType.boolean:
                    self.last_value = self._io.read_u4be()

            if  ((self.property_type == Aep.PropertyType.two_d) or (self.property_type == Aep.PropertyType.three_d)) :
                _on = self.property_type
                if _on == Aep.PropertyType.two_d:
                    self.last_value_x_raw = self._io.read_s4be()
                elif _on == Aep.PropertyType.three_d:
                    self.last_value_x_raw = self._io.read_f8be()

            if  ((self.property_type == Aep.PropertyType.two_d) or (self.property_type == Aep.PropertyType.three_d)) :
                _on = self.property_type
                if _on == Aep.PropertyType.two_d:
                    self.last_value_y_raw = self._io.read_s4be()
                elif _on == Aep.PropertyType.three_d:
                    self.last_value_y_raw = self._io.read_f8be()

            if self.property_type == Aep.PropertyType.three_d:
                self.last_value_z_raw = self._io.read_f8be()

            if self.property_type == Aep.PropertyType.enum:
                self.nb_options = self._io.read_s4be()

            if  ((self.property_type == Aep.PropertyType.boolean) or (self.property_type == Aep.PropertyType.enum)) :
                _on = self.property_type
                if _on == Aep.PropertyType.boolean:
                    self.default = self._io.read_u1()
                elif _on == Aep.PropertyType.enum:
                    self.default = self._io.read_s4be()

            if  ((self.property_type == Aep.PropertyType.scalar) or (self.property_type == Aep.PropertyType.color) or (self.property_type == Aep.PropertyType.slider)) :
                self._unnamed12 = self._io.read_bytes((72 if self.property_type == Aep.PropertyType.scalar else (64 if self.property_type == Aep.PropertyType.color else 52)))

            if self.property_type == Aep.PropertyType.scalar:
                self.min_value = self._io.read_s2be()

            if self.property_type == Aep.PropertyType.scalar:
                self._unnamed14 = self._io.read_bytes(2)

            if self.property_type == Aep.PropertyType.color:
                self.max_color = []
                for i in range(4):
                    self.max_color.append(self._io.read_u1())


            if  ((self.property_type == Aep.PropertyType.scalar) or (self.property_type == Aep.PropertyType.slider)) :
                _on = self.property_type
                if _on == Aep.PropertyType.scalar:
                    self.max_value = self._io.read_s2be()
                elif _on == Aep.PropertyType.slider:
                    self.max_value = self._io.read_f4be()


        @property
        def last_value_x(self):
            if hasattr(self, '_m_last_value_x'):
                return self._m_last_value_x

            if  ((self.property_type == Aep.PropertyType.two_d) or (self.property_type == Aep.PropertyType.three_d)) :
                self._m_last_value_x = (self.last_value_x_raw * (1 // 128 if self.property_type == Aep.PropertyType.two_d else 512))

            return getattr(self, '_m_last_value_x', None)

        @property
        def last_value_y(self):
            if hasattr(self, '_m_last_value_y'):
                return self._m_last_value_y

            if  ((self.property_type == Aep.PropertyType.two_d) or (self.property_type == Aep.PropertyType.three_d)) :
                self._m_last_value_y = (self.last_value_y_raw * (1 // 128 if self.property_type == Aep.PropertyType.two_d else 512))

            return getattr(self, '_m_last_value_y', None)

        @property
        def last_value_z(self):
            if hasattr(self, '_m_last_value_z'):
                return self._m_last_value_z

            if self.property_type == Aep.PropertyType.three_d:
                self._m_last_value_z = (self.last_value_z_raw * 512)

            return getattr(self, '_m_last_value_z', None)


    class TdsbBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flags = self._io.read_bytes(4)

        @property
        def locked_ratio(self):
            if hasattr(self, '_m_locked_ratio'):
                return self._m_locked_ratio

            self._m_locked_ratio = (KaitaiStream.byte_array_index(self.flags, 2) & (1 << 4)) != 0
            return getattr(self, '_m_locked_ratio', None)

        @property
        def visible(self):
            if hasattr(self, '_m_visible'):
                return self._m_visible

            self._m_visible = (KaitaiStream.byte_array_index(self.flags, 3) & 1) != 0
            return getattr(self, '_m_visible', None)

        @property
        def split_position(self):
            if hasattr(self, '_m_split_position'):
                return self._m_split_position

            self._m_split_position = (KaitaiStream.byte_array_index(self.flags, 3) & (1 << 1)) != 0
            return getattr(self, '_m_split_position', None)


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
            self.stretch_numerator = self._io.read_u2be()
            self._unnamed4 = self._io.read_bytes(1)
            self.start_time_sec = self._io.read_s2be()
            self._unnamed6 = self._io.read_bytes(6)
            self.in_time_sec = self._io.read_u2be()
            self._unnamed8 = self._io.read_bytes(6)
            self.out_time_sec = self._io.read_u2be()
            self._unnamed10 = self._io.read_bytes(6)
            self.attributes = self._io.read_bytes(3)
            self.source_id = self._io.read_u4be()
            self._unnamed13 = self._io.read_bytes(17)
            self.label = KaitaiStream.resolve_enum(Aep.Label, self._io.read_u1())
            self._unnamed15 = self._io.read_bytes(2)
            self.layer_name = (self._io.read_bytes(32)).decode(u"cp1250")
            self._unnamed17 = self._io.read_bytes(11)
            self.matte_mode = KaitaiStream.resolve_enum(Aep.MatteMode, self._io.read_u1())
            self._unnamed19 = self._io.read_bytes(2)
            self.stretch_denominator = self._io.read_u2be()
            self._unnamed21 = self._io.read_bytes(19)
            self.layer_type = KaitaiStream.resolve_enum(Aep.LayerType, self._io.read_u1())
            self.parent_id = self._io.read_u4be()
            self._unnamed24 = self._io.read_bytes(24)

        @property
        def null_layer(self):
            if hasattr(self, '_m_null_layer'):
                return self._m_null_layer

            self._m_null_layer = (KaitaiStream.byte_array_index(self.attributes, 1) & (1 << 7)) != 0
            return getattr(self, '_m_null_layer', None)

        @property
        def guide_enabled(self):
            if hasattr(self, '_m_guide_enabled'):
                return self._m_guide_enabled

            self._m_guide_enabled = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 1)) != 0
            return getattr(self, '_m_guide_enabled', None)

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
        def video_enabled(self):
            if hasattr(self, '_m_video_enabled'):
                return self._m_video_enabled

            self._m_video_enabled = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 0)) != 0
            return getattr(self, '_m_video_enabled', None)

        @property
        def frame_blending(self):
            if hasattr(self, '_m_frame_blending'):
                return self._m_frame_blending

            self._m_frame_blending = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 4)) != 0
            return getattr(self, '_m_frame_blending', None)

        @property
        def effects_enabled(self):
            if hasattr(self, '_m_effects_enabled'):
                return self._m_effects_enabled

            self._m_effects_enabled = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 2)) != 0
            return getattr(self, '_m_effects_enabled', None)

        @property
        def solo_enabled(self):
            if hasattr(self, '_m_solo_enabled'):
                return self._m_solo_enabled

            self._m_solo_enabled = (KaitaiStream.byte_array_index(self.attributes, 1) & (1 << 3)) != 0
            return getattr(self, '_m_solo_enabled', None)

        @property
        def markers_locked(self):
            if hasattr(self, '_m_markers_locked'):
                return self._m_markers_locked

            self._m_markers_locked = (KaitaiStream.byte_array_index(self.attributes, 1) & (1 << 4)) != 0
            return getattr(self, '_m_markers_locked', None)

        @property
        def lock_enabled(self):
            if hasattr(self, '_m_lock_enabled'):
                return self._m_lock_enabled

            self._m_lock_enabled = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 5)) != 0
            return getattr(self, '_m_lock_enabled', None)

        @property
        def three_d_enabled(self):
            if hasattr(self, '_m_three_d_enabled'):
                return self._m_three_d_enabled

            self._m_three_d_enabled = (KaitaiStream.byte_array_index(self.attributes, 1) & (1 << 2)) != 0
            return getattr(self, '_m_three_d_enabled', None)

        @property
        def collapse_transform_enabled(self):
            if hasattr(self, '_m_collapse_transform_enabled'):
                return self._m_collapse_transform_enabled

            self._m_collapse_transform_enabled = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 7)) != 0
            return getattr(self, '_m_collapse_transform_enabled', None)

        @property
        def frame_blend_mode(self):
            if hasattr(self, '_m_frame_blend_mode'):
                return self._m_frame_blend_mode

            self._m_frame_blend_mode = KaitaiStream.resolve_enum(Aep.LayerFrameBlendMode, ((KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 2)) >> 2))
            return getattr(self, '_m_frame_blend_mode', None)

        @property
        def adjustment_layer_enabled(self):
            if hasattr(self, '_m_adjustment_layer_enabled'):
                return self._m_adjustment_layer_enabled

            self._m_adjustment_layer_enabled = (KaitaiStream.byte_array_index(self.attributes, 1) & (1 << 1)) != 0
            return getattr(self, '_m_adjustment_layer_enabled', None)

        @property
        def shy_enabled(self):
            if hasattr(self, '_m_shy_enabled'):
                return self._m_shy_enabled

            self._m_shy_enabled = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 6)) != 0
            return getattr(self, '_m_shy_enabled', None)

        @property
        def sampling_mode(self):
            if hasattr(self, '_m_sampling_mode'):
                return self._m_sampling_mode

            self._m_sampling_mode = KaitaiStream.resolve_enum(Aep.LayerSamplingMode, ((KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 6)) >> 6))
            return getattr(self, '_m_sampling_mode', None)

        @property
        def audio_enabled(self):
            if hasattr(self, '_m_audio_enabled'):
                return self._m_audio_enabled

            self._m_audio_enabled = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 1)) != 0
            return getattr(self, '_m_audio_enabled', None)



