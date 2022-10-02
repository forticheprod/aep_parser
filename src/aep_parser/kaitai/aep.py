# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))


class Aep(KaitaiStruct):
    class ChunkType(Enum):
        lst = 1279873876
        utf8 = 1433691704
        cdta = 1667527777
        cmta = 1668117601
        fdta = 1717859425
        idta = 1768191073
        nhed = 1852335460

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
            self.identifier = (self._io.read_bytes(4)).decode(u"ascii")
            self.entries = Aep.Blocks(self._io, self, self._root)

    class CdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown01 = (self._io.read_bytes(140)).decode(u"ascii")
            self.width = self._io.read_u2be()
            self.height = self._io.read_u2be()
            self.unknown02 = (self._io.read_bytes(12)).decode(u"ascii")
            self.frame_rate = self._io.read_u2be()

    class FdtaBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown01 = (self._io.read_bytes(1)).decode(u"ascii")

    class Blocks(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.entries = []
            i = 0
            while not self._io.is_eof():
                self.entries.append(Aep.Block(self._io, self, self._root))
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
            self.unknown01 = (self._io.read_bytes(18)).decode(u"ascii")
            self.id = self._io.read_u2be()

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
            self.unknown01 = (self._io.read_bytes(30)).decode(u"latin-1")
            self.data = self._io.read_u2be()

    class AsciiBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = (self._io.read_bytes_full()).decode(u"latin-1")
