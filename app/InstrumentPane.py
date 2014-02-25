import wx, functools, event_handlers
from wx.lib.pubsub import pub
from ObjectListView import ObjectListView, ColumnDefn

import channels

import utils

import common.utils as cu

class InstrumentPane(wx.Panel):
    def __init__(self, parent, project):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.instr_list = utils.new_obj_list_view(self)
        self.instr_list.SetEmptyListMsg("Loading instrument list ...")

        def instr_name_printer(x):
            name = getattr(x, "name")

            if map(ord, name) == [0] * len(name):
                return "[UNNAMED]"
            else:
                return name

        id_col = ColumnDefn("#", "center", 30, lambda x: "%02d" %
                            (getattr(x, "index")))
        name_col = ColumnDefn("Name", "left", 200, instr_name_printer)
        type_col = ColumnDefn("Type", "left", 50, "type")
        self.instr_list.SetColumns([id_col, name_col, type_col])

        self.instrument_objects = project.song.instruments.as_list()

        self.instr_list.SetObjects(self.instrument_objects)

        self.instr_panels = {
            None: NoInstrumentSelectedPanel(self),
            "pulse": PulseInstrumentPanel(self),
            "wave": WaveInstrumentPanel(self),
            "kit": KitInstrumentPanel(self),
            "noise": NoiseInstrumentPanel(self)
        }

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.handle_instr_changed,
                  self.instr_list)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(self.instr_list, 1, wx.ALL | wx.EXPAND, border=5)

        for panel in self.instr_panels.values():
            sizer.Add(panel, 1, wx.EXPAND)

        self.SetSizer(sizer)

        self.show_instr_panel(None)

    def show_instr_panel(self, instrument):
        instr_type = None

        if instrument is not None:
            instr_type = instrument.type

        for (key, val) in self.instr_panels.items():
            if key == instr_type:
                val.Show()
                val.change_instrument(instrument)
            else:
                val.Hide()

        self.Layout()

    def handle_instr_changed(self, event):
        selected_instruments = self.instr_list.GetSelectedObjects()

        instrument = None

        if len(selected_instruments) > 0:
            instrument = selected_instruments[0]

        self.show_instr_panel(instrument)

class InstrumentPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

    def change_instrument(self, instrument):
        pass

class NoInstrumentSelectedPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)

        info_text = wx.StaticText(
            self, label="No Instrument Selected",
            style=wx.ALIGN_CENTRE_HORIZONTAL)

        sizer.Add(info_text, 1, wx.ALL | wx.EXPAND)

class PulseInstrumentPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)

        instr_label = wx.StaticText(self, label="Instrument")
        self.instr_number = wx.TextCtrl(self)

        instr_sizer = wx.BoxSizer(wx.HORIZONTAL)

        instr_sizer.Add(instr_label, 1, wx.ALL)
        instr_sizer.Add(self.instr_number, 1, wx.ALL)

        sizer.Add(instr_sizer, 0, wx.ALL)

        envelope_label = wx.StaticText(self, label="Envelope")
        self.envelope = wx.TextCtrl(self)

        envelope_sizer = wx.BoxSizer(wx.HORIZONTAL)

        envelope_sizer.Add(envelope_label, 1, wx.ALL)
        envelope_sizer.Add(self.envelope, 1, wx.ALL)

        sizer.Add(envelope_sizer, 0, wx.ALL)

        wave_label = wx.StaticText(self, label="Wave")

        self.wave_images = [
            wx.Image("images/wave12.5.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/wave25.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/wave50.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/wave75.gif", wx.BITMAP_TYPE_GIF)]

        placeholder = wx.EmptyImage(self.wave_images[0].GetWidth(),
                                    self.wave_images[0].GetHeight())

        self.wave = wx.StaticBitmap(
            self, wx.ID_ANY, wx.BitmapFromImage(placeholder))

        wave_sizer = wx.BoxSizer(wx.HORIZONTAL)

        wave_sizer.Add(wave_label, 1, wx.ALL)
        wave_sizer.Add(self.wave, 1, wx.ALL)

        sizer.Add(wave_sizer, 0, wx.ALL)

        pub.subscribe(self.update_view, channels.PULSE_CHANGE)

        self.SetSizer(sizer)

    def update_view(self, data):
        instr = data
        self.instr_number.SetValue("%02d" % (instr.index))
        self.envelope.SetValue("%02x" % (instr.envelope))
        self.wave.SetBitmap(wx.BitmapFromImage(self.wave_images[instr.wave]))
        self.Layout()

    def change_instrument(self, instrument):
        self.instrument = instrument
        pub.sendMessage(channels.PULSE_CHANGE, data=self.instrument)


class WaveInstrumentPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)

        info_text = wx.StaticText(
            self, label="Wave Selected",
            style=wx.ALIGN_CENTRE_HORIZONTAL)

        sizer.Add(info_text, 1, wx.ALL | wx.EXPAND)

class KitInstrumentPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)

        info_text = wx.StaticText(
            self, label="Kit Selected",
            style=wx.ALIGN_CENTRE_HORIZONTAL)

        sizer.Add(info_text, 1, wx.ALL | wx.EXPAND)

class NoiseInstrumentPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)

        info_text = wx.StaticText(
            self, label="Noise Selected",
            style=wx.ALIGN_CENTRE_HORIZONTAL)

        sizer.Add(info_text, 1, wx.ALL | wx.EXPAND)
