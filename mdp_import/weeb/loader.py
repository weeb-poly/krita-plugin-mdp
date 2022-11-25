import logging
from typing import BinaryIO, Tuple

from krita import Krita, Document

from ..neet.CMangaFileMDP import CMangaFileMDP

from .CKritaLayer import CKritaLayer

class MdpLoader:
    krita: Krita

    def __init__(self, krita: Krita) -> None:
        self.krita = krita

    def buildDoc(self, io: BinaryIO) -> Document:
        mdp = self._read(io)
        m_doc = self._decode(mdp)
        return m_doc

    def _read(self, io: BinaryIO) -> CMangaFileMDP:
        try:
            mdp = CMangaFileMDP.read(io)
        except Exception:
            raise Exception("failed reading mdp")

        return mdp

    def _decode(self, mdp: CMangaFileMDP) -> Document:
        mdp_mdi = mdp.mdi
        mdp_mdibin = mdp.mdb

        doc_width = mdp_mdi.width()
        doc_height = mdp_mdi.height()

        doc_icc = mdp_mdi.icc()

        # NOTE: Assuming 1ppi = 1dpi
        doc_ppi = mdp_mdi.dpi()

        m_doc = self.krita.createDocument(
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
        default_node = None
        default_nodes = m_doc.topLevelNodes()
        if len(default_nodes) != 0:
            default_node = default_nodes[0]

        # TODO: Figure out how to handle checkerBG and bgColor
        # https://docs.krita.org/en/user_manual/introduction_from_other_software/introduction_from_sai.html#transparency
        # doc_bg = self.mdp_mdi.bgColor()
        # if doc_bg is not None:
        #     m_doc.setBackgroundColor(doc_bg)

        layers = mdp_mdi.layers()

        # This should be fun(tm)
        # Changing CMangaLayer classes to CKritaLayer
        # Allows us to keep Krita code separate
        for l in layers:
            l.__class__ = CKritaLayer

        # We generate the Krita nodes based on the
        # xml data. We keep track of mdp layer id's so that
        # we can establish parent-child layer stuff in the
        # next step. The id of -1 is supposed to correspond to
        # the root.
        root_node = m_doc.rootNode()
        knodes = { "-1" : root_node }
        for l in layers:
            knode = l.createKritaNode(m_doc)
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
            archive = mdp_mdibin[l.archiveName]
            l.decodeArchive(archive)
            if l.layerType in ("32bpp", "8bpp", "1bpp",):
                l.setKritaPixels()

        # We set the active layer using the dictionary
        # that we made earlier
        active_layer_id = mdp_mdi.activeLayerId()
        active_krita_node = knodes.get(active_layer_id)
        if active_krita_node is not None:
            m_doc.setActiveNode(active_krita_node)

        # Delete default layer that was created for us
        if default_node is not None:
            default_node.remove()
        
        return m_doc
