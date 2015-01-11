import wx

from InstrumentPanel import InstrumentPanel


class NoInstrumentSelectedPanel(InstrumentPanel):

    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent, None)

        info_text = wx.StaticText(
            self, label="No Instrument Selected",
            style=wx.ALIGN_CENTRE_HORIZONTAL)

        self.main_sizer.Add(info_text, 1, wx.ALL | wx.EXPAND)

    def change_instrument(self, instrument):
        pass
