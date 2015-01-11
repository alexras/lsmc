import wx

import channels

from InstrumentPanel import InstrumentPanel

from ReadOnlyTextViewField import ReadOnlyTextViewField
from VibeTypeViewField import VibeTypeViewField

from viewutils import instr_attr, one_digit_hex_format, \
    two_digit_hex_format, automate_format, table_format


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


class KitInstrumentPanel(InstrumentPanel):

    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent, channels.KIT_CHANGE)

        self.kit_1 = ReadOnlyTextViewField(self, two_digit_hex_format("kit_1"))
        self.kit_2 = ReadOnlyTextViewField(self, two_digit_hex_format("kit_2"))
        self.volume = ReadOnlyTextViewField(
            self, one_digit_hex_format("volume"))
        self.pan = ReadOnlyTextViewField(self, instr_attr("pan"))
        self.pitch = ReadOnlyTextViewField(self, two_digit_hex_format("pitch"))
        self.offset_1 = ReadOnlyTextViewField(
            self, two_digit_hex_format("offset_1"))
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
        self.vibe = VibeTypeViewField(self)
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
