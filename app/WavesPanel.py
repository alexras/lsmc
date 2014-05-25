import wx

class WavesPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        GRID_SPACING = 3

        self.wave_panels = []

        for i in xrange(spec.NUM_SYNTHS):
            self.wave_panels.append(WavePanel(self, i))

        sizer = wx.GridSizer(4, 4, GRID_SPACING, GRID_SPACING)

        for panel in self.wave_panels:
            sizer.Add(panel, 1, wx.ALL | wx.EXPAND)

        self.SetSizer(sizer)
