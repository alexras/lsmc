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

def vibe_type_field(parent):
    return ImageSetViewField(
        parent, lambda instr: instr.vibrato.type, VIBE_IMAGES)

def instr_attr(attr):
    def instr_attr_format_fn(instr):
        return getattr(instr, attr)

    return instr_attr_format_fn

def two_digit_hex_format(attr):
    def two_digit_hex_format_fn(instr):
        return "%02x" % (getattr(instr, attr))

    return two_digit_hex_format_fn

def one_digit_hex_format(attr):
    def one_digit_hex_format_fn(instr):
        return "%x" % (getattr(instr, attr))

    return one_digit_hex_format_fn

def len_format(instr):
    if instr.has_sound_length:
        return "%02x" % (instr.sound_length)
    else:
        return "UNLIM"

def kit_len_format(attr):
    def kit_len_format_fn(instr):
        kit_len = getattr(instr, attr)

        if kit_len == 0:
            return "AUT"
        else:
            return "%02x" % (kit_len)

    return kit_len_format_fn

def kit_loop_format(loop_attr, attack_attr):
    def kit_loop_format_fn(instr):
        kit_loop = getattr(instr, loop_attr)
        kit_attack = getattr(instr, attack_attr)

        if kit_attack:
            return "ATK"
        elif kit_loop == 1:
            return "ON"
        else:
            return "OFF"

    return kit_loop_format_fn

def kit_speed_format(instr):
    if instr.half_speed:
        return "0.5"
    else:
        return "1"

def automate_format(instr):
    if instr.automate_1:
        return "ON"
    else:
        return "OFF"

def table_format(instr):
    if instr.table is None:
        return "OFF"
    else:
        return "%02x" % (instr.table.index)

class ViewField(object):
    def __init__(self, parent, field):
        self.parent = parent
        self.field = field

    def subscribe(self, channel):
        pub.subscribe(self.update, channel)

    def update(self, data):
        self.parent.field_changed()

class ReadOnlyTextViewField(ViewField):
    def __init__(self, parent, format_fn):
        ViewField.__init__(
            self, parent, wx.TextCtrl(parent, style=wx.TE_READONLY))
        self.format_fn = format_fn

    def update(self, data):
        instr = data

        self.field.SetValue(self.format_fn(instr))
        super(ReadOnlyTextViewField, self).update(data)

class ImageSetViewField(ViewField):
    def __init__(self, parent, attr_fn, image_array):
        empty_img = wx.BitmapFromImage(wx.EmptyImage(
            image_array[0].GetWidth(), image_array[0].GetHeight()))
        ViewField.__init__(
            self, parent, wx.StaticBitmap(parent, wx.ID_ANY, empty_img))
        self.image_array = image_array
        self.attr_fn = attr_fn

    def update(self, data):
        instr = data

        self.field.SetBitmap(wx.BitmapFromImage(
            self.image_array[self.attr_fn(instr)]))
        super(ImageSetViewField, self).update(data)


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

        id_col = ColumnDefn("#", "center", 30, lambda x: "%02x" %
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

        self.num_fields = 0
        self.updated_fields = 0

        self.pubsub_channel = channel
        self.sizer = wx.GridSizer(rows=0, cols=2)

        self.SetSizer(self.sizer)

    def add_field(self, label_text, control, fields=None):
        label = wx.StaticText(self, label=label_text)

        if fields is None:
            fields = [control]

        self.sizer.Add(label, 0, wx.ALL)

        map(lambda x: x.subscribe(self.pubsub_channel), fields)
        self.num_fields += len(fields)

        if isinstance(control, ViewField):
            self.sizer.Add(control.field, 0, wx.ALL)
        else:
            self.sizer.Add(control, 0, wx.ALL)

    def change_instrument(self, instrument):
        # Reset updated fields count since we're about to start changing fields.
        self.updated_fields = 0
        pub.sendMessage(self.pubsub_channel, data=instrument)

    def field_changed(self):
        """
        We want to call self.Layout() only when all fields have been updated to
        reflect the new instrument. Each field will call this method on its
        parent, and when all fields have updated, we'll trigger a re-layout.
        """

        self.updated_fields += 1

        if self.updated_fields == self.num_fields:
            self.Layout()

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

        self.envelope = ReadOnlyTextViewField(
            self, two_digit_hex_format("envelope"))

        wave_images = [
            wx.Image("images/wave12.5.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/wave25.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/wave50.gif", wx.BITMAP_TYPE_GIF),
            wx.Image("images/wave75.gif", wx.BITMAP_TYPE_GIF)]

        self.wave = ImageSetViewField(self, instr_attr("wave"), wave_images)

        self.pan = ReadOnlyTextViewField(self, instr_attr("pan"))
        self.length = ReadOnlyTextViewField(self, len_format)
        self.sweep = ReadOnlyTextViewField(self, two_digit_hex_format("sweep"))
        self.vibe = vibe_type_field(self)
        self.pu2_tune = ReadOnlyTextViewField(
            self, two_digit_hex_format("phase_transpose"))
        self.pu_fine = ReadOnlyTextViewField(
            self, one_digit_hex_format("phase_finetune"))
        self.automate = ReadOnlyTextViewField(self, automate_format)
        self.table = ReadOnlyTextViewField(self, table_format)

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

class WaveInstrumentPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent, channels.WAVE_CHANGE)

        self.volume = ReadOnlyTextViewField(
            self, two_digit_hex_format("volume"))
        self.pan = ReadOnlyTextViewField(self, instr_attr("pan"))
        self.vibe = vibe_type_field(self)
        self.synth = ReadOnlyTextViewField(self, one_digit_hex_format("synth"))
        self.play = ReadOnlyTextViewField(self, instr_attr("play_type"))
        self.length = ReadOnlyTextViewField(self, one_digit_hex_format("steps"))
        self.repeat = ReadOnlyTextViewField(
            self, one_digit_hex_format("repeat"))
        self.speed = ReadOnlyTextViewField(self, one_digit_hex_format("speed"))
        self.automate = ReadOnlyTextViewField(self, automate_format)
        self.table = ReadOnlyTextViewField(self, table_format)

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

class KitInstrumentPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent, channels.KIT_CHANGE)

        self.kit_1 = ReadOnlyTextViewField(self, two_digit_hex_format("kit"))
        self.kit_2 = ReadOnlyTextViewField(self, two_digit_hex_format("kit_2"))
        self.volume = ReadOnlyTextViewField(
            self, one_digit_hex_format("volume"))
        self.pan = ReadOnlyTextViewField(self, instr_attr("pan"))
        self.pitch = ReadOnlyTextViewField(self, two_digit_hex_format("pitch"))
        self.offset_1 = ReadOnlyTextViewField(
            self, two_digit_hex_format("offset"))
        self.offset_2 = ReadOnlyTextViewField(
            self, two_digit_hex_format("offset_2"))
        self.len_1 = ReadOnlyTextViewField(self, kit_len_format("length_1"))
        self.len_2 = ReadOnlyTextViewField(self, kit_len_format("length_2"))
        self.loop_1 = ReadOnlyTextViewField(
            self, kit_loop_format("loop_1", "keep_attack_1"))
        self.loop_2 = ReadOnlyTextViewField(
            self, kit_loop_format("loop_2", "keep_attack_2"))
        self.speed = ReadOnlyTextViewField(self, kit_speed_format)
        self.dist = ReadOnlyTextViewField(self, instr_attr("dist_type"))
        self.vibe = vibe_type_field(self)
        self.automate = ReadOnlyTextViewField(self, automate_format)
        self.table = ReadOnlyTextViewField(self, table_format)

        self.add_compound_field("Kit", self.kit_1, self.kit_2)
        self.add_field("Volume", self.volume)
        self.add_field("Output", self.pan)
        self.add_field("Pitch", self.pitch)
        self.add_compound_field("Offset", self.offset_1, self.offset_2)
        self.add_compound_field("Len", self.len_1, self.len_2)
        self.add_compound_field("Loop", self.loop_1, self.loop_2)

        speed_sizer = wx.BoxSizer(wx.HORIZONTAL)
        speed_sizer.Add(self.speed.field, wx.ALL | wx.EXPAND)
        speed_sizer.Add(wx.StaticText(self, label='X'))
        self.add_field("Speed", speed_sizer, fields=[self.speed])

        self.add_field("Dist", self.dist)
        self.add_field("Vib. Type", self.vibe)
        self.add_field("Automate", self.automate)
        self.add_field("Table", self.table)

    def add_compound_field(self, name, elt1, elt2):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(elt1.field, 1, wx.ALL)
        sizer.Add(wx.StaticText(self, label="/"), 0.2, wx.ALL)
        sizer.Add(elt2.field, 1, wx.ALL)

        self.add_field(name, sizer, (elt1, elt2))

class NoiseInstrumentPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent, channels.NOISE_CHANGE)

        self.envelope = ReadOnlyTextViewField(
            self, two_digit_hex_format("envelope"))
        self.pan = ReadOnlyTextViewField(self, instr_attr("pan"))
        self.length = ReadOnlyTextViewField(self, len_format)
        self.shape = ReadOnlyTextViewField(self, two_digit_hex_format("sweep"))
        self.s_cmd = ReadOnlyTextViewField(self, instr_attr("s_cmd"))

        self.automate = ReadOnlyTextViewField(self, automate_format)
        self.table = ReadOnlyTextViewField(self, table_format)

        self.add_field("Envelope", self.envelope)
        self.add_field("Output", self.pan)
        self.add_field("Length", self.length)
        self.add_field("Shape", self.shape)
        self.add_field("S Cmd", self.s_cmd)
        self.add_field("Automate", self.automate)
        self.add_field("Table", self.table)
