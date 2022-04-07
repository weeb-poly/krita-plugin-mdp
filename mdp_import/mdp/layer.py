import io
import struct
from typing import BinaryIO, List, Optional
from xml.etree.ElementTree import Element
from distutils.util import strtobool

from krita import Node as KritaNode

from .archive import MdpArchive
from .tile import MdpTile
from .utils import fillNodeWithTiles


class MdpLayer:
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
    kritaNode: KritaNode

    tiles: List[MdpTile]

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

    def decodeArchive(self, archive: MdpArchive) -> None:
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
            tile = MdpTile.read(device)
            self.tiles.append(tile)

    def createKritaNode(self, doc) -> KritaNode:
        if self.layerType == "folder":
            self.kritaNode = doc.createGroupLayer(self.layerName)
        elif self.layerType in ("32bpp", "8bpp", "1bpp",):
            self.kritaNode = doc.createNode(self.layerName, "paintLayer")

        # TODO: Use some sort of filter or mask for 8bpp and 1bpp nodes
        # This would fix the layerColor issue as well as allow
        # This would allow for 8bpp and 1bpp layers to be set to GRAYA
        # if self.layerType in ("8bpp", "1bpp",):
        #     self.kritaNode.setColorSpace("GRAYA", "U8", "")

        # TODO: Figure out how to programmatically add the halftone filter
        # https://docs.krita.org/en/reference_manual/filters/artistic.html#halftone

        if self.visible is not None:
            self.kritaNode.setVisible(self.visible)
        if self.alpha is not None:
            self.kritaNode.setOpacity(self.alpha)
        if self.protectAlpha is not None:
            self.kritaNode.setAlphaLocked(self.protectAlpha)
        if self.locked is not None:
            self.kritaNode.setLocked(self.locked)

        if self.layerType == "folder":
            folderOpen = strtobool(self.xmlEl.attrib.get('folderOpen'))
            if folderOpen is not None:
                self.kritaNode.setCollapsed(not folderOpen)

        return self.kritaNode

    def setKritaPixels(self) -> None:
        # TODO: Handle 8bpp and 1bpp layer colors using masks

        layerColor = self.xmlEl.get('color')

        fillNodeWithTiles(self.kritaNode, self.tiles, self.layerType, self.tileDim, layerColor)

        self.kritaNode.move(self.ofsx, self.ofsy)
