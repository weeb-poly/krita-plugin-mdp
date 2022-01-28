import logging
from io import BytesIO, BufferedReader
from typing import Dict

from .mdp_archive import MdpArchive

class MdpMdiBin:
    @staticmethod
    def read(device: BufferedReader, mdibinSize: int) -> Dict[str, MdpArchive]:
        mdiBinBytes = device.read(mdibinSize)
        if len(mdiBinBytes) != mdibinSize:
            raise BufferError("Could not read mdibin: not enough bytes")
    
        mdiBin = {}
        bytesRead = 0
        with BytesIO(mdiBinBytes) as _mdiBinIo:
            with BufferedReader(_mdiBinIo) as mdiBinIo:
                while bytesRead < mdibinSize:
                    try:
                        archive = MdpArchive.read(mdiBinIo)
                        mdiBin[archive.archiveName] = archive
                        bytesRead += archive.chunkSize
                    except Exception:
                        raise Exception("failed reading mdibin archive")

                    logging.debug("Read archive from mdibin. pos: %i", mdiBinIo.tell())

        return mdiBin
