import wx
from wx.lib.pubsub import pub

import channels

WAVE_IMAGES = [
    wx.Image("images/synth_saw.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/synth_square.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/synth_sine.gif", wx.BITMAP_TYPE_GIF)
]

class SelectedSynthPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        pub.subscribe(self.handle_synth_changed, channels.SYNTH_CHANGE)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.SetSizer(sizer)

    def handle_synth_changed(self, data):
        synth = data
        self.Layout()
