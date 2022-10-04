# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Aep(KaitaiStruct):

    class ChunkType(Enum):
        acsi = 1094939497
        afsi = 1095136105
        arsi = 1095922537
        cptm = 1129337965
        croi = 1129467721
        capl = 1130459212
        ccct = 1130578804
        cprc = 1131442755
        csct = 1131627380
        lst = 1279873876
        rhed = 1382573412
        rout = 1383036276
        utf8 = 1433691704
        acer = 1633903986
        adfr = 1633969778
        cdat = 1667522932
        cdrp = 1667527280
        cdta = 1667527777
        cmta = 1668117601
        cpid = 1668311396
        dwga = 1685546849
        fcid = 1717791076
        fdta = 1717859425
        fiac = 1718182243
        fidi = 1718183017
        fifl = 1718183532
        fimr = 1718185330
        fiop = 1718185840
        fipc = 1718186083
        fipl = 1718186092
        fips = 1718186099
        fits = 1718187123
        fitt = 1718187124
        fivc = 1718187619
        fivi = 1718187625
        foac = 1718575459
        fots = 1718580339
        fott = 1718580340
        fovc = 1718580835
        fovi = 1718580841
        ftts = 1718908019
        ftwd = 1718908772
        fvdv = 1719034998
        gdta = 1734636641
        head = 1751474532
        idta = 1768191073
        ldta = 1818522721
        lhd3 = 1818780723
        nhed = 1852335460
        nnhd = 1852729444
        nums = 1853189459
        oacc = 1868653411
        opti = 1869640809
        otln = 1869900910
        prda = 1886544993
        prin = 1886546286
        qtlg = 1903455335
        seq = 1936027936
        sfid = 1936091492
        sspc = 1936945251
        svap = 1937138032
        tdb4 = 1952735796
        tdgp = 1952737136
        tdmn = 1952738670
        tdsb = 1952740194
        tdsn = 1952740206
        tdum = 1952740717
        wsnm = 2004053613
        wsns = 2004053619

    class Depth(Enum):
        bpc_8 = 0
        bpc_16 = 1
        bpc_32 = 2

    class FootageType(Enum):
        placeholder = 2
        solid = 9

    class ItemType(Enum):
        folder = 1
        composition = 4
        footage = 7
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic1 = self._io.read_bytes(4)
        if not self.magic1 == b"\x52\x49\x46\x58":
            raise kaitaistruct.ValidationNotEqualError(b"\x52\x49\x46\x58", self.magic1, self._io, u"/seq/0")
        self.file_size = self._io.read_u4be()
        self.magic2 = self._io.read_bytes(4)
        if not self.magic2 == b"\x45\x67\x67\x21":
            raise kaitaistruct.ValidationNotEqualError(b"\x45\x67\x67\x21", self.magic2, self._io, u"/seq/2")
        self._raw_data = self._io.read_bytes((self.file_size - 4))
        _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
        self.data = Aep.Blocks(_io__raw_data, self, self._root)

    class ListBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.identifier = (self._io.read_bytes(4)).decode(u"cp1252")
            self.blocks = Aep.Blocks(self._io, self, self._root)


    class CdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown01 = self._io.read_bytes(4)
            self.framerate_divisor = self._io.read_u4be()
            self.framerate_dividend = self._io.read_u4be()
            self.unknown02 = self._io.read_bytes(32)
            self.seconds_dividend = self._io.read_u4be()
            self.seconds_divisor = self._io.read_u4be()
            self.background_color = (self._io.read_bytes(3)).decode(u"cp1252")
            self.unknown03 = self._io.read_bytes(85)
            self.width = self._io.read_u2be()
            self.height = self._io.read_u2be()
            self.unknown04 = self._io.read_bytes(12)
            self.frame_rate = self._io.read_u2be()


    class FdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown01 = self._io.read_bytes(1)


    class Blocks(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.blocks = []
            i = 0
            while not self._io.is_eof():
                self.blocks.append(Aep.Block(self._io, self, self._root))
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


    class SspcBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown01 = self._io.read_bytes(30)
            self.width = self._io.read_u4be()
            self.height = self._io.read_u4be()
            self.seconds_dividend = self._io.read_u4be()
            self.seconds_divisor = self._io.read_u4be()
            self.unknown02 = self._io.read_bytes(10)
            self.framerate = self._io.read_u4be()
            self.framerate_dividend = self._io.read_u2be()


    class OptiBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown01 = self._io.read_bytes(4)
            self.footage_type = KaitaiStream.resolve_enum(Aep.FootageType, self._io.read_u2be())
            self.unknown02 = self._io.read_bytes((20 if self.footage_type == Aep.FootageType.solid else 4))
            self.name = (self._io.read_bytes((229 if self.footage_type == Aep.FootageType.solid else 245))).decode(u"cp1252")


    class Block(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.block_type = KaitaiStream.resolve_enum(Aep.ChunkType, self._io.read_u4be())
            self.block_size = self._io.read_u4be()
            _on = self.block_type
            if _on == Aep.ChunkType.fdta:
                self._raw_data = self._io.read_bytes(self.block_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.FdtaBody(_io__raw_data, self, self._root)
            elif _on == Aep.ChunkType.opti:
                self._raw_data = self._io.read_bytes(self.block_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.OptiBody(_io__raw_data, self, self._root)
            elif _on == Aep.ChunkType.sspc:
                self._raw_data = self._io.read_bytes(self.block_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.SspcBody(_io__raw_data, self, self._root)
            elif _on == Aep.ChunkType.ldta:
                self._raw_data = self._io.read_bytes(self.block_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.LdtaBody(_io__raw_data, self, self._root)
            elif _on == Aep.ChunkType.cmta:
                self._raw_data = self._io.read_bytes(self.block_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == Aep.ChunkType.lst:
                self._raw_data = self._io.read_bytes(self.block_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.ListBody(_io__raw_data, self, self._root)
            elif _on == Aep.ChunkType.utf8:
                self._raw_data = self._io.read_bytes(self.block_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.Utf8Body(_io__raw_data, self, self._root)
            elif _on == Aep.ChunkType.idta:
                self._raw_data = self._io.read_bytes(self.block_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.IdtaBody(_io__raw_data, self, self._root)
            elif _on == Aep.ChunkType.nhed:
                self._raw_data = self._io.read_bytes(self.block_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.NhedBody(_io__raw_data, self, self._root)
            elif _on == Aep.ChunkType.cdta:
                self._raw_data = self._io.read_bytes(self.block_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.CdtaBody(_io__raw_data, self, self._root)
            else:
                self._raw_data = self._io.read_bytes(self.block_size)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Aep.AsciiBody(_io__raw_data, self, self._root)
            if (self.block_size % 2) != 0:
                self.padding = self._io.read_u1()



    class NhedBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown01 = self._io.read_bytes(15)
            self.depth = KaitaiStream.resolve_enum(Aep.Depth, self._io.read_u2be())


    class AsciiBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_bytes_full()


    class LdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown01 = self._io.read_bytes(4)
            self.quality = self._io.read_u2be()
            self.unknown02 = self._io.read_bytes(31)
            self.layer_attr_bits = self._io.read_bytes(3)
            self.source_id = self._io.read_u4be()

        @property
        def guide_enabled(self):
            if hasattr(self, '_m_guide_enabled'):
                return self._m_guide_enabled

            self._m_guide_enabled = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 0) & (1 << 1)) >> 1) == 1
            return getattr(self, '_m_guide_enabled', None)

        @property
        def frame_blend_enabled(self):
            if hasattr(self, '_m_frame_blend_enabled'):
                return self._m_frame_blend_enabled

            self._m_frame_blend_enabled = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 2) & (1 << 4)) >> 4) == 1
            return getattr(self, '_m_frame_blend_enabled', None)

        @property
        def video_enabled(self):
            if hasattr(self, '_m_video_enabled'):
                return self._m_video_enabled

            self._m_video_enabled = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 2) & (1 << 0)) >> 0) == 1
            return getattr(self, '_m_video_enabled', None)

        @property
        def motion_blur_enabled(self):
            if hasattr(self, '_m_motion_blur_enabled'):
                return self._m_motion_blur_enabled

            self._m_motion_blur_enabled = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 2) & (1 << 3)) >> 3) == 1
            return getattr(self, '_m_motion_blur_enabled', None)

        @property
        def effects_enabled(self):
            if hasattr(self, '_m_effects_enabled'):
                return self._m_effects_enabled

            self._m_effects_enabled = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 2) & (1 << 2)) >> 2) == 1
            return getattr(self, '_m_effects_enabled', None)

        @property
        def solo_enabled(self):
            if hasattr(self, '_m_solo_enabled'):
                return self._m_solo_enabled

            self._m_solo_enabled = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 1) & (1 << 3)) >> 3) == 1
            return getattr(self, '_m_solo_enabled', None)

        @property
        def lock_enabled(self):
            if hasattr(self, '_m_lock_enabled'):
                return self._m_lock_enabled

            self._m_lock_enabled = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 2) & (1 << 5)) >> 5) == 1
            return getattr(self, '_m_lock_enabled', None)

        @property
        def three_d_enabled(self):
            if hasattr(self, '_m_three_d_enabled'):
                return self._m_three_d_enabled

            self._m_three_d_enabled = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 1) & (1 << 2)) >> 2) == 1
            return getattr(self, '_m_three_d_enabled', None)

        @property
        def collapse_transform_enabled(self):
            if hasattr(self, '_m_collapse_transform_enabled'):
                return self._m_collapse_transform_enabled

            self._m_collapse_transform_enabled = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 2) & (1 << 7)) >> 7) == 1
            return getattr(self, '_m_collapse_transform_enabled', None)

        @property
        def frame_blend_mode(self):
            if hasattr(self, '_m_frame_blend_mode'):
                return self._m_frame_blend_mode

            self._m_frame_blend_mode = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 0) & (1 << 2)) >> 2)
            return getattr(self, '_m_frame_blend_mode', None)

        @property
        def adjustment_layer_enabled(self):
            if hasattr(self, '_m_adjustment_layer_enabled'):
                return self._m_adjustment_layer_enabled

            self._m_adjustment_layer_enabled = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 1) & (1 << 1)) >> 1) == 1
            return getattr(self, '_m_adjustment_layer_enabled', None)

        @property
        def shy_enabled(self):
            if hasattr(self, '_m_shy_enabled'):
                return self._m_shy_enabled

            self._m_shy_enabled = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 2) & (1 << 6)) >> 6) == 1
            return getattr(self, '_m_shy_enabled', None)

        @property
        def sampling_mode(self):
            if hasattr(self, '_m_sampling_mode'):
                return self._m_sampling_mode

            self._m_sampling_mode = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 0) & (1 << 6)) >> 6)
            return getattr(self, '_m_sampling_mode', None)

        @property
        def audio_enabled(self):
            if hasattr(self, '_m_audio_enabled'):
                return self._m_audio_enabled

            self._m_audio_enabled = ((KaitaiStream.byte_array_index(self.layer_attr_bits, 2) & (1 << 1)) >> 1) == 1
            return getattr(self, '_m_audio_enabled', None)



