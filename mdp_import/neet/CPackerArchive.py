import struct
from typing import BinaryIO
import zlib

MDIPAC_ARC_SIG = b"PAC "

PAC_MAX_NAME = 64
PAC_RESERVED = 48

TPackerHeader = struct.Struct(f"<4sLLLL{PAC_RESERVED}x{PAC_MAX_NAME}s")

class CPackerArchive:
    signature: bytes
    chunkSize: int
    streamType: int
    streamSize: int
    archiveSize: str
    archiveName: str

    archiveData: bytes

    def __init__(self) -> None:
        return

    @classmethod
    def read(cls, device: BinaryIO):
        this = cls()
        this._read(device)
        this._decompress()
        this._valid()
        return this

    def _read(self, device: BinaryIO) -> None:
        headerBytes = device.read(TPackerHeader.size)
        if len(headerBytes) != TPackerHeader.size:
            raise BufferError("Could not read archive header: not enough bytes")

        header = TPackerHeader.unpack(headerBytes)
        (self.signature, self.chunkSize, self.streamType, self.streamSize, self.archiveSize, archiveName) = header

        #archiveName.truncate(archiveName.indexOf(QChar::Null));
        self.archiveName = archiveName.rstrip(b'\0').decode('utf8')

        streamData = device.read(self.streamSize)
        if len(streamData) != self.streamSize:
            raise BufferError("Could not read archive: not enough bytes")

        self.archiveData = streamData

    def _decompress(self) -> None:
        if self.streamType == 0: # COMP_NONE
            return
        elif self.streamType == 1: # COMP_ZLIB
            streamData = self.archiveData
            self.archiveData = zlib.decompress(streamData, bufsize=self.archiveSize)
        else: # unknown
            assert False, f"Unknown streamType Code: {self.streamType}"

        # Change streamType so we don't accidentally decompress twice
        self.streamType = 0

    def _valid(self) -> None:
        assert self.signature == MDIPAC_ARC_SIG, \
            f"Not a MDIBIN document. Signature is: {self.signature}"
        assert (self.chunkSize - TPackerHeader.size) == self.streamSize, \
            f"stream size ({(self.chunkSize - TPackerHeader.size)}) doesn't match streamSize ({self.streamSize})"
        assert len(self.archiveData) == self.archiveSize, \
            f"archive size {len(self.archiveData)} doesn't match archiveSize {self.archiveSize}"
