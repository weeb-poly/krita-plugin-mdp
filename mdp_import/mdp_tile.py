from typing import Optional
import struct
import zlib
from io import BufferedReader

MdpTileHeader = struct.Struct("<IIII")

class MdpTile:
    col: str
    row: int
    ctype: Optional[int]
    data: bytes

    def __init__(self) -> None:
        return

    @classmethod
    def read(cls, device: BufferedReader):
        this = cls()
        this._read(device)
        this._decompress()
        return this

    def _read(self, device: BufferedReader) -> None:
        headerBytes = device.read(MdpTileHeader.size)
        if len(headerBytes) != MdpTileHeader.size:
            raise BufferError("Could not read tile header: not enough bytes")

        header = MdpTileHeader.unpack(headerBytes)
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
            except Exception:
                raise Exception("Could not decompress tile: zlib error")
        elif self.ctype == 1: # snappy
            # The easiest way to do this without breaking Krita is to find
            # a Pure Python implementation of snappy
            # https://github.com/ethereum/py-snappy
            raise Exception("Could not decompress tile: snappy not supported")
        elif self.ctype == 2: # FastLZ
            # The easiest way to do this without breaking Krita is to find
            # a Pure Python implementation of FastLZ
            # 
            raise Exception("Could not decompress tile: FastLZ not supported")
        else:
            # Unknown Compression Type
            assert False, f"Unknown Tile Compression Type '{self.ctype}'"

        # Data has been decompressed successfully
        self.ctype = None
