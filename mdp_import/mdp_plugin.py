from krita import Krita, Extension, Window

from PyQt5.QtWidgets import QFileDialog

from .mdp_loader import MdpLoader

class MdpExtension(Extension):
    # Reduce calls to Krita.instance() and self.parent()
    # by storing reference to current Krita instance
    krita: Krita

    def __init__(self, parent: Krita) -> None:
        super().__init__(parent)
        self.krita = parent

    def setup(self) -> None:
        pass

    @classmethod
    def addExtension(cls, instance: Krita) -> None:
        instance.addExtension(cls(instance))

    def importDocument(self) -> None:
        fileName = QFileDialog.getOpenFileName(filter="mdipack (*.mdp)")[0]

        loader = MdpLoader()
        with open(fileName, "rb") as file_:
            doc = loader.buildDoc(file_, self.krita)

        self.krita.activeWindow().addView(doc)
        doc.refreshProjection()

    def createActions(self, window: Window) -> None:
        action = window.createAction("mdpImport", "Import MDP File")
        action.triggered.connect(self.importDocument)

MdpExtension.addExtension(Krita.instance())
