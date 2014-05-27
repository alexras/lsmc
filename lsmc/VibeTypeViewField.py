import wx

from ImageSetViewField import ImageSetViewField

from utils import make_image

VIBE_IMAGES = [
    make_image(("images", "vibe_hfsine.gif")),
    make_image(("images", "vibe_saw.gif")),
    make_image(("images", "vibe_sine.gif")),
    make_image(("images", "vibe_square.gif"))
]

class VibeTypeViewField(ImageSetViewField):
    def __init__(self, parent):
        ImageSetViewField.__init__(
            self, parent, lambda instr: instr.vibrato.type, VIBE_IMAGES)
