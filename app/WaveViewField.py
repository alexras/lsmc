import wx

from ImageSetViewField import ImageSetViewField

from viewutils import instr_attr

WAVE_IMAGES = [
    wx.Image("images/wave12.5.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/wave25.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/wave50.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/wave75.gif", wx.BITMAP_TYPE_GIF)]

class WaveViewField(ImageSetViewField):
    def __init__(self, parent):
        ImageSetViewField.__init__(
            self, parent, instr_attr("wave"), WAVE_IMAGES)
