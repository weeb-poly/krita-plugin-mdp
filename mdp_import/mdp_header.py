import struct
from typing import BinaryIO

MDIPACK_SIG = b"mdipack"
MDIPACK_VER = 0

TMDIPack = struct.Struct("<7sxLLL")

class MdpHeader:
    signature: bytes
    version: int
    mdiSize: int
    mdibinSize: int

    def __init__(self) -> None:
        return

    @classmethod
    def read(cls, device: BinaryIO):
        this = cls()
        this._read(device)
        return this

    def _read(self, device: BinaryIO) -> None:
        headerBytes = device.read(TMDIPack.size)
        if len(headerBytes) != TMDIPack.size:
            raise BufferError("Could not read header: not enough bytes")

        header = TMDIPack.unpack(headerBytes)
        (self.signature, self.version, self.mdiSize, self.mdibinSize) = header

        return self._valid()

    def _valid(self) -> None:
        assert self.signature == MDIPACK_SIG, f"Not a MDIPACK document. Signature is: {self.signature}"
        assert self.version == MDIPACK_VER, f"Unsupported MDIPACK version: {self.version}"
