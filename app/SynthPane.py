import wx
from wx.lib.pubsub import pub
from ObjectListView import ColumnDefn

import utils
import common.utils as cu

WAVE_IMAGES = [
    wx.Image("images/synth_saw.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/synth_square.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/synth_sine.gif", wx.BITMAP_TYPE_GIF)
]

class SynthPane(wx.Panel):
    def __init__(self, parent, project):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.project = project

        self.synth_list = utils.new_obj_list_view(self)
        self.synth_list.SetEmptyListMsg("Loading synth list ...")

        id_col = ColumnDefn(
            "#", "center", 50,
            lambda x: "%01x0-%01xf" % (getattr(x, "index"),
                                       getattr(x, "index")))
        self.synth_list.SetColumns([id_col])

        self.synth_list.SetObjects(self.project.song.synths.as_list())

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.synth_list, 1, wx.ALL, border=5)

        self.SetSizer(sizer)
