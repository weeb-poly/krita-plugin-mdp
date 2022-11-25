from .utils import fillNodeWithTiles

from ..neet import CMangaLayer

class CKritaLayer(CMangaLayer):
    kritaNode: KritaNode

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

        fillNodeWithTiles(
            self.kritaNode,
            self.tiles,
            self.layerType,
            self.tileDim,
            layerColor
        )

        self.kritaNode.move(self.ofsx, self.ofsy)