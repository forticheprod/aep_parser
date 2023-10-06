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
        asset = 0
        light = 1
        camera = 2
        text = 3
        shape = 4

    class LabelColor(Enum):
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

    class LayerSamplingMode(Enum):
        bilinear = 0
        bicubic = 1

    class Depth(Enum):
        bpc_8 = 0
        bpc_16 = 1
        bpc_32 = 2

    class ItemType(Enum):
        folder = 1
        composition = 4
        asset = 7

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
        self.file_size = self._io.read_u4be()
        self.format = self._io.read_bytes(4)
        if not self.format == b"\x45\x67\x67\x21":
            raise kaitaistruct.ValidationNotEqualError(b"\x45\x67\x67\x21", self.format, self._io, u"/seq/2")
        self._raw_data = self._io.read_bytes((self.file_size - 4))
        _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
        self.data = Aep.Chunks(_io__raw_data, self, self._root)
        self.xmp = (self._io.read_bytes_full()).decode(u"utf8")

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
            self.chunk_size = self._io.read_u4be()
            _on = self.chunk_type
            if _on == u"head":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.HeadBody(_io__raw_data, self, self._root)
            elif _on == u"cdat":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.CdatBody(_io__raw_data, self, self._root)
            elif _on == u"pard":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.PardBody(_io__raw_data, self, self._root)
            elif _on == u"Utf8":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"nnhd":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.NnhdBody(_io__raw_data, self, self._root)
            elif _on == u"ldta":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.LdtaBody(_io__raw_data, self, self._root)
            elif _on == u"nhed":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.NhedBody(_io__raw_data, self, self._root)
            elif _on == u"alas":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"idta":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.IdtaBody(_io__raw_data, self, self._root)
            elif _on == u"tdmn":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"LIST":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ListBody(_io__raw_data, self, self._root)
            elif _on == u"fnam":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
            elif _on == u"tdsb":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.TdsbBody(_io__raw_data, self, self._root)
            elif _on == u"fdta":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.FdtaBody(_io__raw_data, self, self._root)
            elif _on == u"tdsn":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
            elif _on == u"cdta":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.CdtaBody(_io__raw_data, self, self._root)
            elif _on == u"tdb4":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Tdb4Body(_io__raw_data, self, self._root)
            elif _on == u"pjef":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"cmta":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"sspc":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.SspcBody(_io__raw_data, self, self._root)
            elif _on == u"pdnm":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
            elif _on == u"opti":
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.OptiBody(_io__raw_data, self, self._root)
            else:
                self._raw_data = self._io.read_bytes(((self._io.size() - self._io.pos()) if self.chunk_size > (self._io.size() - self._io.pos()) else self.chunk_size))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.AsciiBody(_io__raw_data, self, self._root)
            if (self.chunk_size % 2) != 0:
                self.padding = self._io.read_bytes(1)



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
            self.x_resolution = self._io.read_u2be()
            self.y_resolution = self._io.read_u2be()
            self.unknown01 = self._io.read_bytes(2)
            self.time_scale = self._io.read_u2be()
            self.unknown02 = self._io.read_bytes(2)
            self.framerate_dividend = self._io.read_u2be()
            self.unknown03 = self._io.read_bytes(9)
            self.playhead = self._io.read_u2be()
            self.unknown04 = self._io.read_bytes(6)
            self.in_time = self._io.read_u2be()
            self.unknown05 = self._io.read_bytes(6)
            self.out_time_raw = self._io.read_u2be()
            self.unknown06 = self._io.read_bytes(5)
            self.duration_dividend = self._io.read_u4be()
            self.duration_divisor = self._io.read_u4be()
            self.background_color = []
            for i in range(3):
                self.background_color.append(self._io.read_u1())

            self.unknown08 = self._io.read_bytes(84)
            self.attributes = self._io.read_bytes(1)
            self.width = self._io.read_u2be()
            self.height = self._io.read_u2be()
            self.pixel_ratio_width = self._io.read_u4be()
            self.pixel_ratio_height = self._io.read_u4be()
            self.unknown09 = self._io.read_bytes(4)
            self.frame_rate_integer = self._io.read_u2be()
            self.unknown10 = self._io.read_bytes(16)
            self.shutter_angle = self._io.read_u2be()
            self.shutter_phase = self._io.read_u4be()
            self.unknown11 = self._io.read_bytes(16)
            self.samples_limit = self._io.read_s4be()
            self.samples_per_frame = self._io.read_s4be()

        @property
        def out_time_frames(self):
            if hasattr(self, '_m_out_time_frames'):
                return self._m_out_time_frames

            self._m_out_time_frames = (self.out_time * self.framerate)
            return getattr(self, '_m_out_time_frames', None)

        @property
        def duration_sec(self):
            if hasattr(self, '_m_duration_sec'):
                return self._m_duration_sec

            self._m_duration_sec = (self.duration_dividend / self.duration_divisor)
            return getattr(self, '_m_duration_sec', None)

        @property
        def preserve_resolution(self):
            if hasattr(self, '_m_preserve_resolution'):
                return self._m_preserve_resolution

            self._m_preserve_resolution = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 7)) != 0
            return getattr(self, '_m_preserve_resolution', None)

        @property
        def frame_blend_enabled(self):
            if hasattr(self, '_m_frame_blend_enabled'):
                return self._m_frame_blend_enabled

            self._m_frame_blend_enabled = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 4)) != 0
            return getattr(self, '_m_frame_blend_enabled', None)

        @property
        def duration_frames(self):
            if hasattr(self, '_m_duration_frames'):
                return self._m_duration_frames

            self._m_duration_frames = (self.duration_sec * self.framerate)
            return getattr(self, '_m_duration_frames', None)

        @property
        def motion_blur_enabled(self):
            if hasattr(self, '_m_motion_blur_enabled'):
                return self._m_motion_blur_enabled

            self._m_motion_blur_enabled = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 3)) != 0
            return getattr(self, '_m_motion_blur_enabled', None)

        @property
        def out_time(self):
            if hasattr(self, '_m_out_time'):
                return self._m_out_time

            self._m_out_time = (self.duration_sec if self.out_time_raw == 65535 else self.out_time_raw)
            return getattr(self, '_m_out_time', None)

        @property
        def playhead_frames(self):
            if hasattr(self, '_m_playhead_frames'):
                return self._m_playhead_frames

            self._m_playhead_frames = (self.playhead * self.framerate)
            return getattr(self, '_m_playhead_frames', None)

        @property
        def in_time_frames(self):
            if hasattr(self, '_m_in_time_frames'):
                return self._m_in_time_frames

            self._m_in_time_frames = (self.in_time * self.framerate)
            return getattr(self, '_m_in_time_frames', None)

        @property
        def preserve_framerate(self):
            if hasattr(self, '_m_preserve_framerate'):
                return self._m_preserve_framerate

            self._m_preserve_framerate = (KaitaiStream.byte_array_index(self.attributes, 0) & (1 << 5)) != 0
            return getattr(self, '_m_preserve_framerate', None)

        @property
        def framerate(self):
            if hasattr(self, '_m_framerate'):
                return self._m_framerate

            self._m_framerate = (self.framerate_dividend / self.time_scale)
            return getattr(self, '_m_framerate', None)

        @property
        def shy_enabled(self):
            if hasattr(self, '_m_shy_enabled'):
                return self._m_shy_enabled

            self._m_shy_enabled = (KaitaiStream.byte_array_index(self.attributes, 0) & 1) != 0
            return getattr(self, '_m_shy_enabled', None)

        @property
        def pixel_ratio(self):
            if hasattr(self, '_m_pixel_ratio'):
                return self._m_pixel_ratio

            self._m_pixel_ratio = (self.pixel_ratio_width / self.pixel_ratio_height)
            return getattr(self, '_m_pixel_ratio', None)


    class Tdb4Body(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown01 = self._io.read_bytes(2)
            self.components = self._io.read_u2be()
            self.attributes = self._io.read_bytes(2)
            self.unknown02 = self._io.read_bytes(1)
            self.unknown03 = self._io.read_bytes(1)
            self.unknown04 = self._io.read_bytes(2)
            self.unknown05 = self._io.read_bytes(2)
            self.unknown06 = self._io.read_bytes(2)
            self.unknown07 = self._io.read_bytes(2)
            self.unknown08 = self._io.read_f8be()
            self.unknown09 = self._io.read_f8be()
            self.unknown10 = self._io.read_f8be()
            self.unknown11 = self._io.read_f8be()
            self.unknown12 = self._io.read_f8be()
            self.property_type = self._io.read_bytes(4)
            self.unknown13 = self._io.read_bytes(1)
            self.unknown14 = self._io.read_bytes(7)
            self.animated = self._io.read_u1()
            self.unknown15 = self._io.read_bytes(7)
            self.unknown16 = self._io.read_bytes(4)
            self.unknown17 = self._io.read_bytes(4)
            self.unknown18 = self._io.read_f8be()
            self.unknown19 = self._io.read_f8be()
            self.unknown20 = self._io.read_f8be()
            self.unknown21 = self._io.read_f8be()
            self.unknown22 = self._io.read_bytes(4)
            self.unknown23 = self._io.read_bytes(4)

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


    class NnhdBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown01 = self._io.read_bytes(14)
            self.framerate = self._io.read_u2be()
            self.unknown02 = self._io.read_bytes(24)


    class FdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown01 = self._io.read_bytes(1)


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
            self.unknown01 = self._io.read_bytes(14)
            self.item_id = self._io.read_u4be()
            self.unknown02 = self._io.read_bytes(38)
            self.label_color = KaitaiStream.resolve_enum(Aep.LabelColor, self._io.read_u1())


    class SspcBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown01 = self._io.read_bytes(32)
            self.width = self._io.read_u2be()
            self.unknown02 = self._io.read_bytes(2)
            self.height = self._io.read_u2be()
            self.duration_dividend = self._io.read_u4be()
            self.duration_divisor = self._io.read_u4be()
            self.unknown03 = self._io.read_bytes(10)
            self.framerate_base = self._io.read_u4be()
            self.framerate_dividend = self._io.read_u2be()
            self.unknown04 = self._io.read_bytes(110)
            self.start_frame = self._io.read_u4be()
            self.end_frame = self._io.read_u4be()

        @property
        def duration_sec(self):
            if hasattr(self, '_m_duration_sec'):
                return self._m_duration_sec

            self._m_duration_sec = (self.duration_dividend / self.duration_divisor)
            return getattr(self, '_m_duration_sec', None)

        @property
        def framerate(self):
            if hasattr(self, '_m_framerate'):
                return self._m_framerate

            self._m_framerate = (self.framerate_base + (self.framerate_dividend / (1 << 16)))
            return getattr(self, '_m_framerate', None)

        @property
        def duration_frames(self):
            if hasattr(self, '_m_duration_frames'):
                return self._m_duration_frames

            self._m_duration_frames = (self.duration_sec * self.framerate)
            return getattr(self, '_m_duration_frames', None)


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
                self.unknown02 = self._io.read_bytes(4)

            if self.asset_type == u"Soli":
                self.color = []
                for i in range(4):
                    self.color.append(self._io.read_f4be())


            if self.asset_type == u"Soli":
                self.solid_name = (KaitaiStream.bytes_terminate(self._io.read_bytes(256), 0, False)).decode(u"cp1250")

            if self.asset_type_int == 2:
                self.unknown03 = self._io.read_bytes(4)

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
            self.unknown01 = self._io.read_bytes(15)
            self.depth = KaitaiStream.resolve_enum(Aep.Depth, self._io.read_u1())


    class HeadBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ae_version = self._io.read_bytes(6)
            self.unknown01 = self._io.read_bytes(12)
            self.file_revision = self._io.read_u2be()


    class AlasBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.contents = (self._io.read_bytes_full()).decode(u"ascii")


    class CdatBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.value = []
            for i in range(self._parent.chunk_size // 8):
                self.value.append(self._io.read_f8be())



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
            self.unknown01 = self._io.read_bytes(15)
            self.property_type = KaitaiStream.resolve_enum(Aep.PropertyType, self._io.read_u1())
            self.name = (self._io.read_bytes(32)).decode(u"cp1250")
            self.unknown02 = self._io.read_bytes(8)
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
                self.option_count = self._io.read_s4be()

            if  ((self.property_type == Aep.PropertyType.boolean) or (self.property_type == Aep.PropertyType.enum)) :
                _on = self.property_type
                if _on == Aep.PropertyType.boolean:
                    self.default = self._io.read_u1()
                elif _on == Aep.PropertyType.enum:
                    self.default = self._io.read_s4be()

            if  ((self.property_type == Aep.PropertyType.scalar) or (self.property_type == Aep.PropertyType.color) or (self.property_type == Aep.PropertyType.slider)) :
                self.unknown03 = self._io.read_bytes((72 if self.property_type == Aep.PropertyType.scalar else (64 if self.property_type == Aep.PropertyType.color else 52)))

            if self.property_type == Aep.PropertyType.scalar:
                self.min_value = self._io.read_s2be()

            if self.property_type == Aep.PropertyType.scalar:
                self.unknown04 = self._io.read_bytes(2)

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
            self.unknown01 = self._io.read_bytes(4)
            self.stretch_numerator = self._io.read_u2be()
            self.unknown02 = self._io.read_bytes(1)
            self.start_time_sec = self._io.read_s2be()
            self.unknown03 = self._io.read_bytes(6)
            self.in_time_sec = self._io.read_u2be()
            self.unknown04 = self._io.read_bytes(6)
            self.out_time_sec = self._io.read_u2be()
            self.unknown05 = self._io.read_bytes(6)
            self.attributes = self._io.read_bytes(3)
            self.source_id = self._io.read_u4be()
            self.unknown06 = self._io.read_bytes(17)
            self.label_color = KaitaiStream.resolve_enum(Aep.LabelColor, self._io.read_u1())
            self.unknown07 = self._io.read_bytes(2)
            self.layer_name = (self._io.read_bytes(32)).decode(u"cp1250")
            self.unknown08 = self._io.read_bytes(11)
            self.matte_mode = KaitaiStream.resolve_enum(Aep.MatteMode, self._io.read_u1())
            self.unknown09 = self._io.read_bytes(2)
            self.stretch_denominator = self._io.read_u2be()
            self.unknown10 = self._io.read_bytes(19)
            self.layer_type = KaitaiStream.resolve_enum(Aep.LayerType, self._io.read_u1())
            self.parent_id = self._io.read_u4be()
            self.unknown11 = self._io.read_bytes(24)

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
        def frame_blend_enabled(self):
            if hasattr(self, '_m_frame_blend_enabled'):
                return self._m_frame_blend_enabled

            self._m_frame_blend_enabled = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 4)) != 0
            return getattr(self, '_m_frame_blend_enabled', None)

        @property
        def video_enabled(self):
            if hasattr(self, '_m_video_enabled'):
                return self._m_video_enabled

            self._m_video_enabled = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 0)) != 0
            return getattr(self, '_m_video_enabled', None)

        @property
        def motion_blur_enabled(self):
            if hasattr(self, '_m_motion_blur_enabled'):
                return self._m_motion_blur_enabled

            self._m_motion_blur_enabled = (KaitaiStream.byte_array_index(self.attributes, 2) & (1 << 3)) != 0
            return getattr(self, '_m_motion_blur_enabled', None)

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



