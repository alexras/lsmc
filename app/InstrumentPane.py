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

        self.instr_number = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.envelope = wx.TextCtrl(self, style=wx.TE_READONLY)

        self.wave_images = [
            wx.Image("images/wave12.5.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/wave25.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/wave50.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/wave75.gif", wx.BITMAP_TYPE_GIF)]

        empty_wave = wx.EmptyImage(self.wave_images[0].GetWidth(),
                                    self.wave_images[0].GetHeight())
        self.wave = wx.StaticBitmap(
            self, wx.ID_ANY, wx.BitmapFromImage(empty_wave))

        self.pan = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.length = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.sweep = wx.TextCtrl(self, style=wx.TE_READONLY)

        self.vibe_images = [
            wx.Image("images/vibe_hfsine.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/vibe_saw.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/vibe_sine.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/vibe_square.gif", wx.BITMAP_TYPE_GIF)
        ]

        empty_vibe = wx.EmptyImage(self.vibe_images[0].GetWidth(),
                                   self.vibe_images[0].GetHeight())

        self.vibe = wx.StaticBitmap(
            self, wx.ID_ANY, wx.BitmapFromImage(empty_vibe))

        self.pu2_tune = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.pu_fine = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.automate = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.table = wx.TextCtrl(self, style=wx.TE_READONLY)

        sizer = wx.BoxSizer(wx.VERTICAL)

        def add_field(label_text, control):
            label = wx.StaticText(self, label=label_text)

            field_sizer = wx.BoxSizer(wx.HORIZONTAL)
            field_sizer.Add(label, 1, wx.ALL)
            field_sizer.Add(control, 1, wx.ALL)

            sizer.Add(field_sizer, 0, wx.ALL)

        add_field("Instrument", self.instr_number)
        add_field("Envelope", self.envelope)
        add_field("Wave", self.wave)
        add_field("Output", self.pan)
        add_field("Length", self.length)
        add_field("Sweep", self.sweep)
        add_field("Vib. Type", self.vibe)
        add_field("PU2 Tune", self.pu2_tune)
        add_field("PU Fine", self.pu_fine)
        add_field("Automate", self.automate)
        add_field("Table", self.table)

        pub.subscribe(self.update_view, channels.PULSE_CHANGE)

        self.SetSizer(sizer)

    def update_view(self, data):
        instr = data
        self.instr_number.SetValue("%02d" % (instr.index))
        self.envelope.SetValue("%02x" % (instr.envelope))
        self.wave.SetBitmap(wx.BitmapFromImage(self.wave_images[instr.wave]))
        self.pan.SetValue(instr.pan)

        if instr.has_sound_length:
            length = "%02x" % (instr.sound_length)
        else:
            length = "UNLIM"

        self.length.SetValue(length)
        self.sweep.SetValue("%02x" % (instr.sweep))
        self.vibe.SetBitmap(
            wx.BitmapFromImage(self.vibe_images[instr.vibrato.type]))
        self.pu2_tune.SetValue("%02x" % (instr.phase_transpose))
        self.pu_fine.SetValue("%x" % (instr.phase_finetune))

        if instr.automate_1:
            self.automate.SetValue("ON")
        else:
            self.automate.SetValue("OFF")

        if instr.table is None:
            self.table.SetValue("OFF")
        else:
            self.table.SetValue("%02x" % (instr.table.index))

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
