import io
import struct
from typing import BinaryIO, List, Optional
from xml.etree.ElementTree import Element
from distutils.util import strtobool

from .CPackerArchive import CPackerArchive
from .CImageTile import CImageTile

class CMangaLayer:
    tileDim: int

    id: str
    layerType: str
    layerName: str
    archiveName: str
    parentId: str
    alpha: int
    visible: bool
    locked: bool
    ofsx: int
    ofsy: int
    width: int
    height: int

    xmlEl: Element

    tiles: List[CImageTile]

    def __init__(self, xmlEl: Optional[Element] = None) -> None:
        self.xmlEl = xmlEl
        self.kritaNode = None
        if self.xmlEl is not None:
            self._parseXml()
            self._validXml()

    def _parseXml(self) -> None:
        self.id = self.xmlEl.attrib.get('id')
        self.layerType = self.xmlEl.attrib.get('type')
        self.layerName = self.xmlEl.attrib.get('name')
        self.archiveName = self.xmlEl.attrib.get('bin')
        self.parentId = self.xmlEl.attrib.get('parentId')
        self.alpha = int(self.xmlEl.attrib.get('alpha', '255'))
        self.visible = strtobool(self.xmlEl.attrib.get('visible'))
        self.protectAlpha = strtobool(self.xmlEl.attrib.get('protectAlpha'))
        self.locked = strtobool(self.xmlEl.attrib.get('locked'))
        self.ofsx = int(self.xmlEl.attrib.get('ofsx', '0'))
        self.ofsy = int(self.xmlEl.attrib.get('ofsy', '0'))
        self.width = int(self.xmlEl.get('width'))
        self.height = int(self.xmlEl.get('height'))

    def _validXml(self) -> None:
        binType = self.xmlEl.attrib.get('binType')
        assert binType == "2", f"Unsupported Layer binType: {binType}"

    def decodeArchive(self, archive: CPackerArchive) -> None:
        with io.BytesIO(archive.archiveData) as archiveIo:
            self._readBuffer(archiveIo)

    def _readBuffer(self, device: BinaryIO) -> None:
        tileNum = struct.unpack('<I', device.read(4))[0]

        # If tileNum is zero, no other data is stored
        # This means that trying to read tileDim will
        # cause an error
        tileDim = -1
        if tileNum != 0:
            tileDim = struct.unpack('<I', device.read(4))[0]

        self.tileDim = tileDim
        self.tiles = []

        for _ in range(tileNum):
            tile = CImageTile.read(device)
            self.tiles.append(tile)
