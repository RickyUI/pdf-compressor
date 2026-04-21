"""
Compatibility shim: patch fitz.Pixmap to support the legacy 3-arg constructor
form ``Pixmap(colorspace, irect, samples)`` that was removed after pymupdf 1.23.x.
The current API requires ``Pixmap(colorspace, width, height, samples, alpha)``.
"""
import fitz

_original_pixmap_init = fitz.Pixmap.__init__


def _compat_pixmap_init(self, *args, **kwargs):
    # Legacy form: Pixmap(colorspace, (x0, y0, x1, y1), samples)
    if (
        len(args) == 3
        and isinstance(args[0], fitz.Colorspace)
        and isinstance(args[1], (tuple, list))
        and len(args[1]) == 4
        and isinstance(args[2], (bytes, bytearray))
    ):
        colorspace, irect, samples = args
        x0, y0, x1, y1 = irect
        width = x1 - x0
        height = y1 - y0
        _original_pixmap_init(self, colorspace, width, height, samples, 0)
    else:
        _original_pixmap_init(self, *args, **kwargs)


fitz.Pixmap.__init__ = _compat_pixmap_init
