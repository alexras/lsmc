import wx
from ObjectListView import ColumnDefn

import utils

from SynthParamsPanel import SynthParamsPanel
from WavesPanel import WavesPanel
import channels

class SynthPane(wx.Panel):
    def __init__(self, parent, project):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.project = project

        self.synth_change_channel = channels.SYNTH_CHANGE(project)

        self.synth_list = utils.new_obj_list_view(self)
        self.synth_list.SetEmptyListMsg("Loading synth list ...")

        id_col = ColumnDefn(
            "#", "center", 40,
            lambda x: "%01x0-%01xf" % (getattr(x, "index"),
                                       getattr(x, "index")),
            isSpaceFilling=True)

        self.synth_list.SetColumns([id_col])

        self.synth_list.SetObjects(self.project.song.synths.as_list())

        self.waves_panel = WavesPanel(self)
        self.synth_params_panel = SynthParamsPanel(self)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.handle_synth_changed,
                  self.synth_list)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.synth_list, 1, wx.ALIGN_TOP | wx.ALL | wx.EXPAND,
                  border=5)

        body_sizer = wx.BoxSizer(wx.VERTICAL)

        body_sizer.Add(self.waves_panel, 2, wx.ALL | wx.EXPAND, border=5)
        body_sizer.Add(self.synth_params_panel, 1, wx.ALL | wx.EXPAND, border=5)

        sizer.Add(body_sizer, 7, wx.ALL | wx.EXPAND, border=5)

        self.SetSizer(sizer)

        self.Layout()

    def handle_synth_changed(self, data):
        selected_synths = self.synth_list.GetSelectedObjects()

        synth = None

        if len(selected_synths) > 0:
            synth = selected_synths[0]

        self.synth_change_channel.publish(synth)

    def refresh(self):
        pass
