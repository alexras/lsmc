from instrument import Instrument, InstrumentProperty

LENGTH_AUTO = 0

class KitInstrument(Instrument):
    def __init__(self):
        super(Instrument, self).__init__()

        self.property_info = {
            "volume" : InstrumentProperty(1),
            "keep_attack_2" : InstrumentProperty(2, 7, 7),
            "half_speed" : InstrumentProperty(2, 6, 6),
            "kit" : InstrumentProperty(2, 0, 5),
            "length_1" : InstrumentProperty(3),
            "loop_1" : InstrumentProperty(5, 6, 6),
            "loop_2" : InstrumentProperty(5, 5, 5),
            "automate_1" : InstrumentProperty(5, 4, 4),
            "automate_2" : InstrumentProperty(5, 3, 3),
            "vibrato_type" : InstrumentProperty(5, 1, 2),
            "vibrato_direction" : InstrumentProperty(5, 0, 0),
            "has_table" : InstrumentProperty(6, 5, 5),
            "table_number" : InstrumentProperty(6, 0, 4),
            "pan" : InstrumentProperty(7, 0, 1),
            "pitch" : InstrumentProperty(8),
            "keep_attack_2" : InstrumentProperty(9, 7, 7),
            "kit_2" : InstrumentProperty(9, 0, 5),
            "dist_type" : InstrumentProperty(10),
            "length_2" : InstrumentProperty(11),
            "offset" : InstrumentProperty(12),
            "offset_2" : InstrumentProperty(13)
            }

        for key, value in self.property_info.items():
            setattr(self.__class__, key,
                    property(value.prop_getter, value.prop_setter))
