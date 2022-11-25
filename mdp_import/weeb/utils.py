from typing import List, Optional

from krita import Node as KritaNode

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage, QColor, QPainter

from ..neet.CImageTile import CImageTile


def QColorFromArgbStr(c: str) -> QColor:
    a, r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), int(c[6:8], 16)
    return QColor(r, g, b, a)


def setQImageToKritaNode(
    node: KritaNode,
    img: QImage,
    x: int,
    y: int
) -> None:
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


def fillNodeWithTiles(
    node: KritaNode,
    tiles: List[CImageTile],
    layerType: str,
    tileDim: int,
    layerColor: Optional[str] = None
) -> None:
    if layerColor is not None:
        layerColor = QColorFromArgbStr(layerColor)

    for tile in tiles:
        tile_img = decodeTileImage(tile, layerType, tileDim, layerColor)
        if tile_img is not None:
            setQImageToKritaNode(node, tile_img, tile.col * tileDim, tile.row * tileDim)


def decodeTileImage(
    tile: MdpTile,
    layerType: str,
    tileDim: int,
    layerColor: Optional[QColor] = None
) -> QImage:
    tile_img = None

    if layerType == '32bpp':
        # For some reason, this reads in BGRA data... so... endian problem solved?
        tile_img = QImage(tile.data, tileDim, tileDim, QImage.Format_ARGB32)
    elif layerType == '8bpp':
        tile_img = QImage(tile.data, tileDim, tileDim, QImage.Format_Grayscale8)
        if layerColor is not None:
            mask_img = tile_img
            tile_img = QImage(tileDim, tileDim, QImage.Format_ARGB32)
            tile_img.fill(layerColor)
            tile_img.setAlphaChannel(mask_img)
    elif layerType == '1bpp':
        tile_img = QImage(tile.data, tileDim, tileDim, QImage.Format_Mono)
        if layerColor is not None:
            mask_img = tile_img
            tile_img = QImage(tileDim, tileDim, QImage.Format_ARGB32)
            tile_img.fill(layerColor)
            tile_img.setAlphaChannel(mask_img) # This should convert the mask to 8-bit grayscale

    return tile_img


def decodeLayerImage(
    tiles: List[CImageTile],
    layerWidth: int,
    layerHeight: int,
    layerType: str,
    tileDim: int,
    layerColor: Optional[str] = None
) -> QImage:
    if layerType in ('8bpp', '1bpp',):
        assert layerColor is not None

    if layerColor is not None:
        layerColor = QColorFromArgbStr(layerColor)

    layer_size = QSize(layerWidth, layerHeight)
    layer_img = QImage(layer_size, QImage.Format_ARGB32)

    painter = QPainter(layer_img)

    for tile in tiles:
        tile_img = decodeTileImage(tile, layerType, tileDim, layerColor)

        if tile_img is not None:
            painter.drawImage(tile.col * tileDim, tile.row * tileDim, tile_img)

    return layer_img
