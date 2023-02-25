import logging
from typing import BinaryIO

from .CMangaFileMDB import CMangaFileMDB
from .CMangaFileMDI import CMangaFileMDI
from .TMDIPack import TMDIPack


class CMangaFileMDP:
    header: TMDIPack
    mdi: CMangaFileMDI
    mdb: CMangaFileMDB

    def __init__(self) -> None:
        return

    @classmethod
    def read(cls, device: BinaryIO):
        this = cls()
        this._read(device)
        return this

    def _read(self, device: BinaryIO) -> None:
        logging.debug('pos: %i', device.tell())

        try:
            self.header = TMDIPack.read(device)
        except Exception:
            raise Exception("failed reading header")

        logging.debug("Read header. pos: %i", device.tell())

        try:
            self.mdi = CMangaFileMDI.read(device, self.header.mdiSize)
        except Exception:
            raise Exception("failed reading mdi xml")

        logging.debug("Read mdi xml. pos: %i", device.tell())

        self.mdb = CMangaFileMDB.read(device, self.header.mdibinSize)

        logging.debug("Read mdibin section. pos: %i", device.tell())
