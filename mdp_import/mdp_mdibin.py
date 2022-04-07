import io
import logging
from typing import BinaryIO, Dict

from .mdp_archive import MdpArchive

class MdpMdiBin:
    @staticmethod
    def read(device: BinaryIO, mdibinSize: int) -> Dict[str, MdpArchive]:
        mdiBinBytes = device.read(mdibinSize)
        if len(mdiBinBytes) != mdibinSize:
            raise BufferError("Could not read mdibin: not enough bytes")

        mdiBin = {}
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
