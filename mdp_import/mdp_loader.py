import logging
from typing import Dict
from io import BufferedReader

from krita import Krita, Document

from .mdp_header import MdpHeader
from .mdp_mdi import MdpMdi
from .mdp_mdibin import MdpMdiBin
from .mdp_archive import MdpArchive

class MdpLoader:
    m_doc: Document
    mdp_mdi: MdpMdi
    mdp_mdibin: Dict[str, MdpArchive]

    def __init__(self) -> None:
        self.m_doc = None
        self.mdp_mdi = None
        self.mdp_mdibin = None

    def buildDoc(self, io: BufferedReader, krita: Krita) -> Document:
        self._read(io)
        self._decode(krita)
        return self.m_doc

    def _read(self, io: BufferedReader) -> None:
        logging.debug('pos: %i', io.tell())

        try:
            header = MdpHeader.read(io)
        except Exception:
            raise Exception("failed reading header")

        logging.debug(header)
        logging.debug("Read header. pos: %i", io.tell())

        try:
            self.mdp_mdi = MdpMdi.read(io, header.mdiSize)
        except Exception:
            raise Exception("failed reading mdi xml")

        logging.debug(self.mdp_mdi)
        logging.debug("Read mdi xml. pos: %i", io.tell())

        self.mdp_mdibin = MdpMdiBin.read(io, header.mdibinSize)

        logging.debug("Read mdibin section. pos: %i", io.tell())

    def _decode(self, krita: Krita) -> None:
        doc_width = self.mdp_mdi.width()
        doc_height = self.mdp_mdi.height()

        doc_icc = self.mdp_mdi.icc()

        # NOTE: Assuming 1ppi = 1dpi
        doc_ppi = self.mdp_mdi.dpi()

        self.m_doc = krita.createDocument(
            doc_width,
            doc_height,
            "MDPACK IMPORTED FILE",
            "RGBA",
            "U8",
            doc_icc,
            doc_ppi
        )

        # Krita makes a default layer for us when creating
        # a new document. Let's keep track of it so we can delete it at the end
        default_node = self.m_doc.topLevelNodes()
        if len(default_node) != 0:
            default_node = default_node[0]

        # TODO: Figure out how to handle checkerBG and bgColor
        # https://docs.krita.org/en/user_manual/introduction_from_other_software/introduction_from_sai.html#transparency
        # doc_bg = self.mdp_mdi.bgColor()
        # if doc_bg is not None:
        #     self.m_doc.setBackgroundColor(doc_bg)

        layers = self.mdp_mdi.layers()

        # We generate the Krita nodes based on the
        # xml data. We keep track of mdp layer id's so that
        # we can establish parent-child layer stuff in the
        # next step. The id of -1 is supposed to correspond to
        # the root.
        root_node = self.m_doc.rootNode()
        knodes = { "-1" : root_node }
        for l in layers:
            knode = l.createKritaNode(self.m_doc)
            knodes[l.id] = knode

        # We link up all child nodes with the appropriate
        # parent node using the dictionary from earlier
        for l in layers:
            parent_node = knodes.get(l.parentId)
            assert parent_node is not None
            parent_node.addChildNode(l.kritaNode, None)

        # We decode the archive data to create the tiles
        # We immediately use these tiles to reconstruct
        # the image in the krita node
        for l in layers:
            archive = self.mdp_mdibin[l.archiveName]
            l.decodeArchive(archive)
            if l.layerType in ("32bpp", "8bpp", "1bpp",):
                l.setKritaPixels()

        # We set the active layer using the dictionary
        # that we made earlier
        active_layer_id = self.mdp_mdi.activeLayerId()
        active_krita_node = knodes.get(active_layer_id)
        if active_krita_node is not None:
            self.m_doc.setActiveNode(active_krita_node)

        # Delete default layer that was created for us
        if default_node is not None:
            default_node.remove()
