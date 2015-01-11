from InstrumentPanel import InstrumentPanel

import channels

from viewutils import one_digit_hex_format, two_digit_hex_format, instr_attr, \
    table_format, automate_format, synth_format

from VibeTypeViewField import VibeTypeViewField
from ReadOnlyTextViewField import ReadOnlyTextViewField

class WaveInstrumentPanel(InstrumentPanel):
    def __init__(self, parent):
        InstrumentPanel.__init__(self, parent, channels.WAVE_CHANGE)

        self.volume = ReadOnlyTextViewField(
            self, two_digit_hex_format("volume"))
        self.pan = ReadOnlyTextViewField(self, instr_attr("pan"))
        self.vibe = VibeTypeViewField(self)
        self.synth = ReadOnlyTextViewField(self, synth_format)
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
