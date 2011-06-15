from instrument import Instrument, InstrumentProperty

SOUND_LENGTH_UNLIM = -1

class PulseInstrument(Instrument):
    def __init__(self):
        super(PulseInstrument,self).__init__()

        self.property_info = {
            "envelope" : InstrumentProperty(1),
            "phase_transpose" : InstrumentProperty(2),
            "sound_length" : InstrumentProperty(3, 0, 5),
            "sound_length_unlim" : InstrumentProperty(3, 6, 6),
            "sweep" : InstrumentProperty(4),
            "automate_1" : InstrumentProperty(5, 4, 4),
            "automate_2" : InstrumentProperty(5, 3, 3),
            "vibrato_type" : InstrumentProperty(5, 1, 2),
            "vibrato_direction" : InstrumentProperty(5, 0, 0),
            "has_table" : InstrumentProperty(6, 5, 5),
            "table_number" : InstrumentProperty(6, 0, 4),
            "wave_number" : InstrumentProperty(7, 6, 7),
            "phase_finetune" : InstrumentProperty(7, 2, 5),
            "pan" : InstrumentProperty(7, 0, 1)
        }

        for key, value in self.property_info.items():
            setattr(self.__class__, key,
                    property(value.prop_getter, value.prop_setter))
