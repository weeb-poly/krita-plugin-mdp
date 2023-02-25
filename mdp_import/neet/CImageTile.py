from typing import BinaryIO, Optional
import struct
import zlib

try:
    import py_snappy as snappy
except ImportError:
    pass

try:
    import py_fastlz as fastlz
except ImportError:
    pass


class CImageTile:
    col: str
    row: int
    ctype: Optional[int]
    data: bytes

    _HeaderStruct = struct.Struct("<IIII")

    def __init__(self) -> None:
        return

    @classmethod
    def read(cls, device: BinaryIO):
        this = cls()
        this._read(device)
        this._decompress()
        return this

    def _read(self, device: BinaryIO) -> None:
        cls = self.__class__
        headerBytes = device.read(cls._HeaderStruct.size)
        if len(headerBytes) != cls._HeaderStruct.size:
            raise BufferError("Could not read tile header: not enough bytes")

        header = cls._HeaderStruct.unpack(headerBytes)
        (self.col, self.row, self.ctype, size) = header

        cdata = device.read(size)
        if len(cdata) != size:
            raise BufferError("Could not read tile data: not enough bytes")

        self.data = cdata

        # Byte Alignment
        device.seek((4 - size) % 4, 1)

    def _decompress(self) -> None:
        # Check if data has been decompressed already
        if self.ctype is None:
            return

        cdata = self.data

        if self.ctype == 0: # zlib
            try:
                self.data = zlib.decompress(cdata)
            except Exception as e:
                raise Exception("Could not decompress tile: zlib error") from e
        elif self.ctype == 1: # snappy
            try:
                self.data = snappy.decompress(cdata)
            except Exception as e:
                raise Exception("Could not decompress tile: py_snappy error") from e
            raise Exception("Could not decompress tile: snappy not supported")
        elif self.ctype == 2: # FastLZ
            try:
                self.data = fastlz.decompress(cdata)
            except Exception as e:
                raise Exception("Could not decompress tile: py_fastlz error") from e
            raise Exception("Could not decompress tile: FastLZ not supported")
        else:
            # Unknown Compression Type
            assert False, f"Unknown Tile Compression Type '{self.ctype}'"

        # Data has been decompressed successfully
        self.ctype = None
