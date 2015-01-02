import wx

from ImageSetViewField import ImageSetViewField

from viewutils import instr_attr

from utils import make_image

WAVE_IMAGES = {
    "12.5%": make_image(("images", "wave12.5.gif")),
    "25%": make_image(("images", "wave25.gif")),
    "50%": make_image(("images", "wave50.gif")),
    "75%": make_image(("images", "wave75.gif"))
}

class WaveViewField(ImageSetViewField):
    def __init__(self, parent):
        ImageSetViewField.__init__(
            self, parent, instr_attr("wave"), WAVE_IMAGES)
