from InstrumentPanel import InstrumentPanel

import channels

from viewutils import two_digit_hex_format, len_format, automate_format, \
    table_format, instr_attr

from ReadOnlyTextViewField import ReadOnlyTextViewField


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
