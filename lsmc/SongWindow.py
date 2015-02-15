import wx

import utils
from InstrumentPane import InstrumentPane
from SynthPane import SynthPane
from TablePane import TablePane

from channels import INSTR_IMPORT, SONG_MODIFIED


class SongWindow(wx.Frame):

    def __init__(self, parent, project, index):
        frame_size = (650, 550)

        window_pos = utils.random_pos(frame_size)

        if window_pos is None:
            return

        wx.Frame.__init__(
            self, parent, wx.ID_ANY, "Song - %s" % (project.name),
            size=frame_size, pos=window_pos,
            style=wx.SYSTEM_MENU | wx.CAPTION |
            wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        panel = wx.Panel(self)

        self.notebook = wx.Notebook(panel, wx.ID_ANY, style=wx.BK_DEFAULT)
        self.project = project

        self.instr_import_channel = INSTR_IMPORT(self.project)
        self.instr_import_channel.subscribe(self.handle_song_modified)

        self.song_modified_channel = SONG_MODIFIED(index)
        self.song_modified_channel.subscribe(self.handle_song_modified)

        instrument_pane = InstrumentPane(self.notebook, project, index)
        synth_pane = SynthPane(self.notebook, project)
        table_pane = TablePane(self.notebook, project)

        self.notebook.AddPage(instrument_pane, "Instruments")
        self.notebook.AddPage(synth_pane, "Synths")
        self.notebook.AddPage(table_pane, "Tables")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING,
                  self.handle_notebook_page_changing, self.notebook)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.notebook, 1, flag=wx.ALL | wx.EXPAND, border=5)

        panel.SetSizer(sizer)

        self.Layout()
        self.Show()

    def handle_notebook_page_changing(self, event):
        self.notebook.GetPage(event.GetSelection()).refresh()

    def handle_song_modified(self, data=None):
        if data is not None:
            self.SetTitle(self.GetTitle() + ' - MODIFIED')
