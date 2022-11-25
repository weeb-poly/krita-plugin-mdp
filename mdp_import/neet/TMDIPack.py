import struct
from typing import BinaryIO


MDIPACK_SIG = b"mdipack"
MDIPACK_VER = 0


class TMDIPack:
    signature: bytes
    version: int
    mdiSize: int
    mdibinSize: int

    _TMDIPack = struct.Struct("<7sxLLL")

    def __init__(self) -> None:
        return

    @classmethod
    def read(cls, device: BinaryIO):
        this = cls()
        this._read(device)
        return this

    def _read(self, device: BinaryIO) -> None:
        cls = self.__class__
        headerBytes = device.read(cls._TMDIPack.size)
        if len(headerBytes) != cls._TMDIPack.size:
            raise BufferError("Could not read header: not enough bytes")

        header = cls._TMDIPack.unpack(headerBytes)
        (self.signature, self.version, self.mdiSize, self.mdibinSize) = header

        return self._valid()

    def _valid(self) -> None:
        assert self.signature == MDIPACK_SIG, f"Not a MDIPACK document. Signature is: {self.signature}"
        assert self.version == MDIPACK_VER, f"Unsupported MDIPACK version: {self.version}"
