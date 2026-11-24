"""Rasteriza el favicon existente en los tamaños que usa Windows."""
from pathlib import Path
import struct
import sys

from PySide6.QtCore import QByteArray, QBuffer, QIODevice, QRectF
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parents[2]


def make_icon(path):
    logo = QSvgRenderer(str(ROOT / "dist" / "assets" / "favicon.svg"))
    if not logo.isValid():
        raise RuntimeError("El favicon SVG no se pudo rasterizar.")
    frames = []
    for size in (16, 32, 48, 64, 128, 256):
        image = QImage(size, size, QImage.Format.Format_ARGB32)
        image.fill(0)
        painter = QPainter(image)
        logo.render(painter, QRectF(0, 0, size, size))
        painter.end()
        data = QByteArray()
        buffer = QBuffer(data)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not image.save(buffer, "PNG"):
            raise RuntimeError("No se pudo codificar el icono.")
        frames.append((size, bytes(data)))
    offset = 6 + 16 * len(frames)
    entries = []
    for size, payload in frames:
        entries.append(struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(payload), offset))
        offset += len(payload)
    path.write_bytes(struct.pack("<HHH", 0, 1, len(frames)) + b"".join(entries) + b"".join(data for _, data in frames))


if __name__ == "__main__":
    make_icon(Path(sys.argv[1]))
