import wx
from wx.lib.pubsub import pub
from ObjectListView import ColumnDefn

import utils
import common.utils as cu
import common.bread_spec as spec

from SynthParamsPanel import SynthParamsPanel
from WavePanel import WavePanel
from WavesPanel import WavesPanel

class SynthPane(wx.Panel):
    def __init__(self, parent, project):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.project = project

        self.synth_list = utils.new_obj_list_view(self)
        self.synth_list.SetEmptyListMsg("Loading synth list ...")

        id_col = ColumnDefn(
            "#", "center", 50,
            lambda x: "%01x0-%01xf" % (getattr(x, "index"),
                                       getattr(x, "index")),
            isSpaceFilling=True)

        self.synth_list.SetColumns([id_col])

        self.synth_list.SetObjects(self.project.song.synths.as_list())

        self.waves_panel = WavesPanel(self)
        self.synth_params_panel = SynthParamsPanel(self)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.synth_list, 1, wx.ALIGN_TOP | wx.ALL | wx.EXPAND,
                  border=5)

        body_sizer = wx.BoxSizer(wx.VERTICAL)

        body_sizer.Add(self.waves_panel, 2, wx.ALL | wx.EXPAND, border=5)
        body_sizer.Add(self.synth_params_panel, 1, wx.ALL, border=5)

        sizer.Add(body_sizer, 5, wx.ALL | wx.EXPAND, border=5)

        self.SetSizer(sizer)

        self.Layout()
