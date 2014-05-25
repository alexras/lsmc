import wx

class EmptySynthPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        info_text = wx.StaticText(
            self, label="No synth selected", style=wx.ALIGN_CENTRE_HORIZONTAL)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(info_text, 1, wx.ALL | wx.EXPAND)

        self.SetSizer(sizer)
