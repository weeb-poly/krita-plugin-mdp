from typing import BinaryIO, List, Optional
from distutils.util import strtobool
import xml.etree.ElementTree as ET

from PyQt5.QtGui import QColor

from ..layer import MdpLayer

class MdpMdi:
    el: ET.Element

    @classmethod
    def read(cls, device: BinaryIO, mdiSize: int):
        this = cls()
        mdiBytes = device.read(mdiSize)
        if len(mdiBytes) != mdiSize:
            raise BufferError("Could not read mdi string: not enough bytes")
        this.el = ET.fromstring(mdiBytes.decode('utf8'))
        return this

    def width(self) -> int:
        return int(self.el.attrib.get('width'))

    def height(self) -> int:
        return int(self.el.attrib.get('height'))

    def dpi(self) -> int:
        return int(self.el.attrib.get('dpi'))

    def icc(self) -> str:
        icc_xml = self.el.find('./ICCProfiles')
        if icc_xml is None:
            return ""

        icc_enabled = strtobool(icc_xml.attrib.get('enabled', 'False'))
        if icc_enabled is not True:
            return ""

        # TODO: Extract icc profile from xml
        doc_icc = ""

        return doc_icc

    def bgColor(self) -> Optional[QColor]:
        doc_bg = (
            self.el.get('bgColorR'),
            self.el.get('bgColorG'),
            self.el.get('bgColorB'),
        )

        if None in doc_bg:
            return None
        
        return QColor(int(doc_bg[0]), int(doc_bg[1]), int(doc_bg[2]))

    def activeLayerId(self) -> Optional[str]:
        layersEl = self.el.find('./Layers')
        return layersEl.attrib.get('active')

    def layers(self) -> List[MdpLayer]:
        # This layer ordering seems to match up with how
        # Krita does things (lowest layer first),
        # so I'm just going to leave it as is.

        layers = []
        for layerEl in self.el.iterfind('./Layers/Layer'):
            l = MdpLayer(layerEl)
            layers.append(l)

        return layers