import wx

from ImageSetViewField import ImageSetViewField

from viewutils import instr_attr

from utils import make_image

WAVE_IMAGES = {
    "12.5%": make_image("wave12"),
    "25%": make_image("wave25"),
    "50%": make_image("wave50"),
    "75%": make_image("wave75")
}

class WaveViewField(ImageSetViewField):
    def __init__(self, parent):
        ImageSetViewField.__init__(
            self, parent, instr_attr("wave"), WAVE_IMAGES)
