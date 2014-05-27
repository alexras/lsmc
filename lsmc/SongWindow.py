import wx

import utils
from InstrumentPane import InstrumentPane
from SynthPane import SynthPane
from TablePane import TablePane

class SongWindow(wx.Frame):
    def __init__(self, parent, project):
        frame_size = (650,550)

        wx.Frame.__init__(
            self, parent, wx.ID_ANY, "Song - %s" % (project.name),
            size=frame_size, pos=utils.random_pos(frame_size),
            style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        panel = wx.Panel(self)

        self.notebook = wx.Notebook(panel, wx.ID_ANY, style=wx.BK_DEFAULT)
        self.project = project

        instrument_pane = InstrumentPane(self.notebook, project)
        synth_pane = SynthPane(self.notebook, project)
        table_pane = TablePane(self.notebook, project)

        self.notebook.AddPage(instrument_pane, "Instruments")
        self.notebook.AddPage(synth_pane, "Synths")
        self.notebook.AddPage(table_pane, "Tables")

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.notebook, 1, flag=wx.ALL | wx.EXPAND, border=5)

        panel.SetSizer(sizer)

        self.Layout()
        self.Show()
