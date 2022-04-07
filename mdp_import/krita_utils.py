from typing import Optional

from krita import Node as KritaNode

from PyQt5.QtGui import QImage

def setQImageToKritaNode(node: KritaNode, img: QImage, x: int, y: int) -> None:
    # We're assuming that the KritaNode and the QImage are in the same format
    # Buuut, just to be sure

    assert node.colorModel() == "RGBA"
    assert node.colorDepth() == "U8"

    # Some plugins use Format_RGBA8888
    # I have confirmed after digging into the
    # Krita source code that the appropritate color space
    # is Format_ARGB32
    if img.format() != QImage.Format_ARGB32:
        img = img.convertToFormat(QImage.Format_ARGB32)

    # Get the Width and Height from QImage
    w = img.width()
    h = img.height()

    imgBytes = img.constBits()

    # PyQt5 returns a sip.voidptr while PySide2 returns
    # a bytes object. If we're using PyQt5, then we
    # convert the sip.voidptr to a bytes object
    if not isinstance(imgBytes, bytes):
        imgBytes.setsize(img.byteCount())
        imgBytes = imgBytes.asstring()

    # This is auto-converted to a QByteArray somewhere down the line
    node.setPixelData(imgBytes, x, y, w, h)

def pyz_path_insert(pyz_file: str, path: Optional[str] = None) -> None:
    import os, sys

    if path is None:
        path = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(path, pyz_file))
