import io
import logging
from typing import BinaryIO, Dict

from .archive import MdpArchive

class MdpMdiBin(dict, Dict[str, MdpArchive]):
    @staticmethod
    def read(device: BinaryIO, mdibinSize: int) -> 'MdpMdiBin':
        mdiBinBytes = device.read(mdibinSize)
        if len(mdiBinBytes) != mdibinSize:
            raise BufferError("Could not read mdibin: not enough bytes")

        mdiBin = MdpMdiBin()
        bytesRead = 0
        with io.BytesIO(mdiBinBytes) as mdiBinIo:
            while bytesRead < mdibinSize:
                try:
                    archive = MdpArchive.read(mdiBinIo)
                    mdiBin[archive.archiveName] = archive
                    bytesRead += archive.chunkSize
                except Exception as e:
                    raise Exception("failed reading mdibin archive") from e

                logging.debug("Read archive from mdibin. pos: %i", mdiBinIo.tell())

        return mdiBin
