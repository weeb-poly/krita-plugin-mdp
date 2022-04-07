from krita import Krita, Extension, Window

from PyQt5.QtWidgets import QFileDialog

from ..mdp.loader import MdpLoader

class MdpExtension(Extension):
    # Reduce calls to Krita.instance() and self.parent()
    # by storing reference to current Krita instance
    krita: Krita

    def __init__(self, parent: Krita) -> None:
        super().__init__(parent)
        self.krita = parent

    def setup(self) -> None:
        pass

    def importDocument(self) -> None:
        fileName = QFileDialog.getOpenFileName(filter="mdipack (*.mdp)")[0]

        loader = MdpLoader()
        with open(fileName, "rb") as _file:
            doc = loader.buildDoc(_file, self.krita)

        self.krita.activeWindow().addView(doc)
        doc.refreshProjection()

    def createActions(self, window: Window) -> None:
        action = window.createAction("mdpImport", "Import MDP File")
        action.triggered.connect(self.importDocument)
