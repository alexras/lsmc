import wx
from wx.lib.pubsub import pub

import common.bread_spec as spec
import channels

class WavePanel(wx.Panel):
    def __init__(self, parent, index):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.index = index
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.wave = None

        pub.subscribe(self.handle_synth_changed, channels.SYNTH_CHANGE)

    def handle_synth_changed(self, data):
        synth = data

        self.wave = synth.waves[self.index]

        self.Refresh()

    def on_size(self, event):
        frame = event.GetEventObject()

        width, height = frame.GetSizeTuple()

        if width % spec.FRAMES_PER_WAVE != 0:
            width = (width // spec.FRAMES_PER_WAVE) * spec.FRAMES_PER_WAVE

        square_size = (width, width / 2)

        frame.SetSize(square_size)

    def on_paint(self, event=None):
        width, height = self.GetSizeTuple()

        assert width == height * 2
        assert width % spec.FRAMES_PER_WAVE == 0

        square_dimension = width / spec.FRAMES_PER_WAVE

        dc = wx.PaintDC(self)
        dc.Clear()
        dc.SetBrush(wx.Brush(wx.BLACK, wx.SOLID))

        if self.wave is None:
            return

        squares = [
            (square_dimension * i,
             square_dimension * (0xf - self.wave[i]),
             square_dimension, square_dimension)
            for i in xrange(spec.FRAMES_PER_WAVE)]

        dc.DrawRectangleList(squares)
