# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Aep(KaitaiStruct):

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
    def __init__(self, _io, _parent=None, _root=None):
        super(Aep, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

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
        self.xmp_packet = (self._io.read_bytes_full()).decode(u"UTF-8")


    def _fetch_instances(self):
        pass
        self.data._fetch_instances()

    class AcerBody(KaitaiStruct):
        """Compensate for Scene-Referred Profiles setting in Project Settings.
        This setting affects how scene-referred color profiles are handled.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.AcerBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.compensate_for_scene_referred_profiles = self._io.read_u1()


        def _fetch_instances(self):
            pass


    class AsciiBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.AsciiBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.contents = self._io.read_bytes_full()


        def _fetch_instances(self):
            pass


    class CdatBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.CdatBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.value = []
            for i in range(self._parent.len_data // 8):
                self.value.append(self._io.read_f8be())



        def _fetch_instances(self):
            pass
            for i in range(len(self.value)):
                pass



    class CdrpBody(KaitaiStruct):
        """Composition drop frame setting.
        When true, the composition uses drop-frame timecode.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.CdrpBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.drop_frame = self._io.read_u1()


        def _fetch_instances(self):
            pass


    class CdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.CdtaBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.resolution_factor = []
            for i in range(2):
                self.resolution_factor.append(self._io.read_u2be())

            self._unnamed1 = self._io.read_bytes(1)
            self.time_scale = self._io.read_u2be()
            self._unnamed3 = self._io.read_bytes(14)
            self.time_raw = self._io.read_s2be()
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
            self.display_start_time_dividend = self._io.read_s4be()
            self.display_start_time_divisor = self._io.read_u4be()
            self._unnamed31 = self._io.read_bytes(2)
            self.shutter_angle = self._io.read_u2be()
            self._unnamed33 = self._io.read_bytes(4)
            self.shutter_phase = self._io.read_s4be()
            self._unnamed35 = self._io.read_bytes(12)
            self.motion_blur_adaptive_sample_limit = self._io.read_s4be()
            self.motion_blur_samples_per_frame = self._io.read_s4be()


        def _fetch_instances(self):
            pass
            for i in range(len(self.resolution_factor)):
                pass

            for i in range(len(self.bg_color)):
                pass


        @property
        def display_start_frame(self):
            if hasattr(self, '_m_display_start_frame'):
                return self._m_display_start_frame

            self._m_display_start_frame = self.display_start_time * self.frame_rate
            return getattr(self, '_m_display_start_frame', None)

        @property
        def display_start_time(self):
            if hasattr(self, '_m_display_start_time'):
                return self._m_display_start_time

            self._m_display_start_time = (self.display_start_time_dividend * 1.0) / self.display_start_time_divisor
            return getattr(self, '_m_display_start_time', None)

        @property
        def duration(self):
            if hasattr(self, '_m_duration'):
                return self._m_duration

            self._m_duration = (self.duration_dividend * 1.0) / self.duration_divisor
            return getattr(self, '_m_duration', None)

        @property
        def frame_duration(self):
            if hasattr(self, '_m_frame_duration'):
                return self._m_frame_duration

            self._m_frame_duration = self.duration * self.frame_rate
            return getattr(self, '_m_frame_duration', None)

        @property
        def frame_in_point(self):
            if hasattr(self, '_m_frame_in_point'):
                return self._m_frame_in_point

            self._m_frame_in_point = self.display_start_frame + (self.in_point_raw * 1.0) / self.time_scale
            return getattr(self, '_m_frame_in_point', None)

        @property
        def frame_out_point(self):
            if hasattr(self, '_m_frame_out_point'):
                return self._m_frame_out_point

            self._m_frame_out_point = self.display_start_frame + (self.frame_duration if self.out_point_raw == 65535 else (self.out_point_raw * 1.0) / self.time_scale)
            return getattr(self, '_m_frame_out_point', None)

        @property
        def frame_rate(self):
            if hasattr(self, '_m_frame_rate'):
                return self._m_frame_rate

            self._m_frame_rate = self.frame_rate_integer + (self.frame_rate_fractional * 1.0) / 65536
            return getattr(self, '_m_frame_rate', None)

        @property
        def frame_time(self):
            if hasattr(self, '_m_frame_time'):
                return self._m_frame_time

            self._m_frame_time = (self.time_raw * 1.0) / self.time_scale
            return getattr(self, '_m_frame_time', None)

        @property
        def in_point(self):
            if hasattr(self, '_m_in_point'):
                return self._m_in_point

            self._m_in_point = self.frame_in_point / self.frame_rate
            return getattr(self, '_m_in_point', None)

        @property
        def out_point(self):
            if hasattr(self, '_m_out_point'):
                return self._m_out_point

            self._m_out_point = self.frame_out_point / self.frame_rate
            return getattr(self, '_m_out_point', None)

        @property
        def pixel_aspect(self):
            if hasattr(self, '_m_pixel_aspect'):
                return self._m_pixel_aspect

            self._m_pixel_aspect = (self.pixel_ratio_width * 1.0) / self.pixel_ratio_height
            return getattr(self, '_m_pixel_aspect', None)

        @property
        def time(self):
            if hasattr(self, '_m_time'):
                return self._m_time

            self._m_time = self.frame_time / self.frame_rate
            return getattr(self, '_m_time', None)


    class ChildUtf8Body(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.ChildUtf8Body, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.chunk = Aep.Chunk(self._io, self, self._root)


        def _fetch_instances(self):
            pass
            self.chunk._fetch_instances()


    class Chunk(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.Chunk, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.chunk_type = (self._io.read_bytes(4)).decode(u"ASCII")
            self.len_data = self._io.read_u4be()
            _on = self.chunk_type
            if _on == u"LIST":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ListBody(_io__raw_data, self, self._root)
            elif _on == u"NmHd":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.NmhdBody(_io__raw_data, self, self._root)
            elif _on == u"RCom":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
            elif _on == u"Roou":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.RoouBody(_io__raw_data, self, self._root)
            elif _on == u"Rout":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.RoutBody(_io__raw_data, self, self._root)
            elif _on == u"Utf8":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"acer":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.AcerBody(_io__raw_data, self, self._root)
            elif _on == u"alas":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"cdat":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.CdatBody(_io__raw_data, self, self._root)
            elif _on == u"cdrp":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.CdrpBody(_io__raw_data, self, self._root)
            elif _on == u"cdta":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.CdtaBody(_io__raw_data, self, self._root)
            elif _on == u"cmta":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"dwga":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.DwgaBody(_io__raw_data, self, self._root)
            elif _on == u"fcid":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.FcidBody(_io__raw_data, self, self._root)
            elif _on == u"fdta":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.FdtaBody(_io__raw_data, self, self._root)
            elif _on == u"fiac":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.FiacBody(_io__raw_data, self, self._root)
            elif _on == u"fips":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.FipsBody(_io__raw_data, self, self._root)
            elif _on == u"fitt":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.FittBody(_io__raw_data, self, self._root)
            elif _on == u"fivc":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.FivcBody(_io__raw_data, self, self._root)
            elif _on == u"fivi":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.FiviBody(_io__raw_data, self, self._root)
            elif _on == u"fnam":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
            elif _on == u"foac":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.FoacBody(_io__raw_data, self, self._root)
            elif _on == u"head":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.HeadBody(_io__raw_data, self, self._root)
            elif _on == u"idta":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.IdtaBody(_io__raw_data, self, self._root)
            elif _on == u"ldat":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.LdatBody(_io__raw_data, self, self._root)
            elif _on == u"ldta":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.LdtaBody(_io__raw_data, self, self._root)
            elif _on == u"lhd3":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Lhd3Body(_io__raw_data, self, self._root)
            elif _on == u"nnhd":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.NnhdBody(_io__raw_data, self, self._root)
            elif _on == u"opti":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.OptiBody(_io__raw_data, self, self._root)
            elif _on == u"pard":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.PardBody(_io__raw_data, self, self._root)
            elif _on == u"pdnm":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
            elif _on == u"pjef":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"sspc":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.SspcBody(_io__raw_data, self, self._root)
            elif _on == u"tdb4":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Tdb4Body(_io__raw_data, self, self._root)
            elif _on == u"tdmn":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == u"tdsb":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.TdsbBody(_io__raw_data, self, self._root)
            elif _on == u"tdsn":
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ChildUtf8Body(_io__raw_data, self, self._root)
            else:
                pass
                self._raw_data = self._io.read_bytes((self._io.size() - self._io.pos() if self.len_data > self._io.size() - self._io.pos() else self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.AsciiBody(_io__raw_data, self, self._root)
            if self.len_data % 2 != 0:
                pass
                self.padding = self._io.read_bytes(1)



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
            elif _on == u"cdrp":
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
            elif _on == u"fcid":
                pass
                self.data._fetch_instances()
            elif _on == u"fdta":
                pass
                self.data._fetch_instances()
            elif _on == u"fiac":
                pass
                self.data._fetch_instances()
            elif _on == u"fips":
                pass
                self.data._fetch_instances()
            elif _on == u"fitt":
                pass
                self.data._fetch_instances()
            elif _on == u"fivc":
                pass
                self.data._fetch_instances()
            elif _on == u"fivi":
                pass
                self.data._fetch_instances()
            elif _on == u"fnam":
                pass
                self.data._fetch_instances()
            elif _on == u"foac":
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



    class Chunks(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.Chunks, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.chunks = []
            i = 0
            while not self._io.is_eof():
                self.chunks.append(Aep.Chunk(self._io, self, self._root))
                i += 1



        def _fetch_instances(self):
            pass
            for i in range(len(self.chunks)):
                pass
                self.chunks[i]._fetch_instances()



    class DwgaBody(KaitaiStruct):
        """Working gamma setting. Indicates the gamma value used for color management.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.DwgaBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.working_gamma_selector = self._io.read_u1()
            self._unnamed1 = self._io.read_bytes(3)


        def _fetch_instances(self):
            pass


    class FcidBody(KaitaiStruct):
        """Active composition item ID. Stores the item ID of the currently
        active (most recently focused) composition in the project.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.FcidBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.active_item_id = self._io.read_u4be()


        def _fetch_instances(self):
            pass


    class FdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.FdtaBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(1)


        def _fetch_instances(self):
            pass


    class FiacBody(KaitaiStruct):
        """Viewer inner tab active flag. When non-zero, the inner tab
        (e.g. Composition, Layer, Footage) is focused.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.FiacBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.active = self._io.read_u1()


        def _fetch_instances(self):
            pass


    class FipsBody(KaitaiStruct):
        """Folder item panel settings. Stores viewer panel state including
        Draft 3D mode, view options (channels, exposure, zoom, etc.), and
        toggle flags (guides, rulers, grid, etc.). There are typically 4
        fips chunks per viewer group, one for each AE composition viewer
        panel. Total size is 96 bytes.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.FipsBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(7)
            self.channels = self._io.read_u1()
            self._unnamed2 = self._io.read_bytes(3)
            self._unnamed3 = self._io.read_bits_int_be(6)
            self.proportional_grid = self._io.read_bits_int_be(1) != 0
            self.title_action_safe = self._io.read_bits_int_be(1) != 0
            self._unnamed6 = self._io.read_bits_int_be(5)
            self.draft_3d = self._io.read_bits_int_be(1) != 0
            self._unnamed8 = self._io.read_bits_int_be(2)
            self._unnamed9 = self._io.read_bits_int_be(7)
            self.fast_preview_adaptive = self._io.read_bits_int_be(1) != 0
            self.region_of_interest = self._io.read_bits_int_be(1) != 0
            self.rulers = self._io.read_bits_int_be(1) != 0
            self._unnamed13 = self._io.read_bits_int_be(1) != 0
            self.fast_preview_wireframe = self._io.read_bits_int_be(1) != 0
            self._unnamed15 = self._io.read_bits_int_be(4)
            self.transparency_grid = self._io.read_bits_int_be(1) != 0
            self._unnamed17 = self._io.read_bits_int_be(2)
            self.mask_and_shape_path = self._io.read_bits_int_be(1) != 0
            self._unnamed19 = self._io.read_bits_int_be(4)
            self._unnamed20 = self._io.read_bytes(7)
            self._unnamed21 = self._io.read_bits_int_be(4)
            self.grid = self._io.read_bits_int_be(1) != 0
            self._unnamed23 = self._io.read_bits_int_be(2)
            self.guides_visibility = self._io.read_bits_int_be(1) != 0
            self._unnamed25 = self._io.read_bytes(45)
            self.zoom_type = self._io.read_u1()
            self._unnamed27 = self._io.read_bytes(2)
            self.zoom = self._io.read_f8be()
            self.exposure = self._io.read_f4be()
            self._unnamed30 = self._io.read_bytes(1)
            self._unnamed31 = self._io.read_bits_int_be(7)
            self.use_display_color_management = self._io.read_bits_int_be(1) != 0
            self._unnamed33 = self._io.read_bits_int_be(7)
            self.auto_resolution = self._io.read_bits_int_be(1) != 0
            self._unnamed35 = self._io.read_bytes_full()


        def _fetch_instances(self):
            pass


    class FittBody(KaitaiStruct):
        """Viewer inner tab type label. An ASCII string identifying the
        viewer type (e.g. "AE Composition", "AE Layer", "AE Footage").
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.FittBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.label = (self._io.read_bytes_full()).decode(u"ASCII")


        def _fetch_instances(self):
            pass


    class FivcBody(KaitaiStruct):
        """Viewer inner view count. The number of views in the inner tab.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.FivcBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.view_count = self._io.read_u2be()


        def _fetch_instances(self):
            pass


    class FiviBody(KaitaiStruct):
        """Viewer inner active view index. The zero-based index of the
        currently active view within the inner tab.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.FiviBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.active_view_index = self._io.read_u4be()


        def _fetch_instances(self):
            pass


    class FoacBody(KaitaiStruct):
        """Viewer outer tab active flag. When non-zero, the outer panel
        (e.g. Timeline) is focused.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.FoacBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.active = self._io.read_u1()


        def _fetch_instances(self):
            pass


    class HeadBody(KaitaiStruct):
        """After Effects file header. Contains version info encoded as a 32-bit value.
        Major version = MAJOR-A * 8 + MAJOR-B
        See: https://github.com/tinogithub/aftereffects-version-check
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.HeadBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

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


        def _fetch_instances(self):
            pass

        @property
        def ae_version_beta(self):
            """True if beta version."""
            if hasattr(self, '_m_ae_version_beta'):
                return self._m_ae_version_beta

            self._m_ae_version_beta = (not (self.ae_version_beta_flag))
            return getattr(self, '_m_ae_version_beta', None)

        @property
        def ae_version_major(self):
            """Full major version number (e.g., 25)."""
            if hasattr(self, '_m_ae_version_major'):
                return self._m_ae_version_major

            self._m_ae_version_major = self.ae_version_major_a * 8 + self.ae_version_major_b
            return getattr(self, '_m_ae_version_major', None)


    class IdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.IdtaBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.item_type = KaitaiStream.resolve_enum(Aep.ItemType, self._io.read_u2be())
            self._unnamed1 = self._io.read_bytes(14)
            self.id = self._io.read_u4be()
            self._unnamed3 = self._io.read_bytes(38)
            self.label = KaitaiStream.resolve_enum(Aep.Label, self._io.read_u1())


        def _fetch_instances(self):
            pass


    class KfColor(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.KfColor, self).__init__(_io)
            self._parent = _parent
            self._root = _root
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



        def _fetch_instances(self):
            pass
            for i in range(len(self.value)):
                pass

            for i in range(len(self._unnamed7)):
                pass



    class KfMultiDimensional(KaitaiStruct):
        def __init__(self, num_value, _io, _parent=None, _root=None):
            super(Aep.KfMultiDimensional, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.num_value = num_value
            self._read()

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



    class KfNoValue(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.KfNoValue, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_u8be()
            self._unnamed1 = self._io.read_f8be()
            self.in_speed = self._io.read_f8be()
            self.in_influence = self._io.read_f8be()
            self.out_speed = self._io.read_f8be()
            self.out_influence = self._io.read_f8be()


        def _fetch_instances(self):
            pass


    class KfPosition(KaitaiStruct):
        def __init__(self, num_value, _io, _parent=None, _root=None):
            super(Aep.KfPosition, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.num_value = num_value
            self._read()

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



        def _fetch_instances(self):
            pass
            for i in range(len(self.value)):
                pass

            for i in range(len(self.tan_in)):
                pass

            for i in range(len(self.tan_out)):
                pass



    class KfUnknownData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.KfUnknownData, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.contents = self._io.read_bytes_full()


        def _fetch_instances(self):
            pass


    class LdatBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.LdatBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.items = self._io.read_bytes_full()


        def _fetch_instances(self):
            pass


    class LdatItem(KaitaiStruct):
        def __init__(self, item_type, _io, _parent=None, _root=None):
            super(Aep.LdatItem, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.item_type = item_type
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(1)
            self.time_raw = self._io.read_s2be()
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
            elif _on == Aep.LdatItemType.gide:
                pass
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
            elif _on == Aep.LdatItemType.litm:
                pass
                self.kf_data = Aep.OutputModuleSettingsLdatBody(self._io, self, self._root)
            elif _on == Aep.LdatItemType.lrdr:
                pass
                self.kf_data = Aep.RenderSettingsLdatBody(self._io, self, self._root)
            elif _on == Aep.LdatItemType.marker:
                pass
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)
            elif _on == Aep.LdatItemType.no_value:
                pass
                self.kf_data = Aep.KfNoValue(self._io, self, self._root)
            elif _on == Aep.LdatItemType.one_d:
                pass
                self.kf_data = Aep.KfMultiDimensional(1, self._io, self, self._root)
            elif _on == Aep.LdatItemType.orientation:
                pass
                self.kf_data = Aep.KfMultiDimensional(1, self._io, self, self._root)
            elif _on == Aep.LdatItemType.three_d:
                pass
                self.kf_data = Aep.KfMultiDimensional(3, self._io, self, self._root)
            elif _on == Aep.LdatItemType.three_d_spatial:
                pass
                self.kf_data = Aep.KfPosition(3, self._io, self, self._root)
            elif _on == Aep.LdatItemType.two_d:
                pass
                self.kf_data = Aep.KfMultiDimensional(2, self._io, self, self._root)
            elif _on == Aep.LdatItemType.two_d_spatial:
                pass
                self.kf_data = Aep.KfPosition(2, self._io, self, self._root)
            elif _on == Aep.LdatItemType.unknown:
                pass
                self.kf_data = Aep.KfUnknownData(self._io, self, self._root)


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


    class LdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.LdtaBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.layer_id = self._io.read_u4be()
            self.quality = self._io.read_u2be()
            self._unnamed2 = self._io.read_bytes(2)
            self.stretch_dividend = self._io.read_s4be()
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
            self.stretch_divisor = self._io.read_u4be()
            self._unnamed46 = self._io.read_bytes(19)
            self.layer_type = KaitaiStream.resolve_enum(Aep.LayerType, self._io.read_u1())
            self.parent_id = self._io.read_u4be()
            self._unnamed49 = self._io.read_bytes(3)
            self.light_type = self._io.read_u1()
            self._unnamed51 = self._io.read_bytes(20)


        def _fetch_instances(self):
            pass

        @property
        def in_point(self):
            if hasattr(self, '_m_in_point'):
                return self._m_in_point

            self._m_in_point = (self.in_point_dividend * 1.0) / self.in_point_divisor
            return getattr(self, '_m_in_point', None)

        @property
        def out_point(self):
            if hasattr(self, '_m_out_point'):
                return self._m_out_point

            self._m_out_point = (self.out_point_dividend * 1.0) / self.out_point_divisor
            return getattr(self, '_m_out_point', None)

        @property
        def start_time(self):
            if hasattr(self, '_m_start_time'):
                return self._m_start_time

            self._m_start_time = (self.start_time_dividend * 1.0) / self.start_time_divisor
            return getattr(self, '_m_start_time', None)


    class Lhd3Body(KaitaiStruct):
        """Header for item/keyframe lists. AE reuses this structure for:
        - Property keyframes (count = keyframe count, item_size = keyframe data size)
        - Render queue items (count = item count, item_size = 2246 for settings)
        - Output module items (count = item count, item_size = 128 for settings)
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.Lhd3Body, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(10)
            self.count = self._io.read_u2be()
            self._unnamed2 = self._io.read_bytes(6)
            self.item_size = self._io.read_u2be()
            self._unnamed4 = self._io.read_bytes(3)
            self.item_type_raw = self._io.read_u1()


        def _fetch_instances(self):
            pass

        @property
        def item_type(self):
            if hasattr(self, '_m_item_type'):
                return self._m_item_type

            self._m_item_type = (Aep.LdatItemType.lrdr if  ((self.item_type_raw == 1) and (self.item_size == 2246))  else (Aep.LdatItemType.litm if  ((self.item_type_raw == 1) and (self.item_size == 128))  else (Aep.LdatItemType.gide if  ((self.item_type_raw == 2) and (self.item_size == 1))  else (Aep.LdatItemType.color if  ((self.item_type_raw == 4) and (self.item_size == 152))  else (Aep.LdatItemType.three_d if  ((self.item_type_raw == 4) and (self.item_size == 128))  else (Aep.LdatItemType.two_d_spatial if  ((self.item_type_raw == 4) and (self.item_size == 104))  else (Aep.LdatItemType.two_d if  ((self.item_type_raw == 4) and (self.item_size == 88))  else (Aep.LdatItemType.orientation if  ((self.item_type_raw == 4) and (self.item_size == 80))  else (Aep.LdatItemType.no_value if  ((self.item_type_raw == 4) and (self.item_size == 64))  else (Aep.LdatItemType.one_d if  ((self.item_type_raw == 4) and (self.item_size == 48))  else (Aep.LdatItemType.marker if  ((self.item_type_raw == 4) and (self.item_size == 16))  else Aep.LdatItemType.unknown)))))))))))
            return getattr(self, '_m_item_type', None)


    class ListBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.ListBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.list_type = (self._io.read_bytes(4)).decode(u"windows-1250")
            if self.list_type != u"btdk":
                pass
                self.chunks = []
                i = 0
                while not self._io.is_eof():
                    self.chunks.append(Aep.Chunk(self._io, self, self._root))
                    i += 1


            if self.list_type == u"btdk":
                pass
                self.binary_data = self._io.read_bytes_full()



        def _fetch_instances(self):
            pass
            if self.list_type != u"btdk":
                pass
                for i in range(len(self.chunks)):
                    pass
                    self.chunks[i]._fetch_instances()


            if self.list_type == u"btdk":
                pass



    class NmhdBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.NmhdBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

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


        def _fetch_instances(self):
            pass


    class NnhdBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.NnhdBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(8)
            self.feet_frames_film_type = self._io.read_bits_int_be(1) != 0
            self.time_display_type = self._io.read_bits_int_be(7)
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
            self.transparency_grid_thumbnails = self._io.read_u1()
            self._unnamed14 = self._io.read_bytes(5)
            self._unnamed15 = self._io.read_bits_int_be(2)
            self.linearize_working_space = self._io.read_bits_int_be(1) != 0
            self._unnamed17 = self._io.read_bits_int_be(5)
            self._unnamed18 = self._io.read_bytes(8)


        def _fetch_instances(self):
            pass


    class OptiBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.OptiBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

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

            if self.asset_type_int == 2:
                pass
                self._unnamed5 = self._io.read_bytes(4)

            if self.asset_type_int == 2:
                pass
                self.placeholder_name = (KaitaiStream.bytes_terminate(self._io.read_bytes_full(), 0, False)).decode(u"windows-1250")



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

            if self.asset_type_int == 2:
                pass

            if self.asset_type_int == 2:
                pass


        @property
        def alpha(self):
            if hasattr(self, '_m_alpha'):
                return self._m_alpha

            if self.asset_type == u"Soli":
                pass
                self._m_alpha = self.color[0]

            return getattr(self, '_m_alpha', None)

        @property
        def blue(self):
            if hasattr(self, '_m_blue'):
                return self._m_blue

            if self.asset_type == u"Soli":
                pass
                self._m_blue = self.color[3]

            return getattr(self, '_m_blue', None)

        @property
        def green(self):
            if hasattr(self, '_m_green'):
                return self._m_green

            if self.asset_type == u"Soli":
                pass
                self._m_green = self.color[2]

            return getattr(self, '_m_green', None)

        @property
        def red(self):
            if hasattr(self, '_m_red'):
                return self._m_red

            if self.asset_type == u"Soli":
                pass
                self._m_red = self.color[1]

            return getattr(self, '_m_red', None)


    class OutputModuleSettingsLdatBody(KaitaiStruct):
        """Per-output-module settings chunk (128 bytes).
        Used under LIST:list within LIST:LItm for each render queue item.
        Note: The actual comp_id is stored in render_settings_ldat_body, not here.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.OutputModuleSettingsLdatBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

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


        def _fetch_instances(self):
            pass


    class PardBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.PardBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

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


        @property
        def last_value_x(self):
            if hasattr(self, '_m_last_value_x'):
                return self._m_last_value_x

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                pass
                self._m_last_value_x = self.last_value_x_raw * (1.0 / 128 if self.property_control_type == Aep.PropertyControlType.two_d else 512)

            return getattr(self, '_m_last_value_x', None)

        @property
        def last_value_y(self):
            if hasattr(self, '_m_last_value_y'):
                return self._m_last_value_y

            if  ((self.property_control_type == Aep.PropertyControlType.two_d) or (self.property_control_type == Aep.PropertyControlType.three_d)) :
                pass
                self._m_last_value_y = self.last_value_y_raw * (1.0 / 128 if self.property_control_type == Aep.PropertyControlType.two_d else 512)

            return getattr(self, '_m_last_value_y', None)

        @property
        def last_value_z(self):
            if hasattr(self, '_m_last_value_z'):
                return self._m_last_value_z

            if self.property_control_type == Aep.PropertyControlType.three_d:
                pass
                self._m_last_value_z = self.last_value_z_raw * 512

            return getattr(self, '_m_last_value_z', None)


    class RenderSettingsLdatBody(KaitaiStruct):
        """Render settings ldat chunk (2246 bytes)."""
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.RenderSettingsLdatBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

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


        def _fetch_instances(self):
            pass

        @property
        def frame_rate(self):
            """Frame rate in fps (integer + fractional)."""
            if hasattr(self, '_m_frame_rate'):
                return self._m_frame_rate

            self._m_frame_rate = self.frame_rate_integer + (self.frame_rate_fractional * 1.0) / 65536
            return getattr(self, '_m_frame_rate', None)

        @property
        def time_span_duration(self):
            """Time span duration in seconds."""
            if hasattr(self, '_m_time_span_duration'):
                return self._m_time_span_duration

            self._m_time_span_duration = ((self.time_span_duration_frames * 1.0) / self.time_span_duration_timebase if self.time_span_duration_timebase != 0 else 0)
            return getattr(self, '_m_time_span_duration', None)

        @property
        def time_span_start(self):
            """Time span start in seconds."""
            if hasattr(self, '_m_time_span_start'):
                return self._m_time_span_start

            self._m_time_span_start = ((self.time_span_start_frames * 1.0) / self.time_span_start_timebase if self.time_span_start_timebase != 0 else 0)
            return getattr(self, '_m_time_span_start', None)


    class RoouBody(KaitaiStruct):
        """Output module settings (154 bytes)."""
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.RoouBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

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
            self.remaining = self._io.read_bytes_full()


        def _fetch_instances(self):
            pass

        @property
        def output_audio(self):
            if hasattr(self, '_m_output_audio'):
                return self._m_output_audio

            self._m_output_audio = self.audio_disabled_hi != 255
            return getattr(self, '_m_output_audio', None)

        @property
        def video_output(self):
            """True when video output is enabled (width or height non-zero)."""
            if hasattr(self, '_m_video_output'):
                return self._m_video_output

            self._m_video_output =  ((self.width > 0) or (self.height > 0)) 
            return getattr(self, '_m_video_output', None)


    class RoutBody(KaitaiStruct):
        """Render queue item flags (4-byte header + 4 bytes per item)."""
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.RoutBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(4)
            self.items = []
            i = 0
            while not self._io.is_eof():
                self.items.append(Aep.RoutItem(self._io, self, self._root))
                i += 1



        def _fetch_instances(self):
            pass
            for i in range(len(self.items)):
                pass
                self.items[i]._fetch_instances()



    class RoutItem(KaitaiStruct):
        """Per-item render queue flags (4 bytes)."""
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.RoutItem, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bits_int_be(1) != 0
            self.render = self._io.read_bits_int_be(1) != 0
            self._unnamed2 = self._io.read_bits_int_be(6)
            self._unnamed3 = self._io.read_bytes(3)


        def _fetch_instances(self):
            pass


    class SspcBody(KaitaiStruct):
        """Source footage settings chunk. Contains dimension, timing, and alpha/field settings.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.SspcBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
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


        def _fetch_instances(self):
            pass

        @property
        def duration(self):
            if hasattr(self, '_m_duration'):
                return self._m_duration

            self._m_duration = (self.duration_dividend * 1.0) / self.duration_divisor
            return getattr(self, '_m_duration', None)

        @property
        def frame_duration(self):
            if hasattr(self, '_m_frame_duration'):
                return self._m_frame_duration

            self._m_frame_duration = self.duration * self.frame_rate
            return getattr(self, '_m_frame_duration', None)

        @property
        def frame_rate(self):
            if hasattr(self, '_m_frame_rate'):
                return self._m_frame_rate

            self._m_frame_rate = self.frame_rate_base + (self.frame_rate_fractional * 1.0) / 65536
            return getattr(self, '_m_frame_rate', None)

        @property
        def has_alpha(self):
            """True if footage has an alpha channel (3 means no_alpha)."""
            if hasattr(self, '_m_has_alpha'):
                return self._m_has_alpha

            self._m_has_alpha = self.alpha_mode_raw != 3
            return getattr(self, '_m_has_alpha', None)

        @property
        def pixel_aspect(self):
            if hasattr(self, '_m_pixel_aspect'):
                return self._m_pixel_aspect

            self._m_pixel_aspect = (self.pixel_ratio_width * 1.0) / self.pixel_ratio_height
            return getattr(self, '_m_pixel_aspect', None)


    class Tdb4Body(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.Tdb4Body, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

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


        def _fetch_instances(self):
            pass
            for i in range(len(self.unknown_floats)):
                pass

            for i in range(len(self.unknown_floats_2)):
                pass


        @property
        def expression_enabled(self):
            if hasattr(self, '_m_expression_enabled'):
                return self._m_expression_enabled

            self._m_expression_enabled = (not (self.expression_disabled))
            return getattr(self, '_m_expression_enabled', None)


    class TdsbBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.TdsbBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self._unnamed0 = self._io.read_bytes(2)
            self._unnamed1 = self._io.read_bits_int_be(3)
            self.locked_ratio = self._io.read_bits_int_be(1) != 0
            self._unnamed3 = self._io.read_bits_int_be(4)
            self._unnamed4 = self._io.read_bits_int_be(6)
            self.dimensions_separated = self._io.read_bits_int_be(1) != 0
            self.enabled = self._io.read_bits_int_be(1) != 0


        def _fetch_instances(self):
            pass


    class Utf8Body(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Aep.Utf8Body, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.contents = (self._io.read_bytes_full()).decode(u"UTF-8")


        def _fetch_instances(self):
            pass



