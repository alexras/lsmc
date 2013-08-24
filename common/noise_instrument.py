SOUNDLENGTH_UNLIM = 0

class NoiseInstrument(object):
    def __init__(self, name, raw_instr):
        self.name = name

        important_fields = [
            "envelope",
            "sound_length",
            "sound_length_unlim",
            "sweep",
            "automate_1",
            "automate_2",
            "has_table",
            "table_number"
            ]

        for field in important_fields:
            setattr(self, field, getattr(raw_instr, field))
