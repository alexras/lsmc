SOUND_LENGTH_UNLIM = -1

class PulseInstrument(object):
    def __init__(self, name, raw_instr):
        self.name = name
        self.vibrato_type = raw_instr.vibrato.type
        self.vibrato_direction = raw_instr.vibrato.direction

        important_fields = [
            "envelope",
            "phase_transpose",
            "sound_length",
            "has_sound_length",
            "sweep",
            "automate_1",
            "automate_2",
            "table_on",
            "table",
            "wave",
            "phase_finetune",
            "pan"]

        for field in important_fields:
            setattr(self, field, getattr(raw_instr, field))
