import wx, functools, event_handlers
from wx.lib.pubsub import pub
from ObjectListView import ObjectListView, ColumnDefn

import channels

import utils

import common.utils as cu

VIBE_IMAGES = [
    wx.Image("images/vibe_hfsine.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/vibe_saw.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/vibe_sine.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/vibe_square.gif", wx.BITMAP_TYPE_GIF)

]

EMPTY_VIBE = wx.EmptyImage(
    VIBE_IMAGES[0].GetWidth(), VIBE_IMAGES[0].GetHeight())
def read_only_text_value(parent):
    return wx.TextCtrl(parent, style=wx.TE_READONLY)

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
    def __init__(self, parent, channel):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.pubsub_channel = channel
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(self.sizer)

        if channel is not None:
            pub.subscribe(self.update_view, channel)

    def update_view(self, data):
        pass

    def add_field(self, label_text, control):
        label = wx.StaticText(self, label=label_text)

        field_sizer = wx.BoxSizer(wx.HORIZONTAL)
        field_sizer.Add(label, 1, wx.ALL)
        field_sizer.Add(control, 1, wx.ALL)

        self.sizer.Add(field_sizer, 0, wx.ALL)

    def change_instrument(self, instrument):
        pub.sendMessage(self.pubsub_channel, data=instrument)

class NoInstrumentSelectedPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent, None)

        info_text = wx.StaticText(
            self, label="No Instrument Selected",
            style=wx.ALIGN_CENTRE_HORIZONTAL)

        self.sizer.Add(info_text, 1, wx.ALL | wx.EXPAND)

    def change_instrument(self, instrument):
        pass

class PulseInstrumentPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent, channels.PULSE_CHANGE)

        self.envelope = read_only_text_value(self)

        self.wave_images = [
            wx.Image("images/wave12.5.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/wave25.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/wave50.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/wave75.gif", wx.BITMAP_TYPE_GIF)]

        empty_wave = wx.EmptyImage(self.wave_images[0].GetWidth(),
                                    self.wave_images[0].GetHeight())
        self.wave = wx.StaticBitmap(
            self, wx.ID_ANY, wx.BitmapFromImage(empty_wave))

        self.pan = read_only_text_value(self)
        self.length = read_only_text_value(self)
        self.sweep = read_only_text_value(self)
        self.vibe = wx.StaticBitmap(
            self, wx.ID_ANY, wx.BitmapFromImage(EMPTY_VIBE))
        self.pu2_tune = read_only_text_value(self)
        self.pu_fine = read_only_text_value(self)
        self.automate = read_only_text_value(self)
        self.table = read_only_text_value(self)

        self.add_field("Envelope", self.envelope)
        self.add_field("Wave", self.wave)
        self.add_field("Output", self.pan)
        self.add_field("Length", self.length)
        self.add_field("Sweep", self.sweep)
        self.add_field("Vib. Type", self.vibe)
        self.add_field("PU2 Tune", self.pu2_tune)
        self.add_field("PU Fine", self.pu_fine)
        self.add_field("Automate", self.automate)
        self.add_field("Table", self.table)

    def update_view(self, data):
        instr = data

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
            wx.BitmapFromImage(VIBE_IMAGES[instr.vibrato.type]))
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

class WaveInstrumentPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent, channels.WAVE_CHANGE)

        self.volume = read_only_text_value(self)
        self.pan = read_only_text_value(self)
        self.vibe = wx.StaticBitmap(
            self, wx.ID_ANY, wx.BitmapFromImage(EMPTY_VIBE))
        self.synth = read_only_text_value(self)
        self.play = read_only_text_value(self)
        self.length = read_only_text_value(self)
        self.repeat = read_only_text_value(self)
        self.speed = read_only_text_value(self)
        self.automate = read_only_text_value(self)
        self.table = read_only_text_value(self)

        self.add_field("Volume", self.volume)
        self.add_field("Output", self.pan)
        self.add_field("Vib. Type", self.vibe)
        self.add_field("Synth", self.synth)
        self.add_field("Play", self.play)
        self.add_field("Length", self.length)
        self.add_field("Repeat", self.repeat)
        self.add_field("Speed", self.speed)
        self.add_field("Automate", self.automate)
        self.add_field("Table", self.table)


    def update_view(self, data):
        instr = data

        self.volume.SetValue("%02x" % (instr.volume))
        self.pan.SetValue(instr.pan)

        self.vibe.SetBitmap(
            wx.BitmapFromImage(VIBE_IMAGES[instr.vibrato.type]))

        self.synth.SetValue("%x" % (instr.synth))
        self.play.SetValue(instr.play_type)
        self.length.SetValue("%x" % (instr.steps))
        self.repeat.SetValue("%x" % (instr.repeat))
        self.speed.SetValue("%x" % (instr.speed))

        if instr.automate_1:
            self.automate.SetValue("ON")
        else:
            self.automate.SetValue("OFF")

        if instr.table is None:
            self.table.SetValue("OFF")
        else:
            self.table.SetValue("%02x" % (instr.table.index))


class KitInstrumentPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent, channels.KIT_CHANGE)

        self.kit_1 = read_only_text_value(self)
        self.kit_2 = read_only_text_value(self)
        self.volume = read_only_text_value(self)
        self.pan = read_only_text_value(self)
        self.pitch = read_only_text_value(self)
        self.offset_1 = read_only_text_value(self)
        self.offset_2 = read_only_text_value(self)
        self.len_1 = read_only_text_value(self)
        self.len_2 = read_only_text_value(self)
        self.loop_1 = read_only_text_value(self)
        self.loop_2 = read_only_text_value(self)
        self.speed = read_only_text_value(self)
        self.dist = read_only_text_value(self)
        self.vibe = wx.StaticBitmap(
            self, wx.ID_ANY, wx.BitmapFromImage(EMPTY_VIBE))
        self.automate = read_only_text_value(self)
        self.table = read_only_text_value(self)

        self.add_compound_field("Kit", self.kit_1, self.kit_2)
        self.add_field("Volume", self.volume)
        self.add_field("Output", self.pan)
        self.add_field("Pitch", self.pitch)
        self.add_compound_field("Offset", self.offset_1, self.offset_2)
        self.add_compound_field("Len", self.len_1, self.len_2)
        self.add_compound_field("Loop", self.loop_1, self.loop_2)

        speed_sizer = wx.BoxSizer(wx.HORIZONTAL)
        speed_sizer.Add(self.speed, wx.ALL | wx.EXPAND)
        speed_sizer.Add(wx.StaticText(self, label='X'))
        self.add_field("Speed", speed_sizer)
        self.add_field("Dist", self.dist)
        self.add_field("Vib. Type", self.vibe)
        self.add_field("Automate", self.automate)
        self.add_field("Table", self.table)

    def update_view(self, data):
        instr = data

    def add_compound_field(self, name, elt1, elt2):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(elt1, wx.ALL | wx.EXPAND)
        sizer.Add(wx.StaticText(self, label="/"), wx.ALL | wx.EXPAND)
        sizer.Add(elt2, wx.ALL | wx.EXPAND)

        self.add_field(name, sizer)

class NoiseInstrumentPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent, channels.NOISE_CHANGE)

        self.envelope = read_only_text_value(self)
        self.pan = read_only_text_value(self)
        self.length = read_only_text_value(self)
        self.shape = read_only_text_value(self)
        self.s_cmd = read_only_text_value(self)

        self.automate = read_only_text_value(self)
        self.table = read_only_text_value(self)

        self.add_field("Envelope", self.envelope)
        self.add_field("Output", self.pan)
        self.add_field("Length", self.length)
        self.add_field("Shape", self.shape)
        self.add_field("S Cmd", self.s_cmd)
        self.add_field("Automate", self.automate)
        self.add_field("Table", self.table)

    def update_view(self, data):
        instr = data

        self.envelope.SetValue("%02x" % (instr.envelope))
        self.pan.SetValue(instr.pan)

        if instr.has_sound_length:
            length = "%02x" % (instr.sound_length)
        else:
            length = "UNLIM"

        self.length.SetValue(length)

        self.shape.SetValue("%02x" % (instr.sweep))
        self.s_cmd.SetValue(instr.s_cmd)

        if instr.automate_1:
            self.automate.SetValue("ON")
        else:
            self.automate.SetValue("OFF")

        if instr.table is None:
            self.table.SetValue("OFF")
        else:
            self.table.SetValue("%02x" % (instr.table.index))
