from InstrumentPanel import InstrumentPanel

import wx

import channels

from viewutils import one_digit_hex_format, two_digit_hex_format, \
    len_format, automate_format, table_format, instr_attr

from VibeTypeViewField import VibeTypeViewField
from ReadOnlyTextViewField import ReadOnlyTextViewField
from ImageSetViewField import ImageSetViewField
from WaveViewField import WaveViewField

class PulseInstrumentPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent, channels.PULSE_CHANGE)

        self.envelope = ReadOnlyTextViewField(
            self, two_digit_hex_format("envelope"))

        self.wave = WaveViewField(self)

        self.pan = ReadOnlyTextViewField(self, instr_attr("pan"))
        self.length = ReadOnlyTextViewField(self, len_format)
        self.sweep = ReadOnlyTextViewField(self, two_digit_hex_format("sweep"))
        self.vibe = VibeTypeViewField(self)
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
