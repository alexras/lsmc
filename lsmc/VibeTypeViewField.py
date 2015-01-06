import wx

from ImageSetViewField import ImageSetViewField

from utils import make_image

VIBE_IMAGES = {
    "hf": make_image("vibe_hfsine"),
    "sawtooth": make_image("vibe_saw"),
    "sine": make_image("vibe_sine"),
    "square": make_image("vibe_square")
}

class VibeTypeViewField(ImageSetViewField):
    def __init__(self, parent):
        ImageSetViewField.__init__(
            self, parent, lambda instr: instr.vibrato.type, VIBE_IMAGES)
