import wx
from wx.lib.pubsub import pub

import channels

from EmptySynthPanel import EmptySynthPanel
from SelectedSynthPanel import SelectedSynthPanel

class SynthParamsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.empty_synth_panel = EmptySynthPanel(self)
        self.selected_synth_panel = SelectedSynthPanel(self)

        pub.subscribe(self.handle_synth_changed, channels.SYNTH_CHANGE)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(self.empty_synth_panel, 1, wx.EXPAND)
        sizer.Add(self.selected_synth_panel, 1, wx.EXPAND)

        self.SetSizer(sizer)

        self.show_empty_panel()

    def handle_synth_changed(self, data):
        synth = data

        if synth is None:
            self.show_empty_panel()
        else:
            self.show_selected_panel()

        self.Layout()

    def show_empty_panel(self):
        self.empty_synth_panel.Show()
        self.selected_synth_panel.Hide()

    def show_selected_panel(self):
        self.empty_synth_panel.Hide()
        self.selected_synth_panel.Show()
