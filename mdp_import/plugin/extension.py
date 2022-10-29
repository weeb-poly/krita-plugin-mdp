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

    def importDocuments(self) -> None:
        fileNames = QFileDialog.getOpenFileNames(filter="mdipack (*.mdp)")

        loader = MdpLoader()

        for filename in fileNames:
            with open(fileName, "rb") as _file:
                doc = loader.buildDoc(_file, self.krita)

            self.krita.activeWindow().addView(doc)
            doc.refreshProjection()

    def createActions(self, window: Window) -> None:
        action = window.createAction("mdpImport", "Import MDP File(s)")
        action.triggered.connect(self.importDocuments)
