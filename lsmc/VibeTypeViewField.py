import wx

from ImageSetViewField import ImageSetViewField

VIBE_IMAGES = [
    wx.Image("images/vibe_hfsine.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/vibe_saw.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/vibe_sine.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/vibe_square.gif", wx.BITMAP_TYPE_GIF)
]

class VibeTypeViewField(ImageSetViewField):
    def __init__(self, parent):
        ImageSetViewField.__init__(
            self, parent, lambda instr: instr.vibrato.type, VIBE_IMAGES)
