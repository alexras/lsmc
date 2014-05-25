import json, os
import wx, functools, event_handlers
from wx.lib.pubsub import pub
from ObjectListView import ColumnDefn

import channels

import utils

import common.utils as cu

from StaticTextViewField import StaticTextViewField
from ReadOnlyTextViewField import ReadOnlyTextViewField
from ImageSetViewField import ImageSetViewField
from ViewField import ViewField

VIBE_IMAGES = [
    wx.Image("images/vibe_hfsine.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/vibe_saw.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/vibe_sine.gif", wx.BITMAP_TYPE_GIF),
    wx.Image("images/vibe_square.gif", wx.BITMAP_TYPE_GIF)
]

def name_empty(name):
    return map(ord, name) == [0] * len(name)

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

def read_only_text_value(parent):
    return wx.TextCtrl(parent, style=wx.TE_READONLY)

class InstrumentPane(wx.Panel):
    def __init__(self, parent, project):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.project = project

        self.instr_list = utils.new_obj_list_view(self)
        self.instr_list.SetEmptyListMsg("Loading instrument list ...")

        def instr_name_printer(x):
            name = getattr(x, "name")

            if name_empty(name):
                return "[UNNAMED]"
            else:
                return name

        id_col = ColumnDefn("#", "center", 30, lambda x: "%02x" %
                            (getattr(x, "index")))
        name_col = ColumnDefn(
            "Name", "left", 200, instr_name_printer, isSpaceFilling=True)
        type_col = ColumnDefn("Type", "left", 50, "type", isSpaceFilling=True)
        self.instr_list.SetColumns([id_col, name_col, type_col])

        self.refresh_instr_list()

        self.instr_panels = {
            None: NoInstrumentSelectedPanel(self),
            "pulse": PulseInstrumentPanel(self),
            "wave": WaveInstrumentPanel(self),
            "kit": KitInstrumentPanel(self),
            "noise": NoiseInstrumentPanel(self)
        }

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.handle_instr_changed,
                  self.instr_list)

        pub.subscribe(self.handle_instr_changed, channels.INSTR_IMPORT)
        pub.subscribe(self.update_instr_list, channels.INSTR_IMPORT)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(self.instr_list, 1, wx.ALL | wx.EXPAND, border=5)

        for panel in self.instr_panels.values():
            sizer.Add(panel, 1, wx.EXPAND)

        self.SetSizer(sizer)

        self.show_instr_panel(None)

    def update_instr_list(self, data):
        self.instr_list.SetObjects(self.project.song.instruments.as_list())

    def refresh_instr_list(self):
        self.instr_list.SetObjects(self.project.song.instruments.as_list())

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

    def handle_instr_changed(self, data):
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

        self.instrument = None

        self.pubsub_channel = channel

        if channel is not None:
            pub.subscribe(self._set_instrument, self.pubsub_channel)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_sizer = wx.FlexGridSizer(cols=2, hgap=20, vgap=10)

        if channel is not None:
            self.add_header_gui()

        self.sizer.Add(self.main_sizer, wx.EXPAND | wx.ALL)

        if channel is not None:
            self.add_footer_gui()

        self.SetSizer(self.sizer)

    def _set_instrument(self, data):
        self.instrument = data

    def add_header_gui(self):
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        def header_format(instr):
            return "Instrument %02x" % (instr.index)

        self.instrument_name = StaticTextViewField(self, header_format)
        self.instrument_name.subscribe(self.pubsub_channel)
        self.instrument_name.add_to_sizer(header_sizer, 1, wx.ALL)

        self.sizer.Add(header_sizer, 1, wx.EXPAND | wx.ALL)
        self.sizer.AddSpacer(10)

    def add_footer_gui(self):
        import_button = wx.Button(self, wx.ID_ANY, label="Import ...")
        export_button = wx.Button(self, wx.ID_ANY, label="Export ...")

        self.Bind(wx.EVT_BUTTON, self.import_instrument, import_button)
        self.Bind(wx.EVT_BUTTON, self.export_instrument, export_button)

        bottom_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bottom_buttons_sizer.Add(import_button, 1, wx.EXPAND | wx.ALL)
        bottom_buttons_sizer.AddSpacer(10)
        bottom_buttons_sizer.Add(export_button, 1, wx.EXPAND | wx.ALL)

        self.sizer.AddSpacer(15)
        self.sizer.Add(bottom_buttons_sizer, .2, wx.EXPAND | wx.ALL)
        self.sizer.AddSpacer(5)

    def add_field(self, label_text, control, fields=None):
        label = wx.StaticText(self, label=label_text)

        if fields is None:
            fields = [control]

        self.main_sizer.Add(label, 0, wx.ALL)

        map(lambda x: x.subscribe(self.pubsub_channel), fields)
        self.num_fields += len(fields)

        if isinstance(control, ViewField):
            control.add_to_sizer(self.main_sizer, 0, wx.ALL)
        else:
            self.main_sizer.Add(control, 0, wx.ALL)

    def change_instrument(self, instrument):
        # Reset updated fields count since we're about to start changing fields.
        self.updated_fields = 0
        pub.sendMessage(self.pubsub_channel, data=instrument)

    def import_instrument(self, event):
        def ok_handler(dlg, path):
            with open(path, 'r') as fp:
                self.instrument.import_lsdinst(json.load(fp))

            pub.sendMessage(channels.INSTR_IMPORT, data=self.instrument)

        utils.file_dialog(
            "Load instrument", "*.lsdinst", wx.OPEN, ok_handler)

    def export_instrument(self, event):
        def ok_handler(dlg, path):
            instr_json = self.instrument.export()

            with open(path, 'w') as fp:
                json.dump(instr_json, fp, indent=2)

        if not name_empty(self.instrument.name):
            default_file = '%s.lsdinst' % (self.instrument.name)
        else:
            default_file = ''

        utils.file_dialog(
            "Save instrument as ...", "*.lsdinst", wx.SAVE, ok_handler,
            default_file=default_file)

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

        self.main_sizer.Add(info_text, 1, wx.ALL | wx.EXPAND)

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
        self.speed.add_to_sizer(speed_sizer, wx.ALL | wx.EXPAND)
        speed_sizer.Add(wx.StaticText(self, label='X'))
        self.add_field("Speed", speed_sizer, fields=[self.speed])

        self.add_field("Dist", self.dist)
        self.add_field("Vib. Type", self.vibe)
        self.add_field("Automate", self.automate)
        self.add_field("Table", self.table)

    def add_compound_field(self, name, elt1, elt2):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        elt1.add_to_sizer(sizer, 1, wx.ALL)
        sizer.Add(wx.StaticText(self, label="/"), 0.2, wx.ALL)
        elt2.add_to_sizer(sizer, 1, wx.ALL)

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
