from instrument import Instrument, InstrumentProperty

PLAY_TYPE_ONCE = 0
PLAY_TYPE_LOOP = 1
PLAY_TYPE_PINGPONG = 2
PLAY_TYPE_MANUAL = 3

class WaveInstrument(Instrument):
    def __init__(self):
        super(WaveInstrument,self).__init__()

        self.property_info = {
            "volume" : InstrumentProperty(1),
            "synth"  : InstrumentProperty(2, 4, 7),
            "repeat" : InstrumentProperty(2, 0, 3),
            "automate_1" : InstrumentProperty(5, 4, 4),
            "automate_2" : InstrumentProperty(5, 3, 3),
            "vibrato_type" : InstrumentProperty(5, 1, 2),
            "vibrato_direction" : InstrumentProperty(5, 0, 0),
            "has_table" : InstrumentProperty(6, 5, 5),
            "table_number" : InstrumentProperty(6, 0, 4),
            "pan" : InstrumentProperty(7, 0, 1),
            "play_type" : InstrumentProperty(9, 0, 1),
            "steps" : InstrumentProperty(14, 4, 7),
            "speed" : InstrumentProperty(14, 0, 3)
        }

        for key, value in self.property_info.items():
            setattr(self.__class__, key,
                    property(value.prop_getter, value.prop_setter))
