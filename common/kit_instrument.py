from instrument import Instrument, InstrumentProperty

LENGTH_AUTO = 0

class KitInstrument(object):
    def __init__(self, name, raw_instr):
        self.name = name
        self.vibrato_type = raw_instr.vibrato.type
        self.vibrato_direction = raw_instr.vibrato.direction

        important_fields = [
            "volume",
            "keep_attack_2",
            "half_speed",
            "kit",
            "length_1",
            "loop_1",
            "loop_2",
            "automate_1",
            "automate_2",
            "vibrato_type",
            "vibrato_direction",
            "has_table",
            "table_number",
            "pan",
            "pitch",
            "keep_attack_2",
            "kit_2",
            "dist_type",
            "length_2",
            "offset",
            "offset_2"
            ]

        for field in important_fields:
            setattr(self, field, getattr(raw_instr, field))
