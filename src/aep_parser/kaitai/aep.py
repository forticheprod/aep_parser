# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Aep(ReadWriteKaitaiStruct):

    class AssetType(IntEnum):
        placeholder = 2
        solid = 9

    class ItemType(IntEnum):
        folder = 1
        composition = 4
        footage = 7

    class Label(IntEnum):
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

    class LayerType(IntEnum):
        footage = 0
        light = 1
        camera = 2
        text = 3
        shape = 4

    class LdatItemType(IntEnum):
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

    class PropertyControlType(IntEnum):
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
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Aep, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.header = self._io.read_bytes(4)
        if not self.header == b"\x52\x49\x46\x58":
            raise kaitaistruct.ValidationNotEqualError(b"\x52\x49\x46\x58", self.header, self._io, u"/seq/0")
        self.len_data = self._io.read_u4be()
        self.format = self._io.read_bytes(4)
        if not self.format == b"\x45\x67\x67\x21":
            raise kaitaistruct.ValidationNotEqualError(b"\x45\x67\x67\x21", self.format, self._io, u"/seq/2")
        self._raw_data = self._io.read_bytes(self.len_data - 4)
        _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
        self.data = Aep.Chunks(_io__raw_data, self, self._root)
        self.data._read()
        self.xmp_packet = (self._io.read_bytes_full()).decode(u"UTF-8")
        self._dirty = False


    def _fetch_instances(self):
        pass
        self.data._fetch_instances()


    def _write__seq(self, io=None):
        super(Aep, self)._write__seq(io)
        self._io.write_bytes(self.header)
        self._io.write_u4be(self.len_data)
        self._io.write_bytes(self.format)
        _io__raw_data = KaitaiStream(BytesIO(bytearray(self.len_data - 4)))
        self._io.add_child_stream(_io__raw_data)
        _pos2 = self._io.pos()
        self._io.seek(self._io.pos() + (self.len_data - 4))
        def handler(parent, _io__raw_data=_io__raw_data):
            self._raw_data = _io__raw_data.to_byte_array()
            if len(self._raw_data) != self.len_data - 4:
                raise kaitaistruct.ConsistencyError(u"raw(data)", self.len_data - 4, len(self._raw_data))
            parent.write_bytes(self._raw_data)
        _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
        self.data._write__seq(_io__raw_data)
        self._io.write_bytes((self.xmp_packet).encode(u"UTF-8"))
        if not self._io.is_eof():
            raise kaitaistruct.ConsistencyError(u"xmp_packet", 0, self._io.size() - self._io.pos())


    def _check(self):
        if len(self.header) != 4:
            raise kaitaistruct.ConsistencyError(u"header", 4, len(self.header))
        if not self.header == b"\x52\x49\x46\x58":
            raise kaitaistruct.ValidationNotEqualError(b"\x52\x49\x46\x58", self.header, None, u"/seq/0")
        if len(self.format) != 4:
            raise kaitaistruct.ConsistencyError(u"format", 4, len(self.format))
        if not self.format == b"\x45\x67\x67\x21":
            raise kaitaistruct.ValidationNotEqualError(b"\x45\x67\x67\x21", self.format, None, u"/seq/2")
        if self.data._root != self._root:
            raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
        if self.data._parent != self:
            raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
        self._dirty = False

    class AcerBody(ReadWriteKaitaiStruct):
        """Compensate for Scene-Referred Profiles setting in Project Settings.
        This setting affects how scene-referred color profiles are handled.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.AcerBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.compensate_for_scene_referred_profiles = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.AcerBody, self)._write__seq(io)
            self._io.write_u1(self.compensate_for_scene_referred_profiles)


        def _check(self):
            self._dirty = False


    class AsciiBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.AsciiBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.contents = self._io.read_bytes_full()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.AsciiBody, self)._write__seq(io)
            self._io.write_bytes(self.contents)
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"contents", 0, self._io.size() - self._io.pos())


        def _check(self):
            self._dirty = False


    class CdatBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.CdatBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.value = []
            for i in range(self._parent.len_data // 8):
                self.value.append(self._io.read_f8be())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.value)):
                pass



        def _write__seq(self, io=None):
            super(Aep.CdatBody, self)._write__seq(io)
            for i in range(len(self.value)):
                pass
                self._io.write_f8be(self.value[i])



        def _check(self):
            if len(self.value) != self._parent.len_data // 8:
                raise kaitaistruct.ConsistencyError(u"value", self._parent.len_data // 8, len(self.value))
            for i in range(len(self.value)):
                pass

            self._dirty = False


    class CdtaBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.CdtaBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.resolution_factor = []
            for i in range(2):
                self.resolution_factor.append(self._io.read_u2be())

            self._unnamed1 = self._io.read_bytes(1)
            self.time_scale = self._io.read_u2be()
            self._unnamed3 = self._io.read_bytes(14)
            self.time_raw = self._io.read_u2be()
            self._unnamed5 = self._io.read_bytes(6)
            self.in_point_raw = self._io.read_u2be()
            self._unnamed7 = self._io.read_bytes(6)
            self.out_point_raw = self._io.read_u2be()
            self._unnamed9 = self._io.read_bytes(5)
            self.duration_dividend = self._io.read_u4be()
            self.duration_divisor = self._io.read_u4be()
            self.bg_color = []
            for i in range(3):
                self.bg_color.append(self._io.read_u1())

            self._unnamed13 = self._io.read_bytes(84)
            self.preserve_nested_resolution = self._io.read_bits_int_be(1) != 0
            self._unnamed15 = self._io.read_bits_int_be(1) != 0
            self.preserve_nested_frame_rate = self._io.read_bits_int_be(1) != 0
            self.frame_blending = self._io.read_bits_int_be(1) != 0
            self.motion_blur = self._io.read_bits_int_be(1) != 0
            self._unnamed19 = self._io.read_bits_int_be(2)
            self.hide_shy_layers = self._io.read_bits_int_be(1) != 0
            self.width = self._io.read_u2be()
            self.height = self._io.read_u2be()
            self.pixel_ratio_width = self._io.read_u4be()
            self.pixel_ratio_height = self._io.read_u4be()
            self._unnamed25 = self._io.read_bytes(4)
            self.frame_rate_integer = self._io.read_u2be()
            self.frame_rate_fractional = self._io.read_u2be()
            self._unnamed28 = self._io.read_bytes(4)
            self.display_start_time_dividend = self._io.read_u4be()
            self.display_start_time_divisor = self._io.read_u4be()
            self._unnamed31 = self._io.read_bytes(2)
            self.shutter_angle = self._io.read_u2be()
            self._unnamed33 = self._io.read_bytes(4)
            self.shutter_phase = self._io.read_s4be()
            self._unnamed35 = self._io.read_bytes(12)
            self.motion_blur_adaptive_sample_limit = self._io.read_s4be()
            self.motion_blur_samples_per_frame = self._io.read_s4be()
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.resolution_factor)):
                pass

            for i in range(len(self.bg_color)):
                pass



        def _write__seq(self, io=None):
            super(Aep.CdtaBody, self)._write__seq(io)
            for i in range(len(self.resolution_factor)):
                pass
                self._io.write_u2be(self.resolution_factor[i])

            self._io.write_bytes(self._unnamed1)
            self._io.write_u2be(self.time_scale)
            self._io.write_bytes(self._unnamed3)
            self._io.write_u2be(self.time_raw)
            self._io.write_bytes(self._unnamed5)
            self._io.write_u2be(self.in_point_raw)
            self._io.write_bytes(self._unnamed7)
            self._io.write_u2be(self.out_point_raw)
            self._io.write_bytes(self._unnamed9)
            self._io.write_u4be(self.duration_dividend)
            self._io.write_u4be(self.duration_divisor)
            for i in range(len(self.bg_color)):
                pass
                self._io.write_u1(self.bg_color[i])

            self._io.write_bytes(self._unnamed13)
            self._io.write_bits_int_be(1, int(self.preserve_nested_resolution))
            self._io.write_bits_int_be(1, int(self._unnamed15))
            self._io.write_bits_int_be(1, int(self.preserve_nested_frame_rate))
            self._io.write_bits_int_be(1, int(self.frame_blending))
            self._io.write_bits_int_be(1, int(self.motion_blur))
            self._io.write_bits_int_be(2, self._unnamed19)
            self._io.write_bits_int_be(1, int(self.hide_shy_layers))
            self._io.write_u2be(self.width)
            self._io.write_u2be(self.height)
            self._io.write_u4be(self.pixel_ratio_width)
            self._io.write_u4be(self.pixel_ratio_height)
            self._io.write_bytes(self._unnamed25)
            self._io.write_u2be(self.frame_rate_integer)
            self._io.write_u2be(self.frame_rate_fractional)
            self._io.write_bytes(self._unnamed28)
            self._io.write_u4be(self.display_start_time_dividend)
            self._io.write_u4be(self.display_start_time_divisor)
            self._io.write_bytes(self._unnamed31)
            self._io.write_u2be(self.shutter_angle)
            self._io.write_bytes(self._unnamed33)
            self._io.write_s4be(self.shutter_phase)
            self._io.write_bytes(self._unnamed35)
            self._io.write_s4be(self.motion_blur_adaptive_sample_limit)
            self._io.write_s4be(self.motion_blur_samples_per_frame)


        def _check(self):
            if len(self.resolution_factor) != 2:
                raise kaitaistruct.ConsistencyError(u"resolution_factor", 2, len(self.resolution_factor))
            for i in range(len(self.resolution_factor)):
                pass

            if len(self._unnamed1) != 1:
                raise kaitaistruct.ConsistencyError(u"_unnamed1", 1, len(self._unnamed1))
            if len(self._unnamed3) != 14:
                raise kaitaistruct.ConsistencyError(u"_unnamed3", 14, len(self._unnamed3))
            if len(self._unnamed5) != 6:
                raise kaitaistruct.ConsistencyError(u"_unnamed5", 6, len(self._unnamed5))
            if len(self._unnamed7) != 6:
                raise kaitaistruct.ConsistencyError(u"_unnamed7", 6, len(self._unnamed7))
            if len(self._unnamed9) != 5:
                raise kaitaistruct.ConsistencyError(u"_unnamed9", 5, len(self._unnamed9))
            if len(self.bg_color) != 3:
                raise kaitaistruct.ConsistencyError(u"bg_color", 3, len(self.bg_color))
            for i in range(len(self.bg_color)):
                pass

            if len(self._unnamed13) != 84:
                raise kaitaistruct.ConsistencyError(u"_unnamed13", 84, len(self._unnamed13))
            if len(self._unnamed25) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed25", 4, len(self._unnamed25))
            if len(self._unnamed28) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed28", 4, len(self._unnamed28))
            if len(self._unnamed31) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed31", 2, len(self._unnamed31))
            if len(self._unnamed33) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed33", 4, len(self._unnamed33))
            if len(self._unnamed35) != 12:
                raise kaitaistruct.ConsistencyError(u"_unnamed35", 12, len(self._unnamed35))
            self._dirty = False

        @property
        def display_start_frame(self):
            if hasattr(self, '_m_display_start_frame'):
                return self._m_display_start_frame

            self._m_display_start_frame = self.display_start_time * self.frame_rate
            return getattr(self, '_m_display_start_frame', None)

        def _invalidate_display_start_frame(self):
            del self._m_display_start_frame
        @property
        def display_start_time(self):
            if hasattr(self, '_m_display_start_time'):
                return self._m_display_start_time

            self._m_display_start_time = self.display_start_time_dividend / self.display_start_time_divisor
            return getattr(self, '_m_display_start_time', None)

        def _invalidate_display_start_time(self):
            del self._m_display_start_time
        @property
        def duration(self):
            if hasattr(self, '_m_duration'):
                return self._m_duration

            self._m_duration = self.duration_dividend / self.duration_divisor
            return getattr(self, '_m_duration', None)

        def _invalidate_duration(self):
            del self._m_duration
        @property
        def frame_duration(self):
            if hasattr(self, '_m_frame_duration'):
                return self._m_frame_duration

            self._m_frame_duration = self.duration * self.frame_rate
            return getattr(self, '_m_frame_duration', None)

        def _invalidate_frame_duration(self):
            del self._m_frame_duration
        @property
        def frame_in_point(self):
            if hasattr(self, '_m_frame_in_point'):
                return self._m_frame_in_point

            self._m_frame_in_point = self.display_start_frame + self.in_point_raw // self.time_scale
            return getattr(self, '_m_frame_in_point', None)

        def _invalidate_frame_in_point(self):
            del self._m_frame_in_point
        @property
        def frame_out_point(self):
            if hasattr(self, '_m_frame_out_point'):
                return self._m_frame_out_point

            self._m_frame_out_point = self.display_start_frame + (self.frame_duration if self.out_point_raw == 65535 else self.out_point_raw // self.time_scale)
            return getattr(self, '_m_frame_out_point', None)

        def _invalidate_frame_out_point(self):
            del self._m_frame_out_point
        @property
        def frame_rate(self):
            if hasattr(self, '_m_frame_rate'):
                return self._m_frame_rate

            self._m_frame_rate = self.frame_rate_integer + self.frame_rate_fractional / 65536.0
            return getattr(self, '_m_frame_rate', None)

        def _invalidate_frame_rate(self):
            del self._m_frame_rate
        @property
        def frame_time(self):
            if hasattr(self, '_m_frame_time'):
                return self._m_frame_time

            self._m_frame_time = self.time_raw // self.time_scale
            return getattr(self, '_m_frame_time', None)

        def _invalidate_frame_time(self):
            del self._m_frame_time
        @property
        def in_point(self):
            if hasattr(self, '_m_in_point'):
                return self._m_in_point

            self._m_in_point = self.frame_in_point / self.frame_rate
            return getattr(self, '_m_in_point', None)

        def _invalidate_in_point(self):
            del self._m_in_point
        @property
        def out_point(self):
            if hasattr(self, '_m_out_point'):
                return self._m_out_point

            self._m_out_point = self.frame_out_point / self.frame_rate
            return getattr(self, '_m_out_point', None)

        def _invalidate_out_point(self):
            del self._m_out_point
        @property
        def pixel_aspect(self):
            if hasattr(self, '_m_pixel_aspect'):
                return self._m_pixel_aspect

            self._m_pixel_aspect = self.pixel_ratio_width / self.pixel_ratio_height
            return getattr(self, '_m_pixel_aspect', None)

        def _invalidate_pixel_aspect(self):
            del self._m_pixel_aspect
        @property
        def time(self):
            if hasattr(self, '_m_time'):
                return self._m_time

            self._m_time = self.frame_time / self.frame_rate
            return getattr(self, '_m_time', None)

        def _invalidate_time(self):
            del self._m_time

    class ChildUtf8Body(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.ChildUtf8Body, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.chunk = Aep.Chunk(self._io, self, self._root)
            self.chunk._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.chunk._fetch_instances()


        def _write__seq(self, io=None):
            super(Aep.ChildUtf8Body, self)._write__seq(io)
            self.chunk._write__seq(self._io)


        def _check(self):
            if self.chunk._root != self._root:
                raise kaitaistruct.ConsistencyError(u"chunk", self._root, self.chunk._root)
            if self.chunk._parent != self:
                raise kaitaistruct.ConsistencyError(u"chunk", self, self.chunk._parent)
            self._dirty = False


    class Chunk(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.Chunk, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.chunk_type = (self._io.read_bytes(4)).decode(u"ASCII")
            self.len_data = self._io.read_u4be()
            _on = self.chunk_type
            if _on == u"LIST":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ListBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"NmHd":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.NmhdBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"RCom":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"Rhed":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.RhedBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"Roou":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.RoouBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"Rout":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.RoutBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"Utf8":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"acer":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.AcerBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"alas":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"cdat":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.CdatBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"cdta":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.CdtaBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"cmta":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"dwga":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.DwgaBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"fdta":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.FdtaBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"fnam":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"head":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.HeadBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"idta":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.IdtaBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"ldat":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.LdatBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"ldta":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.LdtaBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"lhd3":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Lhd3Body(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"nnhd":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.NnhdBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"opti":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.OptiBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"pard":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.PardBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"pdnm":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"pjef":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"sspc":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.SspcBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"tdb4":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Tdb4Body(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"tdmn":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"tdsb":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.TdsbBody(_io__raw_data, self, self._root)
                self.data._read()
            elif _on == u"tdsn":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
                self.data._read()
            else:
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.AsciiBody(_io__raw_data, self, self._root)
                self.data._read()
            if self.len_data % 2 != 0:
                pass
                self.padding = self._io.read_bytes(1)

            self._dirty = False


        def _fetch_instances(self):
            pass
            _on = self.chunk_type
            if _on == u"LIST":
                pass
                self.data._fetch_instances()
            elif _on == u"NmHd":
                pass
                self.data._fetch_instances()
            elif _on == u"RCom":
                pass
                self.data._fetch_instances()
            elif _on == u"Rhed":
                pass
                self.data._fetch_instances()
            elif _on == u"Roou":
                pass
                self.data._fetch_instances()
            elif _on == u"Rout":
                pass
                self.data._fetch_instances()
            elif _on == u"Utf8":
                pass
                self.data._fetch_instances()
            elif _on == u"acer":
                pass
                self.data._fetch_instances()
            elif _on == u"alas":
                pass
                self.data._fetch_instances()
            elif _on == u"cdat":
                pass
                self.data._fetch_instances()
            elif _on == u"cdta":
                pass
                self.data._fetch_instances()
            elif _on == u"cmta":
                pass
                self.data._fetch_instances()
            elif _on == u"dwga":
                pass
                self.data._fetch_instances()
            elif _on == u"fdta":
                pass
                self.data._fetch_instances()
            elif _on == u"fnam":
                pass
                self.data._fetch_instances()
            elif _on == u"head":
                pass
                self.data._fetch_instances()
            elif _on == u"idta":
                pass
                self.data._fetch_instances()
            elif _on == u"ldat":
                pass
                self.data._fetch_instances()
            elif _on == u"ldta":
                pass
                self.data._fetch_instances()
            elif _on == u"lhd3":
                pass
                self.data._fetch_instances()
            elif _on == u"nnhd":
                pass
                self.data._fetch_instances()
            elif _on == u"opti":
                pass
                self.data._fetch_instances()
            elif _on == u"pard":
                pass
                self.data._fetch_instances()
            elif _on == u"pdnm":
                pass
                self.data._fetch_instances()
            elif _on == u"pjef":
                pass
                self.data._fetch_instances()
            elif _on == u"sspc":
                pass
                self.data._fetch_instances()
            elif _on == u"tdb4":
                pass
                self.data._fetch_instances()
            elif _on == u"tdmn":
                pass
                self.data._fetch_instances()
            elif _on == u"tdsb":
                pass
                self.data._fetch_instances()
            elif _on == u"tdsn":
                pass
                self.data._fetch_instances()
            else:
                pass
                self.data._fetch_instances()
            if self.len_data % 2 != 0:
                pass



        def _write__seq(self, io=None):
            super(Aep.Chunk, self)._write__seq(io)
            self._io.write_bytes((self.chunk_type).encode(u"ASCII"))
            self._io.write_u4be(self.len_data)
            _on = self.chunk_type
            if _on == u"LIST":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"NmHd":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"RCom":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"Rhed":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"Roou":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"Rout":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"Utf8":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"acer":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"alas":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"cdat":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"cdta":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"cmta":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"dwga":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"fdta":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"fnam":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"head":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"idta":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"ldat":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"ldta":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"lhd3":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"nnhd":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"opti":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"pard":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"pdnm":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"pjef":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"sspc":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"tdb4":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"tdmn":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"tdsb":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            elif _on == u"tdsn":
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            else:
                pass
                _io__raw_data = KaitaiStream(BytesIO(bytearray((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))))
                self._io.add_child_stream(_io__raw_data)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + ((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data)))
                def handler(parent, _io__raw_data=_io__raw_data):
                    self._raw_data = _io__raw_data.to_byte_array()
                    if len(self._raw_data) != (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data):
                        raise kaitaistruct.ConsistencyError(u"raw(data)", (self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data), len(self._raw_data))
                    parent.write_bytes(self._raw_data)
                _io__raw_data.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.data._write__seq(_io__raw_data)
            if self.len_data % 2 != 0:
                pass
                self._io.write_bytes(self.padding)



        def _check(self):
            if len((self.chunk_type).encode(u"ASCII")) != 4:
                raise kaitaistruct.ConsistencyError(u"chunk_type", 4, len((self.chunk_type).encode(u"ASCII")))
            _on = self.chunk_type
            if _on == u"LIST":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"NmHd":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"RCom":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"Rhed":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"Roou":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"Rout":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"Utf8":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"acer":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"alas":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"cdat":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"cdta":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"cmta":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"dwga":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"fdta":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"fnam":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"head":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"idta":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"ldat":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"ldta":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"lhd3":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"nnhd":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"opti":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"pard":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"pdnm":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"pjef":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"sspc":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"tdb4":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"tdmn":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"tdsb":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            elif _on == u"tdsn":
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            else:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
            if self.len_data % 2 != 0:
                pass
                if len(self.padding) != 1:
                    raise kaitaistruct.ConsistencyError(u"padding", 1, len(self.padding))

            self._dirty = False


    class Chunks(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.Chunks, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.chunks = []
            i = 0
            while not self._io.is_eof():
                _t_chunks = Aep.Chunk(self._io, self, self._root)
                try:
                    _t_chunks._read()
                finally:
                    self.chunks.append(_t_chunks)
                i += 1

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.chunks)):
                pass
                self.chunks[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Aep.Chunks, self)._write__seq(io)
            for i in range(len(self.chunks)):
                pass
                if self._io.is_eof():
                    raise kaitaistruct.ConsistencyError(u"chunks", 0, self._io.size() - self._io.pos())
                self.chunks[i]._write__seq(self._io)

            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"chunks", 0, self._io.size() - self._io.pos())


        def _check(self):
            for i in range(len(self.chunks)):
                pass
                if self.chunks[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"chunks", self._root, self.chunks[i]._root)
                if self.chunks[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"chunks", self, self.chunks[i]._parent)

            self._dirty = False


    class DwgaBody(ReadWriteKaitaiStruct):
        """Working gamma setting. Indicates the gamma value used for color management.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.DwgaBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.working_gamma_selector = self._io.read_u1()
            self._unnamed1 = self._io.read_bytes(3)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.DwgaBody, self)._write__seq(io)
            self._io.write_u1(self.working_gamma_selector)
            self._io.write_bytes(self._unnamed1)


        def _check(self):
            if len(self._unnamed1) != 3:
                raise kaitaistruct.ConsistencyError(u"_unnamed1", 3, len(self._unnamed1))
            self._dirty = False


    class FdtaBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.FdtaBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bytes(1)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.FdtaBody, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)


        def _check(self):
            if len(self._unnamed0) != 1:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 1, len(self._unnamed0))
            self._dirty = False


    class HeadBody(ReadWriteKaitaiStruct):
        """After Effects file header. Contains version info encoded as a 32-bit value.
        Major version = MAJOR-A * 8 + MAJOR-B
        See: https://github.com/tinogithub/aftereffects-version-check
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.HeadBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bytes(4)
            self._unnamed1 = self._io.read_bits_int_be(1) != 0
            self.ae_version_major_a = self._io.read_bits_int_be(5)
            self.ae_version_os = self._io.read_bits_int_be(4)
            self.ae_version_major_b = self._io.read_bits_int_be(3)
            self.ae_version_minor = self._io.read_bits_int_be(4)
            self.ae_version_patch = self._io.read_bits_int_be(4)
            self._unnamed7 = self._io.read_bits_int_be(1) != 0
            self.ae_version_beta_flag = self._io.read_bits_int_be(1) != 0
            self._unnamed9 = self._io.read_bits_int_be(1) != 0
            self.ae_build_number = self._io.read_bits_int_be(8)
            self._unnamed11 = self._io.read_bytes(10)
            self.file_revision = self._io.read_u2be()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.HeadBody, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)
            self._io.write_bits_int_be(1, int(self._unnamed1))
            self._io.write_bits_int_be(5, self.ae_version_major_a)
            self._io.write_bits_int_be(4, self.ae_version_os)
            self._io.write_bits_int_be(3, self.ae_version_major_b)
            self._io.write_bits_int_be(4, self.ae_version_minor)
            self._io.write_bits_int_be(4, self.ae_version_patch)
            self._io.write_bits_int_be(1, int(self._unnamed7))
            self._io.write_bits_int_be(1, int(self.ae_version_beta_flag))
            self._io.write_bits_int_be(1, int(self._unnamed9))
            self._io.write_bits_int_be(8, self.ae_build_number)
            self._io.write_bytes(self._unnamed11)
            self._io.write_u2be(self.file_revision)


        def _check(self):
            if len(self._unnamed0) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 4, len(self._unnamed0))
            if len(self._unnamed11) != 10:
                raise kaitaistruct.ConsistencyError(u"_unnamed11", 10, len(self._unnamed11))
            self._dirty = False

        @property
        def ae_version_beta(self):
            """True if beta version."""
            if hasattr(self, '_m_ae_version_beta'):
                return self._m_ae_version_beta

            self._m_ae_version_beta = (not (self.ae_version_beta_flag))
            return getattr(self, '_m_ae_version_beta', None)

        def _invalidate_ae_version_beta(self):
            del self._m_ae_version_beta
        @property
        def ae_version_major(self):
            """Full major version number (e.g., 25)."""
            if hasattr(self, '_m_ae_version_major'):
                return self._m_ae_version_major

            self._m_ae_version_major = self.ae_version_major_a * 8 + self.ae_version_major_b
            return getattr(self, '_m_ae_version_major', None)

        def _invalidate_ae_version_major(self):
            del self._m_ae_version_major

    class IdtaBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.IdtaBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.item_type = KaitaiStream.resolve_enum(Aep.ItemType, self._io.read_u2be())
            self._unnamed1 = self._io.read_bytes(14)
            self.id = self._io.read_u4be()
            self._unnamed3 = self._io.read_bytes(38)
            self.label = KaitaiStream.resolve_enum(Aep.Label, self._io.read_u1())
            self._unnamed5 = self._io.read_bytes_full()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.IdtaBody, self)._write__seq(io)
            self._io.write_u2be(int(self.item_type))
            self._io.write_bytes(self._unnamed1)
            self._io.write_u4be(self.id)
            self._io.write_bytes(self._unnamed3)
            self._io.write_u1(int(self.label))
            self._io.write_bytes(self._unnamed5)
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"_unnamed5", 0, self._io.size() - self._io.pos())


        def _check(self):
            if len(self._unnamed1) != 14:
                raise kaitaistruct.ConsistencyError(u"_unnamed1", 14, len(self._unnamed1))
            if len(self._unnamed3) != 38:
                raise kaitaistruct.ConsistencyError(u"_unnamed3", 38, len(self._unnamed3))
            self._dirty = False


    class KfColor(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.KfColor, self).__init__(_io)
            self._parent = _parent
            self._root = _root

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

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.value)):
                pass

            for i in range(len(self._unnamed7)):
                pass



        def _write__seq(self, io=None):
            super(Aep.KfColor, self)._write__seq(io)
            self._io.write_u8be(self._unnamed0)
            self._io.write_f8be(self._unnamed1)
            self._io.write_f8be(self.in_speed)
            self._io.write_f8be(self.in_influence)
            self._io.write_f8be(self.out_speed)
            self._io.write_f8be(self.out_influence)
            for i in range(len(self.value)):
                pass
                self._io.write_f8be(self.value[i])

            for i in range(len(self._unnamed7)):
                pass
                self._io.write_f8be(self._unnamed7[i])



        def _check(self):
            if len(self.value) != 4:
                raise kaitaistruct.ConsistencyError(u"value", 4, len(self.value))
            for i in range(len(self.value)):
                pass

            if len(self._unnamed7) != 8:
                raise kaitaistruct.ConsistencyError(u"_unnamed7", 8, len(self._unnamed7))
            for i in range(len(self._unnamed7)):
                pass

            self._dirty = False


    class KfMultiDimensional(ReadWriteKaitaiStruct):
        def __init__(self, num_value, _io=None, _parent=None, _root=None):
            super(Aep.KfMultiDimensional, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.num_value = num_value

        def _read(self):
            self.value = []
            for i in range(self.num_value):
                self.value.append(self._io.read_f8be())

            self.in_speed = []
            for i in range(self.num_value):
                self.in_speed.append(self._io.read_f8be())

            self.in_influence = []
            for i in range(self.num_value):
                self.in_influence.append(self._io.read_f8be())

            self.out_speed = []
            for i in range(self.num_value):
                self.out_speed.append(self._io.read_f8be())

            self.out_influence = []
            for i in range(self.num_value):
                self.out_influence.append(self._io.read_f8be())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.value)):
                pass

            for i in range(len(self.in_speed)):
                pass

            for i in range(len(self.in_influence)):
                pass

            for i in range(len(self.out_speed)):
                pass

            for i in range(len(self.out_influence)):
                pass



        def _write__seq(self, io=None):
            super(Aep.KfMultiDimensional, self)._write__seq(io)
            for i in range(len(self.value)):
                pass
                self._io.write_f8be(self.value[i])

            for i in range(len(self.in_speed)):
                pass
                self._io.write_f8be(self.in_speed[i])

            for i in range(len(self.in_influence)):
                pass
                self._io.write_f8be(self.in_influence[i])

            for i in range(len(self.out_speed)):
                pass
                self._io.write_f8be(self.out_speed[i])

            for i in range(len(self.out_influence)):
                pass
                self._io.write_f8be(self.out_influence[i])



        def _check(self):
            if len(self.value) != self.num_value:
                raise kaitaistruct.ConsistencyError(u"value", self.num_value, len(self.value))
            for i in range(len(self.value)):
                pass

            if len(self.in_speed) != self.num_value:
                raise kaitaistruct.ConsistencyError(u"in_speed", self.num_value, len(self.in_speed))
            for i in range(len(self.in_speed)):
                pass

            if len(self.in_influence) != self.num_value:
                raise kaitaistruct.ConsistencyError(u"in_influence", self.num_value, len(self.in_influence))
            for i in range(len(self.in_influence)):
                pass

            if len(self.out_speed) != self.num_value:
                raise kaitaistruct.ConsistencyError(u"out_speed", self.num_value, len(self.out_speed))
            for i in range(len(self.out_speed)):
                pass

            if len(self.out_influence) != self.num_value:
                raise kaitaistruct.ConsistencyError(u"out_influence", self.num_value, len(self.out_influence))
            for i in range(len(self.out_influence)):
                pass

            self._dirty = False


    class KfNoValue(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.KfNoValue, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_u8be()
            self._unnamed1 = self._io.read_f8be()
            self.in_speed = self._io.read_f8be()
            self.in_influence = self._io.read_f8be()
            self.out_speed = self._io.read_f8be()
            self.out_influence = self._io.read_f8be()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.KfNoValue, self)._write__seq(io)
            self._io.write_u8be(self._unnamed0)
            self._io.write_f8be(self._unnamed1)
            self._io.write_f8be(self.in_speed)
            self._io.write_f8be(self.in_influence)
            self._io.write_f8be(self.out_speed)
            self._io.write_f8be(self.out_influence)


        def _check(self):
            self._dirty = False


    class KfPosition(ReadWriteKaitaiStruct):
        def __init__(self, num_value, _io=None, _parent=None, _root=None):
            super(Aep.KfPosition, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.num_value = num_value

        def _read(self):
            self._unnamed0 = self._io.read_u8be()
            self._unnamed1 = self._io.read_f8be()
            self.in_speed = self._io.read_f8be()
            self.in_influence = self._io.read_f8be()
            self.out_speed = self._io.read_f8be()
            self.out_influence = self._io.read_f8be()
            self.value = []
            for i in range(self.num_value):
                self.value.append(self._io.read_f8be())

            self.tan_in = []
            for i in range(self.num_value):
                self.tan_in.append(self._io.read_f8be())

            self.tan_out = []
            for i in range(self.num_value):
                self.tan_out.append(self._io.read_f8be())

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.value)):
                pass

            for i in range(len(self.tan_in)):
                pass

            for i in range(len(self.tan_out)):
                pass



        def _write__seq(self, io=None):
            super(Aep.KfPosition, self)._write__seq(io)
            self._io.write_u8be(self._unnamed0)
            self._io.write_f8be(self._unnamed1)
            self._io.write_f8be(self.in_speed)
            self._io.write_f8be(self.in_influence)
            self._io.write_f8be(self.out_speed)
            self._io.write_f8be(self.out_influence)
            for i in range(len(self.value)):
                pass
                self._io.write_f8be(self.value[i])

            for i in range(len(self.tan_in)):
                pass
                self._io.write_f8be(self.tan_in[i])

            for i in range(len(self.tan_out)):
                pass
                self._io.write_f8be(self.tan_out[i])



        def _check(self):
            if len(self.value) != self.num_value:
                raise kaitaistruct.ConsistencyError(u"value", self.num_value, len(self.value))
            for i in range(len(self.value)):
                pass

            if len(self.tan_in) != self.num_value:
                raise kaitaistruct.ConsistencyError(u"tan_in", self.num_value, len(self.tan_in))
            for i in range(len(self.tan_in)):
                pass

            if len(self.tan_out) != self.num_value:
                raise kaitaistruct.ConsistencyError(u"tan_out", self.num_value, len(self.tan_out))
            for i in range(len(self.tan_out)):
                pass

            self._dirty = False


    class KfUnknownData(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.KfUnknownData, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.contents = self._io.read_bytes_full()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.KfUnknownData, self)._write__seq(io)
            self._io.write_bytes(self.contents)
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"contents", 0, self._io.size() - self._io.pos())


        def _check(self):
            self._dirty = False


    class LdatBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.LdatBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.items = self._io.read_bytes_full()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.LdatBody, self)._write__seq(io)
            self._io.write_bytes(self.items)
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"items", 0, self._io.size() - self._io.pos())


        def _check(self):
            self._dirty = False


    class LdatItem(ReadWriteKaitaiStruct):
        def __init__(self, item_type, _io=None, _parent=None, _root=None):
            super(Aep.LdatItem, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.item_type = item_type

        def _read(self):
            self._unnamed0 = self._io.read_bytes(1)
            self.time_raw = self._io.read_u2be()
            self._unnamed2 = self._io.read_bytes(2)
            self.keyframe_interpolation_type = self._io.read_u1()
            self.label = KaitaiStream.resolve_enum(Aep.Label, self._io.read_u1())
            self._unnamed5 = self._io.read_bits_int_be(2)
            self.roving_across_time = self._io.read_bits_int_be(1) != 0
            self.auto_bezier = self._io.read_bits_int_be(1) != 0
            self.continuous_bezier = self._io.read_bits_int_be(1) != 0
            self._unnamed9 = self._io.read_bits_int_be(3)
            _on = self.item_type
            if _on == Aep.LdatItemType.color:
                pass
                self.kf_data = Aep.KfColor(self._io, self, self._root)
                self.kf_data._read()
            elif _on == Aep.LdatItemType.gide:
                pass
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
                self.kf_data._read()
            elif _on == Aep.LdatItemType.litm:
                pass
                self.kf_data = Aep.OutputModuleSettingsLdatBody(self._io, self, self._root)
                self.kf_data._read()
            elif _on == Aep.LdatItemType.lrdr:
                pass
                self.kf_data = Aep.RenderSettingsLdatBody(self._io, self, self._root)
                self.kf_data._read()
            elif _on == Aep.LdatItemType.marker:
                pass
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
                self.kf_data._read()
            elif _on == Aep.LdatItemType.no_value:
                pass
                self.kf_data = Aep.KfNoValue(self._io, self, self._root)
                self.kf_data._read()
            elif _on == Aep.LdatItemType.one_d:
                pass
                self.kf_data = Aep.KfMultiDimensional(1, self._io, self, self._root)
                self.kf_data._read()
            elif _on == Aep.LdatItemType.orientation:
                pass
                self.kf_data = Aep.KfMultiDimensional(1, self._io, self, self._root)
                self.kf_data._read()
            elif _on == Aep.LdatItemType.three_d:
                pass
                self.kf_data = Aep.KfMultiDimensional(3, self._io, self, self._root)
                self.kf_data._read()
            elif _on == Aep.LdatItemType.three_d_spatial:
                pass
                self.kf_data = Aep.KfPosition(3, self._io, self, self._root)
                self.kf_data._read()
            elif _on == Aep.LdatItemType.two_d:
                pass
                self.kf_data = Aep.KfMultiDimensional(2, self._io, self, self._root)
                self.kf_data._read()
            elif _on == Aep.LdatItemType.two_d_spatial:
                pass
                self.kf_data = Aep.KfPosition(2, self._io, self, self._root)
                self.kf_data._read()
            elif _on == Aep.LdatItemType.unknown:
                pass
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
                self.kf_data._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            _on = self.item_type
            if _on == Aep.LdatItemType.color:
                pass
                self.kf_data._fetch_instances()
            elif _on == Aep.LdatItemType.gide:
                pass
                self.kf_data._fetch_instances()
            elif _on == Aep.LdatItemType.litm:
                pass
                self.kf_data._fetch_instances()
            elif _on == Aep.LdatItemType.lrdr:
                pass
                self.kf_data._fetch_instances()
            elif _on == Aep.LdatItemType.marker:
                pass
                self.kf_data._fetch_instances()
            elif _on == Aep.LdatItemType.no_value:
                pass
                self.kf_data._fetch_instances()
            elif _on == Aep.LdatItemType.one_d:
                pass
                self.kf_data._fetch_instances()
            elif _on == Aep.LdatItemType.orientation:
                pass
                self.kf_data._fetch_instances()
            elif _on == Aep.LdatItemType.three_d:
                pass
                self.kf_data._fetch_instances()
            elif _on == Aep.LdatItemType.three_d_spatial:
                pass
                self.kf_data._fetch_instances()
            elif _on == Aep.LdatItemType.two_d:
                pass
                self.kf_data._fetch_instances()
            elif _on == Aep.LdatItemType.two_d_spatial:
                pass
                self.kf_data._fetch_instances()
            elif _on == Aep.LdatItemType.unknown:
                pass
                self.kf_data._fetch_instances()


        def _write__seq(self, io=None):
            super(Aep.LdatItem, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)
            self._io.write_u2be(self.time_raw)
            self._io.write_bytes(self._unnamed2)
            self._io.write_u1(self.keyframe_interpolation_type)
            self._io.write_u1(int(self.label))
            self._io.write_bits_int_be(2, self._unnamed5)
            self._io.write_bits_int_be(1, int(self.roving_across_time))
            self._io.write_bits_int_be(1, int(self.auto_bezier))
            self._io.write_bits_int_be(1, int(self.continuous_bezier))
            self._io.write_bits_int_be(3, self._unnamed9)
            _on = self.item_type
            if _on == Aep.LdatItemType.color:
                pass
                self.kf_data._write__seq(self._io)
            elif _on == Aep.LdatItemType.gide:
                pass
                self.kf_data._write__seq(self._io)
            elif _on == Aep.LdatItemType.litm:
                pass
                self.kf_data._write__seq(self._io)
            elif _on == Aep.LdatItemType.lrdr:
                pass
                self.kf_data._write__seq(self._io)
            elif _on == Aep.LdatItemType.marker:
                pass
                self.kf_data._write__seq(self._io)
            elif _on == Aep.LdatItemType.no_value:
                pass
                self.kf_data._write__seq(self._io)
            elif _on == Aep.LdatItemType.one_d:
                pass
                self.kf_data._write__seq(self._io)
            elif _on == Aep.LdatItemType.orientation:
                pass
                self.kf_data._write__seq(self._io)
            elif _on == Aep.LdatItemType.three_d:
                pass
                self.kf_data._write__seq(self._io)
            elif _on == Aep.LdatItemType.three_d_spatial:
                pass
                self.kf_data._write__seq(self._io)
            elif _on == Aep.LdatItemType.two_d:
                pass
                self.kf_data._write__seq(self._io)
            elif _on == Aep.LdatItemType.two_d_spatial:
                pass
                self.kf_data._write__seq(self._io)
            elif _on == Aep.LdatItemType.unknown:
                pass
                self.kf_data._write__seq(self._io)


        def _check(self):
            if len(self._unnamed0) != 1:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 1, len(self._unnamed0))
            if len(self._unnamed2) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed2", 2, len(self._unnamed2))
            _on = self.item_type
            if _on == Aep.LdatItemType.color:
                pass
                if self.kf_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self._root, self.kf_data._root)
                if self.kf_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self, self.kf_data._parent)
            elif _on == Aep.LdatItemType.gide:
                pass
                if self.kf_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self._root, self.kf_data._root)
                if self.kf_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self, self.kf_data._parent)
            elif _on == Aep.LdatItemType.litm:
                pass
                if self.kf_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self._root, self.kf_data._root)
                if self.kf_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self, self.kf_data._parent)
            elif _on == Aep.LdatItemType.lrdr:
                pass
                if self.kf_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self._root, self.kf_data._root)
                if self.kf_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self, self.kf_data._parent)
            elif _on == Aep.LdatItemType.marker:
                pass
                if self.kf_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self._root, self.kf_data._root)
                if self.kf_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self, self.kf_data._parent)
            elif _on == Aep.LdatItemType.no_value:
                pass
                if self.kf_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self._root, self.kf_data._root)
                if self.kf_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self, self.kf_data._parent)
            elif _on == Aep.LdatItemType.one_d:
                pass
                if self.kf_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self._root, self.kf_data._root)
                if self.kf_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self, self.kf_data._parent)
                if self.kf_data.num_value != 1:
                    raise kaitaistruct.ConsistencyError(u"kf_data", 1, self.kf_data.num_value)
            elif _on == Aep.LdatItemType.orientation:
                pass
                if self.kf_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self._root, self.kf_data._root)
                if self.kf_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self, self.kf_data._parent)
                if self.kf_data.num_value != 1:
                    raise kaitaistruct.ConsistencyError(u"kf_data", 1, self.kf_data.num_value)
            elif _on == Aep.LdatItemType.three_d:
                pass
                if self.kf_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self._root, self.kf_data._root)
                if self.kf_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self, self.kf_data._parent)
                if self.kf_data.num_value != 3:
                    raise kaitaistruct.ConsistencyError(u"kf_data", 3, self.kf_data.num_value)
            elif _on == Aep.LdatItemType.three_d_spatial:
                pass
                if self.kf_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self._root, self.kf_data._root)
                if self.kf_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self, self.kf_data._parent)
                if self.kf_data.num_value != 3:
                    raise kaitaistruct.ConsistencyError(u"kf_data", 3, self.kf_data.num_value)
            elif _on == Aep.LdatItemType.two_d:
                pass
                if self.kf_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self._root, self.kf_data._root)
                if self.kf_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self, self.kf_data._parent)
                if self.kf_data.num_value != 2:
                    raise kaitaistruct.ConsistencyError(u"kf_data", 2, self.kf_data.num_value)
            elif _on == Aep.LdatItemType.two_d_spatial:
                pass
                if self.kf_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self._root, self.kf_data._root)
                if self.kf_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self, self.kf_data._parent)
                if self.kf_data.num_value != 2:
                    raise kaitaistruct.ConsistencyError(u"kf_data", 2, self.kf_data.num_value)
            elif _on == Aep.LdatItemType.unknown:
                pass
                if self.kf_data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self._root, self.kf_data._root)
                if self.kf_data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"kf_data", self, self.kf_data._parent)
            self._dirty = False


    class LdtaBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.LdtaBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.layer_id = self._io.read_u4be()
            self.quality = self._io.read_u2be()
            self._unnamed2 = self._io.read_bytes(4)
            self.stretch_dividend = self._io.read_s2be()
            self.start_time_dividend = self._io.read_s4be()
            self.start_time_divisor = self._io.read_u4be()
            self.in_point_dividend = self._io.read_s4be()
            self.in_point_divisor = self._io.read_u4be()
            self.out_point_dividend = self._io.read_s4be()
            self.out_point_divisor = self._io.read_u4be()
            self._unnamed10 = self._io.read_bytes(1)
            self._unnamed11 = self._io.read_bits_int_be(1) != 0
            self.sampling_quality = self._io.read_bits_int_be(1) != 0
            self.environment_layer = self._io.read_bits_int_be(1) != 0
            self.characters_toward_camera = self._io.read_bits_int_be(2)
            self.frame_blending_type = self._io.read_bits_int_be(1) != 0
            self.guide_layer = self._io.read_bits_int_be(1) != 0
            self._unnamed17 = self._io.read_bits_int_be(1) != 0
            self.null_layer = self._io.read_bits_int_be(1) != 0
            self._unnamed19 = self._io.read_bits_int_be(1) != 0
            self.camera_or_poi_auto_orient = self._io.read_bits_int_be(1) != 0
            self.markers_locked = self._io.read_bits_int_be(1) != 0
            self.solo = self._io.read_bits_int_be(1) != 0
            self.three_d_layer = self._io.read_bits_int_be(1) != 0
            self.adjustment_layer = self._io.read_bits_int_be(1) != 0
            self.auto_orient_along_path = self._io.read_bits_int_be(1) != 0
            self.collapse_transformation = self._io.read_bits_int_be(1) != 0
            self.shy = self._io.read_bits_int_be(1) != 0
            self.locked = self._io.read_bits_int_be(1) != 0
            self.frame_blending = self._io.read_bits_int_be(1) != 0
            self.motion_blur = self._io.read_bits_int_be(1) != 0
            self.effects_active = self._io.read_bits_int_be(1) != 0
            self.audio_enabled = self._io.read_bits_int_be(1) != 0
            self.enabled = self._io.read_bits_int_be(1) != 0
            self.source_id = self._io.read_u4be()
            self._unnamed35 = self._io.read_bytes(17)
            self.label = KaitaiStream.resolve_enum(Aep.Label, self._io.read_u1())
            self._unnamed37 = self._io.read_bytes(2)
            self.layer_name = (self._io.read_bytes(32)).decode(u"windows-1250")
            self._unnamed39 = self._io.read_bytes(3)
            self.blending_mode = self._io.read_u1()
            self._unnamed41 = self._io.read_bytes(3)
            self.preserve_transparency = self._io.read_u1()
            self._unnamed43 = self._io.read_bytes(3)
            self.track_matte_type = self._io.read_u1()
            self._unnamed45 = self._io.read_bytes(2)
            self.stretch_divisor = self._io.read_u2be()
            self._unnamed47 = self._io.read_bytes(19)
            self.layer_type = KaitaiStream.resolve_enum(Aep.LayerType, self._io.read_u1())
            self.parent_id = self._io.read_u4be()
            self._unnamed50 = self._io.read_bytes(3)
            self.light_type = self._io.read_u1()
            self._unnamed52 = self._io.read_bytes(20)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.LdtaBody, self)._write__seq(io)
            self._io.write_u4be(self.layer_id)
            self._io.write_u2be(self.quality)
            self._io.write_bytes(self._unnamed2)
            self._io.write_s2be(self.stretch_dividend)
            self._io.write_s4be(self.start_time_dividend)
            self._io.write_u4be(self.start_time_divisor)
            self._io.write_s4be(self.in_point_dividend)
            self._io.write_u4be(self.in_point_divisor)
            self._io.write_s4be(self.out_point_dividend)
            self._io.write_u4be(self.out_point_divisor)
            self._io.write_bytes(self._unnamed10)
            self._io.write_bits_int_be(1, int(self._unnamed11))
            self._io.write_bits_int_be(1, int(self.sampling_quality))
            self._io.write_bits_int_be(1, int(self.environment_layer))
            self._io.write_bits_int_be(2, self.characters_toward_camera)
            self._io.write_bits_int_be(1, int(self.frame_blending_type))
            self._io.write_bits_int_be(1, int(self.guide_layer))
            self._io.write_bits_int_be(1, int(self._unnamed17))
            self._io.write_bits_int_be(1, int(self.null_layer))
            self._io.write_bits_int_be(1, int(self._unnamed19))
            self._io.write_bits_int_be(1, int(self.camera_or_poi_auto_orient))
            self._io.write_bits_int_be(1, int(self.markers_locked))
            self._io.write_bits_int_be(1, int(self.solo))
            self._io.write_bits_int_be(1, int(self.three_d_layer))
            self._io.write_bits_int_be(1, int(self.adjustment_layer))
            self._io.write_bits_int_be(1, int(self.auto_orient_along_path))
            self._io.write_bits_int_be(1, int(self.collapse_transformation))
            self._io.write_bits_int_be(1, int(self.shy))
            self._io.write_bits_int_be(1, int(self.locked))
            self._io.write_bits_int_be(1, int(self.frame_blending))
            self._io.write_bits_int_be(1, int(self.motion_blur))
            self._io.write_bits_int_be(1, int(self.effects_active))
            self._io.write_bits_int_be(1, int(self.audio_enabled))
            self._io.write_bits_int_be(1, int(self.enabled))
            self._io.write_u4be(self.source_id)
            self._io.write_bytes(self._unnamed35)
            self._io.write_u1(int(self.label))
            self._io.write_bytes(self._unnamed37)
            self._io.write_bytes((self.layer_name).encode(u"windows-1250"))
            self._io.write_bytes(self._unnamed39)
            self._io.write_u1(self.blending_mode)
            self._io.write_bytes(self._unnamed41)
            self._io.write_u1(self.preserve_transparency)
            self._io.write_bytes(self._unnamed43)
            self._io.write_u1(self.track_matte_type)
            self._io.write_bytes(self._unnamed45)
            self._io.write_u2be(self.stretch_divisor)
            self._io.write_bytes(self._unnamed47)
            self._io.write_u1(int(self.layer_type))
            self._io.write_u4be(self.parent_id)
            self._io.write_bytes(self._unnamed50)
            self._io.write_u1(self.light_type)
            self._io.write_bytes(self._unnamed52)


        def _check(self):
            if len(self._unnamed2) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed2", 4, len(self._unnamed2))
            if len(self._unnamed10) != 1:
                raise kaitaistruct.ConsistencyError(u"_unnamed10", 1, len(self._unnamed10))
            if len(self._unnamed35) != 17:
                raise kaitaistruct.ConsistencyError(u"_unnamed35", 17, len(self._unnamed35))
            if len(self._unnamed37) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed37", 2, len(self._unnamed37))
            if len((self.layer_name).encode(u"windows-1250")) != 32:
                raise kaitaistruct.ConsistencyError(u"layer_name", 32, len((self.layer_name).encode(u"windows-1250")))
            if len(self._unnamed39) != 3:
                raise kaitaistruct.ConsistencyError(u"_unnamed39", 3, len(self._unnamed39))
            if len(self._unnamed41) != 3:
                raise kaitaistruct.ConsistencyError(u"_unnamed41", 3, len(self._unnamed41))
            if len(self._unnamed43) != 3:
                raise kaitaistruct.ConsistencyError(u"_unnamed43", 3, len(self._unnamed43))
            if len(self._unnamed45) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed45", 2, len(self._unnamed45))
            if len(self._unnamed47) != 19:
                raise kaitaistruct.ConsistencyError(u"_unnamed47", 19, len(self._unnamed47))
            if len(self._unnamed50) != 3:
                raise kaitaistruct.ConsistencyError(u"_unnamed50", 3, len(self._unnamed50))
            if len(self._unnamed52) != 20:
                raise kaitaistruct.ConsistencyError(u"_unnamed52", 20, len(self._unnamed52))
            self._dirty = False

        @property
        def in_point(self):
            if hasattr(self, '_m_in_point'):
                return self._m_in_point

            self._m_in_point = self.in_point_dividend / self.in_point_divisor
            return getattr(self, '_m_in_point', None)

        def _invalidate_in_point(self):
            del self._m_in_point
        @property
        def out_point(self):
            if hasattr(self, '_m_out_point'):
                return self._m_out_point

            self._m_out_point = self.out_point_dividend / self.out_point_divisor
            return getattr(self, '_m_out_point', None)

        def _invalidate_out_point(self):
            del self._m_out_point
        @property
        def start_time(self):
            if hasattr(self, '_m_start_time'):
                return self._m_start_time

            self._m_start_time = self.start_time_dividend / self.start_time_divisor
            return getattr(self, '_m_start_time', None)

        def _invalidate_start_time(self):
            del self._m_start_time

    class Lhd3Body(ReadWriteKaitaiStruct):
        """Header for item/keyframe lists. AE reuses this structure for:
        - Property keyframes (count = keyframe count, item_size = keyframe data size)
        - Render queue items (count = item count, item_size = 2246 for settings)
        - Output module items (count = item count, item_size = 128 for settings)
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.Lhd3Body, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bytes(10)
            self.count = self._io.read_u2be()
            self._unnamed2 = self._io.read_bytes(6)
            self.item_size = self._io.read_u2be()
            self._unnamed4 = self._io.read_bytes(3)
            self.item_type_raw = self._io.read_u1()
            self._unnamed6 = self._io.read_bytes_full()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.Lhd3Body, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)
            self._io.write_u2be(self.count)
            self._io.write_bytes(self._unnamed2)
            self._io.write_u2be(self.item_size)
            self._io.write_bytes(self._unnamed4)
            self._io.write_u1(self.item_type_raw)
            self._io.write_bytes(self._unnamed6)
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"_unnamed6", 0, self._io.size() - self._io.pos())


        def _check(self):
            if len(self._unnamed0) != 10:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 10, len(self._unnamed0))
            if len(self._unnamed2) != 6:
                raise kaitaistruct.ConsistencyError(u"_unnamed2", 6, len(self._unnamed2))
            if len(self._unnamed4) != 3:
                raise kaitaistruct.ConsistencyError(u"_unnamed4", 3, len(self._unnamed4))
            self._dirty = False

        @property
        def item_type(self):
            if hasattr(self, '_m_item_type'):
                return self._m_item_type

            self._m_item_type = (Aep.LdatItemType.lrdr if  ((self.item_type_raw == 1) and (self.item_size == 2246))  else (Aep.LdatItemType.litm if  ((self.item_type_raw == 1) and (self.item_size == 128))  else (Aep.LdatItemType.gide if  ((self.item_type_raw == 2) and (self.item_size == 1))  else (Aep.LdatItemType.color if  ((self.item_type_raw == 4) and (self.item_size == 152))  else (Aep.LdatItemType.three_d if  ((self.item_type_raw == 4) and (self.item_size == 128))  else (Aep.LdatItemType.two_d_spatial if  ((self.item_type_raw == 4) and (self.item_size == 104))  else (Aep.LdatItemType.two_d if  ((self.item_type_raw == 4) and (self.item_size == 88))  else (Aep.LdatItemType.orientation if  ((self.item_type_raw == 4) and (self.item_size == 80))  else (Aep.LdatItemType.no_value if  ((self.item_type_raw == 4) and (self.item_size == 64))  else (Aep.LdatItemType.one_d if  ((self.item_type_raw == 4) and (self.item_size == 48))  else (Aep.LdatItemType.marker if  ((self.item_type_raw == 4) and (self.item_size == 16))  else Aep.LdatItemType.unknown)))))))))))
            return getattr(self, '_m_item_type', None)

        def _invalidate_item_type(self):
            del self._m_item_type

    class ListBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.ListBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.list_type = (self._io.read_bytes(4)).decode(u"windows-1250")
            if self.list_type != u"btdk":
                pass
                self.chunks = []
                i = 0
                while not self._io.is_eof():
                    _t_chunks = Aep.Chunk(self._io, self, self._root)
                    try:
                        _t_chunks._read()
                    finally:
                        self.chunks.append(_t_chunks)
                    i += 1


            if self.list_type == u"btdk":
                pass
                self.binary_data = self._io.read_bytes_full()

            self._dirty = False


        def _fetch_instances(self):
            pass
            if self.list_type != u"btdk":
                pass
                for i in range(len(self.chunks)):
                    pass
                    self.chunks[i]._fetch_instances()


            if self.list_type == u"btdk":
                pass



        def _write__seq(self, io=None):
            super(Aep.ListBody, self)._write__seq(io)
            self._io.write_bytes((self.list_type).encode(u"windows-1250"))
            if self.list_type != u"btdk":
                pass
                for i in range(len(self.chunks)):
                    pass
                    if self._io.is_eof():
                        raise kaitaistruct.ConsistencyError(u"chunks", 0, self._io.size() - self._io.pos())
                    self.chunks[i]._write__seq(self._io)

                if not self._io.is_eof():
                    raise kaitaistruct.ConsistencyError(u"chunks", 0, self._io.size() - self._io.pos())

            if self.list_type == u"btdk":
                pass
                self._io.write_bytes(self.binary_data)
                if not self._io.is_eof():
                    raise kaitaistruct.ConsistencyError(u"binary_data", 0, self._io.size() - self._io.pos())



        def _check(self):
            if len((self.list_type).encode(u"windows-1250")) != 4:
                raise kaitaistruct.ConsistencyError(u"list_type", 4, len((self.list_type).encode(u"windows-1250")))
            if self.list_type != u"btdk":
                pass
                for i in range(len(self.chunks)):
                    pass
                    if self.chunks[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"chunks", self._root, self.chunks[i]._root)
                    if self.chunks[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"chunks", self, self.chunks[i]._parent)


            if self.list_type == u"btdk":
                pass

            self._dirty = False


    class NmhdBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.NmhdBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bytes(3)
            self._unnamed1 = self._io.read_bits_int_be(5)
            self.unknown = self._io.read_bits_int_be(1) != 0
            self.protected_region = self._io.read_bits_int_be(1) != 0
            self.navigation = self._io.read_bits_int_be(1) != 0
            self._unnamed5 = self._io.read_bytes(4)
            self.frame_duration = self._io.read_u4be()
            self._unnamed7 = self._io.read_bytes(4)
            self.label = KaitaiStream.resolve_enum(Aep.Label, self._io.read_u1())
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.NmhdBody, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)
            self._io.write_bits_int_be(5, self._unnamed1)
            self._io.write_bits_int_be(1, int(self.unknown))
            self._io.write_bits_int_be(1, int(self.protected_region))
            self._io.write_bits_int_be(1, int(self.navigation))
            self._io.write_bytes(self._unnamed5)
            self._io.write_u4be(self.frame_duration)
            self._io.write_bytes(self._unnamed7)
            self._io.write_u1(int(self.label))


        def _check(self):
            if len(self._unnamed0) != 3:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 3, len(self._unnamed0))
            if len(self._unnamed5) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed5", 4, len(self._unnamed5))
            if len(self._unnamed7) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed7", 4, len(self._unnamed7))
            self._dirty = False


    class NnhdBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.NnhdBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bytes(8)
            self.time_display_type = self._io.read_bits_int_be(7)
            self.feet_frames_film_type = self._io.read_bits_int_be(1) != 0
            self.footage_timecode_display_start_type = self._io.read_u1()
            self._unnamed4 = self._io.read_bytes(1)
            self._unnamed5 = self._io.read_bits_int_be(7)
            self.frames_use_feet_frames = self._io.read_bits_int_be(1) != 0
            self._unnamed7 = self._io.read_bytes(2)
            self.frame_rate = self._io.read_u2be()
            self._unnamed9 = self._io.read_bytes(4)
            self.frames_count_type = self._io.read_u1()
            self._unnamed11 = self._io.read_bytes(3)
            self.bits_per_channel = self._io.read_u1()
            self._unnamed13 = self._io.read_bytes(6)
            self._unnamed14 = self._io.read_bits_int_be(2)
            self.linearize_working_space = self._io.read_bits_int_be(1) != 0
            self._unnamed16 = self._io.read_bits_int_be(5)
            self._unnamed17 = self._io.read_bytes(8)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.NnhdBody, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)
            self._io.write_bits_int_be(7, self.time_display_type)
            self._io.write_bits_int_be(1, int(self.feet_frames_film_type))
            self._io.write_u1(self.footage_timecode_display_start_type)
            self._io.write_bytes(self._unnamed4)
            self._io.write_bits_int_be(7, self._unnamed5)
            self._io.write_bits_int_be(1, int(self.frames_use_feet_frames))
            self._io.write_bytes(self._unnamed7)
            self._io.write_u2be(self.frame_rate)
            self._io.write_bytes(self._unnamed9)
            self._io.write_u1(self.frames_count_type)
            self._io.write_bytes(self._unnamed11)
            self._io.write_u1(self.bits_per_channel)
            self._io.write_bytes(self._unnamed13)
            self._io.write_bits_int_be(2, self._unnamed14)
            self._io.write_bits_int_be(1, int(self.linearize_working_space))
            self._io.write_bits_int_be(5, self._unnamed16)
            self._io.write_bytes(self._unnamed17)


        def _check(self):
            if len(self._unnamed0) != 8:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 8, len(self._unnamed0))
            if len(self._unnamed4) != 1:
                raise kaitaistruct.ConsistencyError(u"_unnamed4", 1, len(self._unnamed4))
            if len(self._unnamed7) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed7", 2, len(self._unnamed7))
            if len(self._unnamed9) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed9", 4, len(self._unnamed9))
            if len(self._unnamed11) != 3:
                raise kaitaistruct.ConsistencyError(u"_unnamed11", 3, len(self._unnamed11))
            if len(self._unnamed13) != 6:
                raise kaitaistruct.ConsistencyError(u"_unnamed13", 6, len(self._unnamed13))
            if len(self._unnamed17) != 8:
                raise kaitaistruct.ConsistencyError(u"_unnamed17", 8, len(self._unnamed17))
            self._dirty = False


    class OptiBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.OptiBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.asset_type = (KaitaiStream.bytes_terminate(self._io.read_bytes(4), 0, False)).decode(u"ASCII")
            self.asset_type_int = self._io.read_u2be()
            if self.asset_type == u"Soli":
                pass
                self._unnamed2 = self._io.read_bytes(4)

            if self.asset_type == u"Soli":
                pass
                self.color = []
                for i in range(4):
                    self.color.append(self._io.read_f4be())


            if self.asset_type == u"Soli":
                pass
                self.solid_name = (KaitaiStream.bytes_terminate(self._io.read_bytes(256), 0, False)).decode(u"windows-1250")

            if self.asset_type == u"Soli":
                pass
                self.solid_remaining = self._io.read_bytes_full()

            if self.asset_type_int == 2:
                pass
                self._unnamed6 = self._io.read_bytes(4)

            if self.asset_type_int == 2:
                pass
                self.placeholder_name = (KaitaiStream.bytes_terminate(self._io.read_bytes_full(), 0, False)).decode(u"windows-1250")

            if  ((self.asset_type != u"Soli") and (self.asset_type_int != 2)) :
                pass
                self.file_remaining = self._io.read_bytes_full()

            self._dirty = False


        def _fetch_instances(self):
            pass
            if self.asset_type == u"Soli":
                pass

            if self.asset_type == u"Soli":
                pass
                for i in range(len(self.color)):
                    pass


            if self.asset_type == u"Soli":
                pass

            if self.asset_type == u"Soli":
                pass

            if self.asset_type_int == 2:
                pass

            if self.asset_type_int == 2:
                pass

            if  ((self.asset_type != u"Soli") and (self.asset_type_int != 2)) :
                pass



        def _write__seq(self, io=None):
            super(Aep.OptiBody, self)._write__seq(io)
            self._io.write_bytes_limit((self.asset_type).encode(u"ASCII"), 4, 0, 0)
            self._io.write_u2be(self.asset_type_int)
            if self.asset_type == u"Soli":
                pass
                self._io.write_bytes(self._unnamed2)

            if self.asset_type == u"Soli":
                pass
                for i in range(len(self.color)):
                    pass
                    self._io.write_f4be(self.color[i])


            if self.asset_type == u"Soli":
                pass
                self._io.write_bytes_limit((self.solid_name).encode(u"windows-1250"), 256, 0, 0)

            if self.asset_type == u"Soli":
                pass
                self._io.write_bytes(self.solid_remaining)
                if not self._io.is_eof():
                    raise kaitaistruct.ConsistencyError(u"solid_remaining", 0, self._io.size() - self._io.pos())

            if self.asset_type_int == 2:
                pass
                self._io.write_bytes(self._unnamed6)

            if self.asset_type_int == 2:
                pass
                self._io.write_bytes_limit((self.placeholder_name).encode(u"windows-1250"), self._io.size() - self._io.pos(), 0, 0)
                if not self._io.is_eof():
                    raise kaitaistruct.ConsistencyError(u"placeholder_name", 0, self._io.size() - self._io.pos())

            if  ((self.asset_type != u"Soli") and (self.asset_type_int != 2)) :
                pass
                self._io.write_bytes(self.file_remaining)
                if not self._io.is_eof():
                    raise kaitaistruct.ConsistencyError(u"file_remaining", 0, self._io.size() - self._io.pos())



        def _check(self):
            if len((self.asset_type).encode(u"ASCII")) > 4:
                raise kaitaistruct.ConsistencyError(u"asset_type", 4, len((self.asset_type).encode(u"ASCII")))
            if KaitaiStream.byte_array_index_of((self.asset_type).encode(u"ASCII"), 0) != -1:
                raise kaitaistruct.ConsistencyError(u"asset_type", -1, KaitaiStream.byte_array_index_of((self.asset_type).encode(u"ASCII"), 0))
            if self.asset_type == u"Soli":
                pass
                if len(self._unnamed2) != 4:
                    raise kaitaistruct.ConsistencyError(u"_unnamed2", 4, len(self._unnamed2))

            if self.asset_type == u"Soli":
                pass
                if len(self.color) != 4:
                    raise kaitaistruct.ConsistencyError(u"color", 4, len(self.color))
                for i in range(len(self.color)):
                    pass


            if self.asset_type == u"Soli":
                pass
                if len((self.solid_name).encode(u"windows-1250")) > 256:
                    raise kaitaistruct.ConsistencyError(u"solid_name", 256, len((self.solid_name).encode(u"windows-1250")))
                if KaitaiStream.byte_array_index_of((self.solid_name).encode(u"windows-1250"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"solid_name", -1, KaitaiStream.byte_array_index_of((self.solid_name).encode(u"windows-1250"), 0))

            if self.asset_type == u"Soli":
                pass

            if self.asset_type_int == 2:
                pass
                if len(self._unnamed6) != 4:
                    raise kaitaistruct.ConsistencyError(u"_unnamed6", 4, len(self._unnamed6))

            if self.asset_type_int == 2:
                pass

            if  ((self.asset_type != u"Soli") and (self.asset_type_int != 2)) :
                pass

            self._dirty = False

        @property
        def alpha(self):
            if hasattr(self, '_m_alpha'):
                return self._m_alpha

            if self.asset_type == u"Soli":
                pass
                self._m_alpha = self.color[0]

            return getattr(self, '_m_alpha', None)

        def _invalidate_alpha(self):
            del self._m_alpha
        @property
        def blue(self):
            if hasattr(self, '_m_blue'):
                return self._m_blue

            if self.asset_type == u"Soli":
                pass
                self._m_blue = self.color[3]

            return getattr(self, '_m_blue', None)

        def _invalidate_blue(self):
            del self._m_blue
        @property
        def green(self):
            if hasattr(self, '_m_green'):
                return self._m_green

            if self.asset_type == u"Soli":
                pass
                self._m_green = self.color[2]

            return getattr(self, '_m_green', None)

        def _invalidate_green(self):
            del self._m_green
        @property
        def red(self):
            if hasattr(self, '_m_red'):
                return self._m_red

            if self.asset_type == u"Soli":
                pass
                self._m_red = self.color[1]

            return getattr(self, '_m_red', None)

        def _invalidate_red(self):
            del self._m_red

    class OutputModuleSettingsLdatBody(ReadWriteKaitaiStruct):
        """Per-output-module settings chunk (128 bytes).
        Used under LIST:list within LIST:LItm for each render queue item.
        Note: The actual comp_id is stored in render_settings_ldat_body, not here.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.OutputModuleSettingsLdatBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bytes(7)
            self._unnamed1 = self._io.read_bits_int_be(1) != 0
            self.include_source_xmp = self._io.read_bits_int_be(1) != 0
            self._unnamed3 = self._io.read_bits_int_be(6)
            self.post_render_target_comp_id = self._io.read_u4be()
            self._unnamed5 = self._io.read_bytes(4)
            self._unnamed6 = self._io.read_bytes(15)
            self._unnamed7 = self._io.read_bits_int_be(7)
            self.crop = self._io.read_bits_int_be(1) != 0
            self.crop_top = self._io.read_u2be()
            self.crop_left = self._io.read_u2be()
            self.crop_bottom = self._io.read_u2be()
            self.crop_right = self._io.read_u2be()
            self._unnamed13 = self._io.read_bytes(8)
            self.post_render_action = self._io.read_u4be()
            self.post_render_use_comp = self._io.read_u4be()
            self.remaining = self._io.read_bytes(72)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.OutputModuleSettingsLdatBody, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)
            self._io.write_bits_int_be(1, int(self._unnamed1))
            self._io.write_bits_int_be(1, int(self.include_source_xmp))
            self._io.write_bits_int_be(6, self._unnamed3)
            self._io.write_u4be(self.post_render_target_comp_id)
            self._io.write_bytes(self._unnamed5)
            self._io.write_bytes(self._unnamed6)
            self._io.write_bits_int_be(7, self._unnamed7)
            self._io.write_bits_int_be(1, int(self.crop))
            self._io.write_u2be(self.crop_top)
            self._io.write_u2be(self.crop_left)
            self._io.write_u2be(self.crop_bottom)
            self._io.write_u2be(self.crop_right)
            self._io.write_bytes(self._unnamed13)
            self._io.write_u4be(self.post_render_action)
            self._io.write_u4be(self.post_render_use_comp)
            self._io.write_bytes(self.remaining)


        def _check(self):
            if len(self._unnamed0) != 7:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 7, len(self._unnamed0))
            if len(self._unnamed5) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed5", 4, len(self._unnamed5))
            if len(self._unnamed6) != 15:
                raise kaitaistruct.ConsistencyError(u"_unnamed6", 15, len(self._unnamed6))
            if len(self._unnamed13) != 8:
                raise kaitaistruct.ConsistencyError(u"_unnamed13", 8, len(self._unnamed13))
            if len(self.remaining) != 72:
                raise kaitaistruct.ConsistencyError(u"remaining", 72, len(self.remaining))
            self._dirty = False


    class PardBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.PardBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bytes(15)
            self.property_control_type = KaitaiStream.resolve_enum(Aep.PropertyControlType, self._io.read_u1())
            self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(32), 0, False)).decode(u"windows-1250")
            self._unnamed3 = self._io.read_bytes(8)
            if self.property_control_type == Aep.PropertyControlType.color:
                pass
                self.last_color = []
                for i in range(4):
                    self.last_color.append(self._io.read_u1())


            if self.property_control_type == Aep.PropertyControlType.color:
                pass
                self.default_color = []
                for i in range(4):
                    self.default_color.append(self._io.read_u1())


            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.angle) or (self.property_control_type == Aep.PropertyControlType.boolean) or (self.property_control_type == Aep.PropertyControlType.enum) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.angle:
                    pass
                    self.last_value = self._io.read_s4be()
                elif _on == Aep.PropertyControlType.boolean:
                    pass
                    self.last_value = self._io.read_u4be()
                elif _on == Aep.PropertyControlType.enum:
                    pass
                    self.last_value = self._io.read_u4be()
                elif _on == Aep.PropertyControlType.scalar:
                    pass
                    self.last_value = self._io.read_s4be()
                elif _on == Aep.PropertyControlType.slider:
                    pass
                    self.last_value = self._io.read_f8be()

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.three_d:
                    pass
                    self.last_value_x_raw = self._io.read_f8be()
                elif _on == Aep.PropertyControlType.two_d:
                    pass
                    self.last_value_x_raw = self._io.read_s4be()

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.three_d:
                    pass
                    self.last_value_y_raw = self._io.read_f8be()
                elif _on == Aep.PropertyControlType.two_d:
                    pass
                    self.last_value_y_raw = self._io.read_s4be()

            if self.property_control_type == Aep.PropertyControlType.three_d:
                pass
                self.last_value_z_raw = self._io.read_f8be()

            if self.property_control_type == Aep.PropertyControlType.enum:
                pass
                self.nb_options = self._io.read_s4be()

            if  ((self.property_control_type == Aep.PropertyControlType.boolean) or (self.property_control_type == Aep.PropertyControlType.enum)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.boolean:
                    pass
                    self.default = self._io.read_u1()
                elif _on == Aep.PropertyControlType.enum:
                    pass
                    self.default = self._io.read_s4be()

            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.color) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                pass
                self._unnamed12 = self._io.read_bytes((72 if self.property_control_type == Aep.PropertyControlType.scalar else (64 if self.property_control_type == Aep.PropertyControlType.color else 52)))

            if self.property_control_type == Aep.PropertyControlType.scalar:
                pass
                self.min_value = self._io.read_s2be()

            if self.property_control_type == Aep.PropertyControlType.scalar:
                pass
                self._unnamed14 = self._io.read_bytes(2)

            if self.property_control_type == Aep.PropertyControlType.color:
                pass
                self.max_color = []
                for i in range(4):
                    self.max_color.append(self._io.read_u1())


            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.scalar:
                    pass
                    self.max_value = self._io.read_s2be()
                elif _on == Aep.PropertyControlType.slider:
                    pass
                    self.max_value = self._io.read_f4be()

            self._unnamed17 = self._io.read_bytes_full()
            self._dirty = False


        def _fetch_instances(self):
            pass
            if self.property_control_type == Aep.PropertyControlType.color:
                pass
                for i in range(len(self.last_color)):
                    pass


            if self.property_control_type == Aep.PropertyControlType.color:
                pass
                for i in range(len(self.default_color)):
                    pass


            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.angle) or (self.property_control_type == Aep.PropertyControlType.boolean) or (self.property_control_type == Aep.PropertyControlType.enum) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.angle:
                    pass
                elif _on == Aep.PropertyControlType.boolean:
                    pass
                elif _on == Aep.PropertyControlType.enum:
                    pass
                elif _on == Aep.PropertyControlType.scalar:
                    pass
                elif _on == Aep.PropertyControlType.slider:
                    pass

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.three_d:
                    pass
                elif _on == Aep.PropertyControlType.two_d:
                    pass

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.three_d:
                    pass
                elif _on == Aep.PropertyControlType.two_d:
                    pass

            if self.property_control_type == Aep.PropertyControlType.three_d:
                pass

            if self.property_control_type == Aep.PropertyControlType.enum:
                pass

            if  ((self.property_control_type == Aep.PropertyControlType.boolean) or (self.property_control_type == Aep.PropertyControlType.enum)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.boolean:
                    pass
                elif _on == Aep.PropertyControlType.enum:
                    pass

            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.color) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                pass

            if self.property_control_type == Aep.PropertyControlType.scalar:
                pass

            if self.property_control_type == Aep.PropertyControlType.scalar:
                pass

            if self.property_control_type == Aep.PropertyControlType.color:
                pass
                for i in range(len(self.max_color)):
                    pass


            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.scalar:
                    pass
                elif _on == Aep.PropertyControlType.slider:
                    pass



        def _write__seq(self, io=None):
            super(Aep.PardBody, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)
            self._io.write_u1(int(self.property_control_type))
            self._io.write_bytes_limit((self.name).encode(u"windows-1250"), 32, 0, 0)
            self._io.write_bytes(self._unnamed3)
            if self.property_control_type == Aep.PropertyControlType.color:
                pass
                for i in range(len(self.last_color)):
                    pass
                    self._io.write_u1(self.last_color[i])


            if self.property_control_type == Aep.PropertyControlType.color:
                pass
                for i in range(len(self.default_color)):
                    pass
                    self._io.write_u1(self.default_color[i])


            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.angle) or (self.property_control_type == Aep.PropertyControlType.boolean) or (self.property_control_type == Aep.PropertyControlType.enum) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.angle:
                    pass
                    self._io.write_s4be(self.last_value)
                elif _on == Aep.PropertyControlType.boolean:
                    pass
                    self._io.write_u4be(self.last_value)
                elif _on == Aep.PropertyControlType.enum:
                    pass
                    self._io.write_u4be(self.last_value)
                elif _on == Aep.PropertyControlType.scalar:
                    pass
                    self._io.write_s4be(self.last_value)
                elif _on == Aep.PropertyControlType.slider:
                    pass
                    self._io.write_f8be(self.last_value)

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.three_d:
                    pass
                    self._io.write_f8be(self.last_value_x_raw)
                elif _on == Aep.PropertyControlType.two_d:
                    pass
                    self._io.write_s4be(self.last_value_x_raw)

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.three_d:
                    pass
                    self._io.write_f8be(self.last_value_y_raw)
                elif _on == Aep.PropertyControlType.two_d:
                    pass
                    self._io.write_s4be(self.last_value_y_raw)

            if self.property_control_type == Aep.PropertyControlType.three_d:
                pass
                self._io.write_f8be(self.last_value_z_raw)

            if self.property_control_type == Aep.PropertyControlType.enum:
                pass
                self._io.write_s4be(self.nb_options)

            if  ((self.property_control_type == Aep.PropertyControlType.boolean) or (self.property_control_type == Aep.PropertyControlType.enum)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.boolean:
                    pass
                    self._io.write_u1(self.default)
                elif _on == Aep.PropertyControlType.enum:
                    pass
                    self._io.write_s4be(self.default)

            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.color) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                pass
                self._io.write_bytes(self._unnamed12)

            if self.property_control_type == Aep.PropertyControlType.scalar:
                pass
                self._io.write_s2be(self.min_value)

            if self.property_control_type == Aep.PropertyControlType.scalar:
                pass
                self._io.write_bytes(self._unnamed14)

            if self.property_control_type == Aep.PropertyControlType.color:
                pass
                for i in range(len(self.max_color)):
                    pass
                    self._io.write_u1(self.max_color[i])


            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.scalar:
                    pass
                    self._io.write_s2be(self.max_value)
                elif _on == Aep.PropertyControlType.slider:
                    pass
                    self._io.write_f4be(self.max_value)

            self._io.write_bytes(self._unnamed17)
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"_unnamed17", 0, self._io.size() - self._io.pos())


        def _check(self):
            if len(self._unnamed0) != 15:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 15, len(self._unnamed0))
            if len((self.name).encode(u"windows-1250")) > 32:
                raise kaitaistruct.ConsistencyError(u"name", 32, len((self.name).encode(u"windows-1250")))
            if KaitaiStream.byte_array_index_of((self.name).encode(u"windows-1250"), 0) != -1:
                raise kaitaistruct.ConsistencyError(u"name", -1, KaitaiStream.byte_array_index_of((self.name).encode(u"windows-1250"), 0))
            if len(self._unnamed3) != 8:
                raise kaitaistruct.ConsistencyError(u"_unnamed3", 8, len(self._unnamed3))
            if self.property_control_type == Aep.PropertyControlType.color:
                pass
                if len(self.last_color) != 4:
                    raise kaitaistruct.ConsistencyError(u"last_color", 4, len(self.last_color))
                for i in range(len(self.last_color)):
                    pass


            if self.property_control_type == Aep.PropertyControlType.color:
                pass
                if len(self.default_color) != 4:
                    raise kaitaistruct.ConsistencyError(u"default_color", 4, len(self.default_color))
                for i in range(len(self.default_color)):
                    pass


            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.angle) or (self.property_control_type == Aep.PropertyControlType.boolean) or (self.property_control_type == Aep.PropertyControlType.enum) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.angle:
                    pass
                elif _on == Aep.PropertyControlType.boolean:
                    pass
                elif _on == Aep.PropertyControlType.enum:
                    pass
                elif _on == Aep.PropertyControlType.scalar:
                    pass
                elif _on == Aep.PropertyControlType.slider:
                    pass

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.three_d:
                    pass
                elif _on == Aep.PropertyControlType.two_d:
                    pass

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.three_d:
                    pass
                elif _on == Aep.PropertyControlType.two_d:
                    pass

            if self.property_control_type == Aep.PropertyControlType.three_d:
                pass

            if self.property_control_type == Aep.PropertyControlType.enum:
                pass

            if  ((self.property_control_type == Aep.PropertyControlType.boolean) or (self.property_control_type == Aep.PropertyControlType.enum)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.boolean:
                    pass
                elif _on == Aep.PropertyControlType.enum:
                    pass

            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.color) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                pass
                if len(self._unnamed12) != (72 if self.property_control_type == Aep.PropertyControlType.scalar else (64 if self.property_control_type == Aep.PropertyControlType.color else 52)):
                    raise kaitaistruct.ConsistencyError(u"_unnamed12", (72 if self.property_control_type == Aep.PropertyControlType.scalar else (64 if self.property_control_type == Aep.PropertyControlType.color else 52)), len(self._unnamed12))

            if self.property_control_type == Aep.PropertyControlType.scalar:
                pass

            if self.property_control_type == Aep.PropertyControlType.scalar:
                pass
                if len(self._unnamed14) != 2:
                    raise kaitaistruct.ConsistencyError(u"_unnamed14", 2, len(self._unnamed14))

            if self.property_control_type == Aep.PropertyControlType.color:
                pass
                if len(self.max_color) != 4:
                    raise kaitaistruct.ConsistencyError(u"max_color", 4, len(self.max_color))
                for i in range(len(self.max_color)):
                    pass


            if  ((self.property_control_type == Aep.PropertyControlType.scalar) or (self.property_control_type == Aep.PropertyControlType.slider)) :
                pass
                _on = self.property_control_type
                if _on == Aep.PropertyControlType.scalar:
                    pass
                elif _on == Aep.PropertyControlType.slider:
                    pass

            self._dirty = False

        @property
        def last_value_x(self):
            if hasattr(self, '_m_last_value_x'):
                return self._m_last_value_x

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                pass
                self._m_last_value_x = self.last_value_x_raw * (1 // 128 if self.property_control_type == Aep.PropertyControlType.two_d else 512)

            return getattr(self, '_m_last_value_x', None)

        def _invalidate_last_value_x(self):
            del self._m_last_value_x
        @property
        def last_value_y(self):
            if hasattr(self, '_m_last_value_y'):
                return self._m_last_value_y

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                pass
                self._m_last_value_y = self.last_value_y_raw * (1 // 128 if self.property_control_type == Aep.PropertyControlType.two_d else 512)

            return getattr(self, '_m_last_value_y', None)

        def _invalidate_last_value_y(self):
            del self._m_last_value_y
        @property
        def last_value_z(self):
            if hasattr(self, '_m_last_value_z'):
                return self._m_last_value_z

            if self.property_control_type == Aep.PropertyControlType.three_d:
                pass
                self._m_last_value_z = self.last_value_z_raw * 512

            return getattr(self, '_m_last_value_z', None)

        def _invalidate_last_value_z(self):
            del self._m_last_value_z

    class RenderSettingsLdatBody(ReadWriteKaitaiStruct):
        """Render settings ldat chunk (2246 bytes)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.RenderSettingsLdatBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bytes(7)
            self._unnamed1 = self._io.read_bits_int_be(5)
            self.queue_item_notify = self._io.read_bits_int_be(1) != 0
            self._unnamed3 = self._io.read_bits_int_be(2)
            self.comp_id = self._io.read_u4be()
            self.status = self._io.read_u4be()
            self._unnamed6 = self._io.read_bytes(4)
            self.time_span_start_frames = self._io.read_u4be()
            self.time_span_start_timebase = self._io.read_u4be()
            self.time_span_duration_frames = self._io.read_u4be()
            self.time_span_duration_timebase = self._io.read_u4be()
            self._unnamed11 = self._io.read_bytes(8)
            self.frame_rate_integer = self._io.read_u2be()
            self.frame_rate_fractional = self._io.read_u2be()
            self._unnamed14 = self._io.read_bytes(2)
            self.field_render = self._io.read_u2be()
            self._unnamed16 = self._io.read_bytes(2)
            self.pulldown = self._io.read_u2be()
            self.quality = self._io.read_u2be()
            self.resolution_x = self._io.read_u2be()
            self.resolution_y = self._io.read_u2be()
            self._unnamed21 = self._io.read_bytes(2)
            self.effects = self._io.read_u2be()
            self._unnamed23 = self._io.read_bytes(2)
            self.proxy_use = self._io.read_u2be()
            self._unnamed25 = self._io.read_bytes(2)
            self.motion_blur = self._io.read_u2be()
            self._unnamed27 = self._io.read_bytes(2)
            self.frame_blending = self._io.read_u2be()
            self._unnamed29 = self._io.read_bytes(2)
            self.log_type = self._io.read_u2be()
            self._unnamed31 = self._io.read_bytes(2)
            self.skip_existing_files = self._io.read_u2be()
            self._unnamed33 = self._io.read_bytes(4)
            self.template_name = (KaitaiStream.bytes_terminate(self._io.read_bytes(64), 0, False)).decode(u"ASCII")
            self._unnamed35 = self._io.read_bytes(1990)
            self.use_this_frame_rate = self._io.read_u2be()
            self._unnamed37 = self._io.read_bytes(2)
            self.time_span_source = self._io.read_u2be()
            self._unnamed39 = self._io.read_bytes(14)
            self.solo_switches = self._io.read_u2be()
            self._unnamed41 = self._io.read_bytes(2)
            self.disk_cache = self._io.read_u2be()
            self._unnamed43 = self._io.read_bytes(2)
            self.guide_layers = self._io.read_u2be()
            self._unnamed45 = self._io.read_bytes(6)
            self.color_depth = self._io.read_u2be()
            self._unnamed47 = self._io.read_bytes(16)
            self.start_time = self._io.read_u4be()
            self.elapsed_seconds = self._io.read_u4be()
            self.remaining = self._io.read_bytes(40)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.RenderSettingsLdatBody, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)
            self._io.write_bits_int_be(5, self._unnamed1)
            self._io.write_bits_int_be(1, int(self.queue_item_notify))
            self._io.write_bits_int_be(2, self._unnamed3)
            self._io.write_u4be(self.comp_id)
            self._io.write_u4be(self.status)
            self._io.write_bytes(self._unnamed6)
            self._io.write_u4be(self.time_span_start_frames)
            self._io.write_u4be(self.time_span_start_timebase)
            self._io.write_u4be(self.time_span_duration_frames)
            self._io.write_u4be(self.time_span_duration_timebase)
            self._io.write_bytes(self._unnamed11)
            self._io.write_u2be(self.frame_rate_integer)
            self._io.write_u2be(self.frame_rate_fractional)
            self._io.write_bytes(self._unnamed14)
            self._io.write_u2be(self.field_render)
            self._io.write_bytes(self._unnamed16)
            self._io.write_u2be(self.pulldown)
            self._io.write_u2be(self.quality)
            self._io.write_u2be(self.resolution_x)
            self._io.write_u2be(self.resolution_y)
            self._io.write_bytes(self._unnamed21)
            self._io.write_u2be(self.effects)
            self._io.write_bytes(self._unnamed23)
            self._io.write_u2be(self.proxy_use)
            self._io.write_bytes(self._unnamed25)
            self._io.write_u2be(self.motion_blur)
            self._io.write_bytes(self._unnamed27)
            self._io.write_u2be(self.frame_blending)
            self._io.write_bytes(self._unnamed29)
            self._io.write_u2be(self.log_type)
            self._io.write_bytes(self._unnamed31)
            self._io.write_u2be(self.skip_existing_files)
            self._io.write_bytes(self._unnamed33)
            self._io.write_bytes_limit((self.template_name).encode(u"ASCII"), 64, 0, 0)
            self._io.write_bytes(self._unnamed35)
            self._io.write_u2be(self.use_this_frame_rate)
            self._io.write_bytes(self._unnamed37)
            self._io.write_u2be(self.time_span_source)
            self._io.write_bytes(self._unnamed39)
            self._io.write_u2be(self.solo_switches)
            self._io.write_bytes(self._unnamed41)
            self._io.write_u2be(self.disk_cache)
            self._io.write_bytes(self._unnamed43)
            self._io.write_u2be(self.guide_layers)
            self._io.write_bytes(self._unnamed45)
            self._io.write_u2be(self.color_depth)
            self._io.write_bytes(self._unnamed47)
            self._io.write_u4be(self.start_time)
            self._io.write_u4be(self.elapsed_seconds)
            self._io.write_bytes(self.remaining)


        def _check(self):
            if len(self._unnamed0) != 7:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 7, len(self._unnamed0))
            if len(self._unnamed6) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed6", 4, len(self._unnamed6))
            if len(self._unnamed11) != 8:
                raise kaitaistruct.ConsistencyError(u"_unnamed11", 8, len(self._unnamed11))
            if len(self._unnamed14) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed14", 2, len(self._unnamed14))
            if len(self._unnamed16) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed16", 2, len(self._unnamed16))
            if len(self._unnamed21) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed21", 2, len(self._unnamed21))
            if len(self._unnamed23) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed23", 2, len(self._unnamed23))
            if len(self._unnamed25) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed25", 2, len(self._unnamed25))
            if len(self._unnamed27) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed27", 2, len(self._unnamed27))
            if len(self._unnamed29) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed29", 2, len(self._unnamed29))
            if len(self._unnamed31) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed31", 2, len(self._unnamed31))
            if len(self._unnamed33) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed33", 4, len(self._unnamed33))
            if len((self.template_name).encode(u"ASCII")) > 64:
                raise kaitaistruct.ConsistencyError(u"template_name", 64, len((self.template_name).encode(u"ASCII")))
            if KaitaiStream.byte_array_index_of((self.template_name).encode(u"ASCII"), 0) != -1:
                raise kaitaistruct.ConsistencyError(u"template_name", -1, KaitaiStream.byte_array_index_of((self.template_name).encode(u"ASCII"), 0))
            if len(self._unnamed35) != 1990:
                raise kaitaistruct.ConsistencyError(u"_unnamed35", 1990, len(self._unnamed35))
            if len(self._unnamed37) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed37", 2, len(self._unnamed37))
            if len(self._unnamed39) != 14:
                raise kaitaistruct.ConsistencyError(u"_unnamed39", 14, len(self._unnamed39))
            if len(self._unnamed41) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed41", 2, len(self._unnamed41))
            if len(self._unnamed43) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed43", 2, len(self._unnamed43))
            if len(self._unnamed45) != 6:
                raise kaitaistruct.ConsistencyError(u"_unnamed45", 6, len(self._unnamed45))
            if len(self._unnamed47) != 16:
                raise kaitaistruct.ConsistencyError(u"_unnamed47", 16, len(self._unnamed47))
            if len(self.remaining) != 40:
                raise kaitaistruct.ConsistencyError(u"remaining", 40, len(self.remaining))
            self._dirty = False

        @property
        def frame_rate(self):
            """Frame rate in fps (integer + fractional)."""
            if hasattr(self, '_m_frame_rate'):
                return self._m_frame_rate

            self._m_frame_rate = self.frame_rate_integer + (self.frame_rate_fractional * 1.0) / 65536
            return getattr(self, '_m_frame_rate', None)

        def _invalidate_frame_rate(self):
            del self._m_frame_rate
        @property
        def time_span_duration(self):
            """Time span duration in seconds."""
            if hasattr(self, '_m_time_span_duration'):
                return self._m_time_span_duration

            self._m_time_span_duration = ((self.time_span_duration_frames * 1.0) / self.time_span_duration_timebase if self.time_span_duration_timebase != 0 else 0)
            return getattr(self, '_m_time_span_duration', None)

        def _invalidate_time_span_duration(self):
            del self._m_time_span_duration
        @property
        def time_span_start(self):
            """Time span start in seconds."""
            if hasattr(self, '_m_time_span_start'):
                return self._m_time_span_start

            self._m_time_span_start = ((self.time_span_start_frames * 1.0) / self.time_span_start_timebase if self.time_span_start_timebase != 0 else 0)
            return getattr(self, '_m_time_span_start', None)

        def _invalidate_time_span_start(self):
            del self._m_time_span_start

    class RhedBody(ReadWriteKaitaiStruct):
        """Render preferences header. Contains GPU acceleration settings.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.RhedBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bytes(13)
            self.gpu_accel_type = self._io.read_u1()
            self._unnamed2 = self._io.read_bytes_full()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.RhedBody, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)
            self._io.write_u1(self.gpu_accel_type)
            self._io.write_bytes(self._unnamed2)
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"_unnamed2", 0, self._io.size() - self._io.pos())


        def _check(self):
            if len(self._unnamed0) != 13:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 13, len(self._unnamed0))
            self._dirty = False


    class RoouBody(ReadWriteKaitaiStruct):
        """Output module settings (154 bytes)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.RoouBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.magic = self._io.read_bytes(4)
            self.video_codec = (self._io.read_bytes(4)).decode(u"ASCII")
            self._unnamed2 = self._io.read_bytes(24)
            self._unnamed3 = self._io.read_bytes(4)
            self.width = self._io.read_u2be()
            self._unnamed5 = self._io.read_bytes(2)
            self.height = self._io.read_u2be()
            self._unnamed7 = self._io.read_bytes(25)
            self.frame_rate = self._io.read_u1()
            self._unnamed9 = self._io.read_bytes(9)
            self.color_premultiplied = self._io.read_u1()
            self._unnamed11 = self._io.read_bytes(3)
            self.color_matted = self._io.read_u1()
            self._unnamed13 = self._io.read_bytes(26)
            self.audio_disabled_hi = self._io.read_u1()
            self.audio_format = self._io.read_u1()
            self._unnamed16 = self._io.read_bytes(1)
            self.audio_bit_depth = self._io.read_u1()
            self._unnamed18 = self._io.read_bytes(1)
            self.audio_channels = self._io.read_u1()
            self._unnamed20 = self._io.read_bytes_full()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.RoouBody, self)._write__seq(io)
            self._io.write_bytes(self.magic)
            self._io.write_bytes((self.video_codec).encode(u"ASCII"))
            self._io.write_bytes(self._unnamed2)
            self._io.write_bytes(self._unnamed3)
            self._io.write_u2be(self.width)
            self._io.write_bytes(self._unnamed5)
            self._io.write_u2be(self.height)
            self._io.write_bytes(self._unnamed7)
            self._io.write_u1(self.frame_rate)
            self._io.write_bytes(self._unnamed9)
            self._io.write_u1(self.color_premultiplied)
            self._io.write_bytes(self._unnamed11)
            self._io.write_u1(self.color_matted)
            self._io.write_bytes(self._unnamed13)
            self._io.write_u1(self.audio_disabled_hi)
            self._io.write_u1(self.audio_format)
            self._io.write_bytes(self._unnamed16)
            self._io.write_u1(self.audio_bit_depth)
            self._io.write_bytes(self._unnamed18)
            self._io.write_u1(self.audio_channels)
            self._io.write_bytes(self._unnamed20)
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"_unnamed20", 0, self._io.size() - self._io.pos())


        def _check(self):
            if len(self.magic) != 4:
                raise kaitaistruct.ConsistencyError(u"magic", 4, len(self.magic))
            if len((self.video_codec).encode(u"ASCII")) != 4:
                raise kaitaistruct.ConsistencyError(u"video_codec", 4, len((self.video_codec).encode(u"ASCII")))
            if len(self._unnamed2) != 24:
                raise kaitaistruct.ConsistencyError(u"_unnamed2", 24, len(self._unnamed2))
            if len(self._unnamed3) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed3", 4, len(self._unnamed3))
            if len(self._unnamed5) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed5", 2, len(self._unnamed5))
            if len(self._unnamed7) != 25:
                raise kaitaistruct.ConsistencyError(u"_unnamed7", 25, len(self._unnamed7))
            if len(self._unnamed9) != 9:
                raise kaitaistruct.ConsistencyError(u"_unnamed9", 9, len(self._unnamed9))
            if len(self._unnamed11) != 3:
                raise kaitaistruct.ConsistencyError(u"_unnamed11", 3, len(self._unnamed11))
            if len(self._unnamed13) != 26:
                raise kaitaistruct.ConsistencyError(u"_unnamed13", 26, len(self._unnamed13))
            if len(self._unnamed16) != 1:
                raise kaitaistruct.ConsistencyError(u"_unnamed16", 1, len(self._unnamed16))
            if len(self._unnamed18) != 1:
                raise kaitaistruct.ConsistencyError(u"_unnamed18", 1, len(self._unnamed18))
            self._dirty = False

        @property
        def output_audio(self):
            if hasattr(self, '_m_output_audio'):
                return self._m_output_audio

            self._m_output_audio = self.audio_disabled_hi != 255
            return getattr(self, '_m_output_audio', None)

        def _invalidate_output_audio(self):
            del self._m_output_audio
        @property
        def video_output(self):
            """True when video output is enabled (width or height non-zero)."""
            if hasattr(self, '_m_video_output'):
                return self._m_video_output

            self._m_video_output =  ((self.width > 0) or (self.height > 0)) 
            return getattr(self, '_m_video_output', None)

        def _invalidate_video_output(self):
            del self._m_video_output

    class RoutBody(ReadWriteKaitaiStruct):
        """Render queue item flags (4-byte header + 4 bytes per item)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.RoutBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bytes(4)
            self.items = []
            i = 0
            while not self._io.is_eof():
                _t_items = Aep.RoutItem(self._io, self, self._root)
                try:
                    _t_items._read()
                finally:
                    self.items.append(_t_items)
                i += 1

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.items)):
                pass
                self.items[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Aep.RoutBody, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)
            for i in range(len(self.items)):
                pass
                if self._io.is_eof():
                    raise kaitaistruct.ConsistencyError(u"items", 0, self._io.size() - self._io.pos())
                self.items[i]._write__seq(self._io)

            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"items", 0, self._io.size() - self._io.pos())


        def _check(self):
            if len(self._unnamed0) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 4, len(self._unnamed0))
            for i in range(len(self.items)):
                pass
                if self.items[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"items", self._root, self.items[i]._root)
                if self.items[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"items", self, self.items[i]._parent)

            self._dirty = False


    class RoutItem(ReadWriteKaitaiStruct):
        """Per-item render queue flags (4 bytes)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.RoutItem, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bits_int_be(1) != 0
            self.render = self._io.read_bits_int_be(1) != 0
            self._unnamed2 = self._io.read_bits_int_be(6)
            self._unnamed3 = self._io.read_bytes(3)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.RoutItem, self)._write__seq(io)
            self._io.write_bits_int_be(1, int(self._unnamed0))
            self._io.write_bits_int_be(1, int(self.render))
            self._io.write_bits_int_be(6, self._unnamed2)
            self._io.write_bytes(self._unnamed3)


        def _check(self):
            if len(self._unnamed3) != 3:
                raise kaitaistruct.ConsistencyError(u"_unnamed3", 3, len(self._unnamed3))
            self._dirty = False


    class SspcBody(ReadWriteKaitaiStruct):
        """Source footage settings chunk. Contains dimension, timing, and alpha/field settings.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.SspcBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bytes(32)
            self.width = self._io.read_u2be()
            self._unnamed2 = self._io.read_bytes(2)
            self.height = self._io.read_u2be()
            self.duration_dividend = self._io.read_u4be()
            self.duration_divisor = self._io.read_u4be()
            self._unnamed6 = self._io.read_bytes(10)
            self.frame_rate_base = self._io.read_u4be()
            self.frame_rate_fractional = self._io.read_u2be()
            self._unnamed9 = self._io.read_bytes(7)
            self._unnamed10 = self._io.read_bits_int_be(6)
            self.invert_alpha = self._io.read_bits_int_be(1) != 0
            self.premultiplied = self._io.read_bits_int_be(1) != 0
            self.premul_color_r = self._io.read_u1()
            self.premul_color_g = self._io.read_u1()
            self.premul_color_b = self._io.read_u1()
            self.alpha_mode_raw = self._io.read_u1()
            self._unnamed17 = self._io.read_bytes(9)
            self.field_separation_type_raw = self._io.read_u1()
            self._unnamed19 = self._io.read_bytes(3)
            self.field_order = self._io.read_u1()
            self._unnamed21 = self._io.read_bytes(41)
            self.loop = self._io.read_u1()
            self._unnamed23 = self._io.read_bytes(6)
            self.pixel_ratio_width = self._io.read_u4be()
            self.pixel_ratio_height = self._io.read_u4be()
            self._unnamed26 = self._io.read_bytes(5)
            self.conform_frame_rate = self._io.read_u1()
            self._unnamed28 = self._io.read_bytes(9)
            self.high_quality_field_separation = self._io.read_u1()
            self._unnamed30 = self._io.read_bytes(12)
            self.start_frame = self._io.read_u4be()
            self.end_frame = self._io.read_u4be()
            self._unnamed33 = self._io.read_bytes_full()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.SspcBody, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)
            self._io.write_u2be(self.width)
            self._io.write_bytes(self._unnamed2)
            self._io.write_u2be(self.height)
            self._io.write_u4be(self.duration_dividend)
            self._io.write_u4be(self.duration_divisor)
            self._io.write_bytes(self._unnamed6)
            self._io.write_u4be(self.frame_rate_base)
            self._io.write_u2be(self.frame_rate_fractional)
            self._io.write_bytes(self._unnamed9)
            self._io.write_bits_int_be(6, self._unnamed10)
            self._io.write_bits_int_be(1, int(self.invert_alpha))
            self._io.write_bits_int_be(1, int(self.premultiplied))
            self._io.write_u1(self.premul_color_r)
            self._io.write_u1(self.premul_color_g)
            self._io.write_u1(self.premul_color_b)
            self._io.write_u1(self.alpha_mode_raw)
            self._io.write_bytes(self._unnamed17)
            self._io.write_u1(self.field_separation_type_raw)
            self._io.write_bytes(self._unnamed19)
            self._io.write_u1(self.field_order)
            self._io.write_bytes(self._unnamed21)
            self._io.write_u1(self.loop)
            self._io.write_bytes(self._unnamed23)
            self._io.write_u4be(self.pixel_ratio_width)
            self._io.write_u4be(self.pixel_ratio_height)
            self._io.write_bytes(self._unnamed26)
            self._io.write_u1(self.conform_frame_rate)
            self._io.write_bytes(self._unnamed28)
            self._io.write_u1(self.high_quality_field_separation)
            self._io.write_bytes(self._unnamed30)
            self._io.write_u4be(self.start_frame)
            self._io.write_u4be(self.end_frame)
            self._io.write_bytes(self._unnamed33)
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"_unnamed33", 0, self._io.size() - self._io.pos())


        def _check(self):
            if len(self._unnamed0) != 32:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 32, len(self._unnamed0))
            if len(self._unnamed2) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed2", 2, len(self._unnamed2))
            if len(self._unnamed6) != 10:
                raise kaitaistruct.ConsistencyError(u"_unnamed6", 10, len(self._unnamed6))
            if len(self._unnamed9) != 7:
                raise kaitaistruct.ConsistencyError(u"_unnamed9", 7, len(self._unnamed9))
            if len(self._unnamed17) != 9:
                raise kaitaistruct.ConsistencyError(u"_unnamed17", 9, len(self._unnamed17))
            if len(self._unnamed19) != 3:
                raise kaitaistruct.ConsistencyError(u"_unnamed19", 3, len(self._unnamed19))
            if len(self._unnamed21) != 41:
                raise kaitaistruct.ConsistencyError(u"_unnamed21", 41, len(self._unnamed21))
            if len(self._unnamed23) != 6:
                raise kaitaistruct.ConsistencyError(u"_unnamed23", 6, len(self._unnamed23))
            if len(self._unnamed26) != 5:
                raise kaitaistruct.ConsistencyError(u"_unnamed26", 5, len(self._unnamed26))
            if len(self._unnamed28) != 9:
                raise kaitaistruct.ConsistencyError(u"_unnamed28", 9, len(self._unnamed28))
            if len(self._unnamed30) != 12:
                raise kaitaistruct.ConsistencyError(u"_unnamed30", 12, len(self._unnamed30))
            self._dirty = False

        @property
        def duration(self):
            if hasattr(self, '_m_duration'):
                return self._m_duration

            self._m_duration = self.duration_dividend / self.duration_divisor
            return getattr(self, '_m_duration', None)

        def _invalidate_duration(self):
            del self._m_duration
        @property
        def frame_duration(self):
            if hasattr(self, '_m_frame_duration'):
                return self._m_frame_duration

            self._m_frame_duration = self.duration * self.frame_rate
            return getattr(self, '_m_frame_duration', None)

        def _invalidate_frame_duration(self):
            del self._m_frame_duration
        @property
        def frame_rate(self):
            if hasattr(self, '_m_frame_rate'):
                return self._m_frame_rate

            self._m_frame_rate = self.frame_rate_base + self.frame_rate_fractional / (1 << 16)
            return getattr(self, '_m_frame_rate', None)

        def _invalidate_frame_rate(self):
            del self._m_frame_rate
        @property
        def has_alpha(self):
            """True if footage has an alpha channel (3 means no_alpha)."""
            if hasattr(self, '_m_has_alpha'):
                return self._m_has_alpha

            self._m_has_alpha = self.alpha_mode_raw != 3
            return getattr(self, '_m_has_alpha', None)

        def _invalidate_has_alpha(self):
            del self._m_has_alpha
        @property
        def pixel_aspect(self):
            if hasattr(self, '_m_pixel_aspect'):
                return self._m_pixel_aspect

            self._m_pixel_aspect = self.pixel_ratio_width / self.pixel_ratio_height
            return getattr(self, '_m_pixel_aspect', None)

        def _invalidate_pixel_aspect(self):
            del self._m_pixel_aspect

    class Tdb4Body(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.Tdb4Body, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bytes(2)
            self.dimensions = self._io.read_u2be()
            self._unnamed2 = self._io.read_bytes(1)
            self._unnamed3 = self._io.read_bits_int_be(4)
            self.is_spatial = self._io.read_bits_int_be(1) != 0
            self._unnamed5 = self._io.read_bits_int_be(2)
            self.static = self._io.read_bits_int_be(1) != 0
            self._unnamed7 = self._io.read_bytes(10)
            self.unknown_floats = []
            for i in range(5):
                self.unknown_floats.append(self._io.read_f8be())

            self._unnamed9 = self._io.read_bytes(1)
            self._unnamed10 = self._io.read_bits_int_be(7)
            self.no_value = self._io.read_bits_int_be(1) != 0
            self._unnamed12 = self._io.read_bytes(1)
            self._unnamed13 = self._io.read_bits_int_be(4)
            self.vector = self._io.read_bits_int_be(1) != 0
            self.integer = self._io.read_bits_int_be(1) != 0
            self._unnamed16 = self._io.read_bits_int_be(1) != 0
            self.color = self._io.read_bits_int_be(1) != 0
            self._unnamed18 = self._io.read_bytes(8)
            self.animated = self._io.read_u1()
            self._unnamed20 = self._io.read_bytes(15)
            self.unknown_floats_2 = []
            for i in range(4):
                self.unknown_floats_2.append(self._io.read_f8be())

            self._unnamed22 = self._io.read_bytes(3)
            self._unnamed23 = self._io.read_bits_int_be(7)
            self.expression_disabled = self._io.read_bits_int_be(1) != 0
            self._unnamed25 = self._io.read_bytes(4)
            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.unknown_floats)):
                pass

            for i in range(len(self.unknown_floats_2)):
                pass



        def _write__seq(self, io=None):
            super(Aep.Tdb4Body, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)
            self._io.write_u2be(self.dimensions)
            self._io.write_bytes(self._unnamed2)
            self._io.write_bits_int_be(4, self._unnamed3)
            self._io.write_bits_int_be(1, int(self.is_spatial))
            self._io.write_bits_int_be(2, self._unnamed5)
            self._io.write_bits_int_be(1, int(self.static))
            self._io.write_bytes(self._unnamed7)
            for i in range(len(self.unknown_floats)):
                pass
                self._io.write_f8be(self.unknown_floats[i])

            self._io.write_bytes(self._unnamed9)
            self._io.write_bits_int_be(7, self._unnamed10)
            self._io.write_bits_int_be(1, int(self.no_value))
            self._io.write_bytes(self._unnamed12)
            self._io.write_bits_int_be(4, self._unnamed13)
            self._io.write_bits_int_be(1, int(self.vector))
            self._io.write_bits_int_be(1, int(self.integer))
            self._io.write_bits_int_be(1, int(self._unnamed16))
            self._io.write_bits_int_be(1, int(self.color))
            self._io.write_bytes(self._unnamed18)
            self._io.write_u1(self.animated)
            self._io.write_bytes(self._unnamed20)
            for i in range(len(self.unknown_floats_2)):
                pass
                self._io.write_f8be(self.unknown_floats_2[i])

            self._io.write_bytes(self._unnamed22)
            self._io.write_bits_int_be(7, self._unnamed23)
            self._io.write_bits_int_be(1, int(self.expression_disabled))
            self._io.write_bytes(self._unnamed25)


        def _check(self):
            if len(self._unnamed0) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 2, len(self._unnamed0))
            if len(self._unnamed2) != 1:
                raise kaitaistruct.ConsistencyError(u"_unnamed2", 1, len(self._unnamed2))
            if len(self._unnamed7) != 10:
                raise kaitaistruct.ConsistencyError(u"_unnamed7", 10, len(self._unnamed7))
            if len(self.unknown_floats) != 5:
                raise kaitaistruct.ConsistencyError(u"unknown_floats", 5, len(self.unknown_floats))
            for i in range(len(self.unknown_floats)):
                pass

            if len(self._unnamed9) != 1:
                raise kaitaistruct.ConsistencyError(u"_unnamed9", 1, len(self._unnamed9))
            if len(self._unnamed12) != 1:
                raise kaitaistruct.ConsistencyError(u"_unnamed12", 1, len(self._unnamed12))
            if len(self._unnamed18) != 8:
                raise kaitaistruct.ConsistencyError(u"_unnamed18", 8, len(self._unnamed18))
            if len(self._unnamed20) != 15:
                raise kaitaistruct.ConsistencyError(u"_unnamed20", 15, len(self._unnamed20))
            if len(self.unknown_floats_2) != 4:
                raise kaitaistruct.ConsistencyError(u"unknown_floats_2", 4, len(self.unknown_floats_2))
            for i in range(len(self.unknown_floats_2)):
                pass

            if len(self._unnamed22) != 3:
                raise kaitaistruct.ConsistencyError(u"_unnamed22", 3, len(self._unnamed22))
            if len(self._unnamed25) != 4:
                raise kaitaistruct.ConsistencyError(u"_unnamed25", 4, len(self._unnamed25))
            self._dirty = False

        @property
        def expression_enabled(self):
            if hasattr(self, '_m_expression_enabled'):
                return self._m_expression_enabled

            self._m_expression_enabled = (not (self.expression_disabled))
            return getattr(self, '_m_expression_enabled', None)

        def _invalidate_expression_enabled(self):
            del self._m_expression_enabled

    class TdsbBody(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.TdsbBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self._unnamed0 = self._io.read_bytes(2)
            self._unnamed1 = self._io.read_bits_int_be(3)
            self.locked_ratio = self._io.read_bits_int_be(1) != 0
            self._unnamed3 = self._io.read_bits_int_be(4)
            self._unnamed4 = self._io.read_bits_int_be(6)
            self.dimensions_separated = self._io.read_bits_int_be(1) != 0
            self.enabled = self._io.read_bits_int_be(1) != 0
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.TdsbBody, self)._write__seq(io)
            self._io.write_bytes(self._unnamed0)
            self._io.write_bits_int_be(3, self._unnamed1)
            self._io.write_bits_int_be(1, int(self.locked_ratio))
            self._io.write_bits_int_be(4, self._unnamed3)
            self._io.write_bits_int_be(6, self._unnamed4)
            self._io.write_bits_int_be(1, int(self.dimensions_separated))
            self._io.write_bits_int_be(1, int(self.enabled))


        def _check(self):
            if len(self._unnamed0) != 2:
                raise kaitaistruct.ConsistencyError(u"_unnamed0", 2, len(self._unnamed0))
            self._dirty = False


    class Utf8Body(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Aep.Utf8Body, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.contents = (self._io.read_bytes_full()).decode(u"UTF-8")
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Aep.Utf8Body, self)._write__seq(io)
            self._io.write_bytes((self.contents).encode(u"UTF-8"))
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"contents", 0, self._io.size() - self._io.pos())


        def _check(self):
            self._dirty = False



