import wx

class WavePanel(wx.Panel):
    def __init__(self, parent, index):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.index = index
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, event=None):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.SetPen(wx.Pen(wx.BLACK, 4))
        dc.DrawText("%d" % (self.index), 0, 0)
