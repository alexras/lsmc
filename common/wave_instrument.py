class WaveInstrument(object):
    def __init__(self, name, raw_instr):
        self.name = name
        self.vibrato_type = raw_instr.vibrato.type
        self.vibrato_direction = raw_instr.vibrato.direction

        important_fields = [
            "volume",
            "synth" ,
            "repeat",
            "automate_1",
            "automate_2",
            "table_on",
            "table",
            "pan",
            "play_type",
            "steps",
            "speed"
        ]

        for field in important_fields:
            setattr(self, field, getattr(raw_instr, field))
