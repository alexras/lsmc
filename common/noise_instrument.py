from instrument import Instrument, InstrumentProperty

SOUNDLENGTH_UNLIM = 0

class NoiseInstrument(Instrument):
    def __init__(self):
        super(Instrument, self).__init__()

        self.property_info = {
            "envelope" : InstrumentProperty(1),
            "sound_length" : InstrumentProperty(3, 0, 5),
            "sound_length_unlim" : InstrumentProperty(3, 6, 6),
            "sweep" : InstrumentProperty(4),
            "automate_1" : InstrumentProperty(5, 4, 4),
            "automate_2" : InstrumentProperty(5, 3, 3),
            "has_table" : InstrumentProperty(6, 5, 5),
            "table_number" : InstrumentProperty(6, 0, 4)
            }

        for key, value in self.property_info.items():
            setattr(self.__class__, key,
                    property(value.prop_getter, value.prop_setter))
