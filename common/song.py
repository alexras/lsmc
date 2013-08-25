# Number of channels
NUM_CHANNELS = 4

def _assert_index_sane(self, index, upper_bound_exclusive):
    assert type(index) == int, "Indices should be integers"
    assert 0 <= index < upper_bound_exclusive, (
        "Index %d out of range [%d, %d)" % (index, 0, upper_bound_exclusive))

class AllocTable(object):
    def __init__(self, song_data, alloc_table, object_class, field_prefix,
                 fields):
        self.alloc_table = alloc_table
        self.song_data = song_data
        self.object_class = object_class
        self.field_prefix = field_prefix
        self.fields = fields

    def _get_song_data_field(self, field):
        full_field_name = self.field_prefix + field

        assert hasattr(self.song_data, full_field_name), (
            "Can't find field '%s' in song data" % (full_field_name))

        song_data_field = getattr(self.song_data, full_field_name)

        assert type(song_data_field) == list, (
            "Expect to be pulling field data from arrays")
        assert len(song_data_field) == len(self.alloc_table), (
            "Expected song data field '%s' to have %d elements, "
            "but it has %d" % (full_field_name, len(self.alloc_table),
                               len(song_data_field)))

    def __getitem__(self, index):
        _assert_index_sane(index, len(self.alloc_table))

        if not self.alloc_table[index]:
            # The object isn't allocated
            return None

        # Construct the arguments for the class' constructor by retrieving the
        # data from appropriate fields in the song data object. In particular,
        # we're assuming that the fields we're looking at in the song data
        # object are arrays, and that the relevant piece of data for each
        # constructor parameter is at index `index` in its corresponding array.
        constructor_args = {}

        for field in self.fields:
            song_data_field = self._get_song_data_field(field)
            constructor_args[field] = song_data_field[index]

        return self.object_class(**constructor_args)

    def __setitem__(self, index, value_obj):
        _assert_index_sane(index, len(self.alloc_table))

        assert type(value_obj) == self.object_class, (
            "Can only set objects of type '%s'" % (self.object_class))

        # Whether or not the field was allocated before, it's allocated now.
        self.alloc_table[index] = True

        for field in self.fields:
            assert hasattr(value_obj, field), (
                "Class %s doesn't have field '%s'" % (self.object_class, field))

            song_data_field = self._get_song_data_field(field)
            song_data_field[index] = getattr(value_obj, field)

class Instruments(object):
    classes = {
        "pulse": Pulse,
        "wave": Wave,
        "kit": Kit,
        "noise": Noise
    }

    def __init__(self, song_data):
        self.song_data = song_data

    def __getitem__(self, index):
        _assert_index_sane(index, len(self.song_data.instruments))

        if not self.song_data.instr_alloc_table[index]:
            return None

        instr_data = self.song_data.instruments[index]

        return Instruments.classes[instr_data.instrument_type](
            song_data, index)

    def __setitem__(self, index, value_obj):
        _assert_index_sane(index, len(self.song_data.instruments))

        assert type(value_obj) in Instruments.classes.values(), (
            "Instrument type must be one of '%s'" % (
                Instruments.classes.values()))

        # Instrument is now allocated
        self.song_data.instr_alloc_table[index] = True
        self.song_data.instruments[index] = value_obj.parsed_data

class Grooves(object):
    def __init__(self, song_data):
        self.song_data = song_data

    def __getitem__(self, index):
        _assert_index_sane(index, len(self.song_data.grooves))

        return Groove(self.song_data.grooves[index])

class Sequence(object):
    PU1 = "pu1"
    PU2 = "pu2"
    WAV = "wav"
    NOI = "noi"

    def __init__(self, song_data):
        self.song_data = song_data

    def __getitem__(self, index):
        _assert_index_sane(index, len(self.song_data.song))
        raw_chain = self.song_data.song[index]

        chain_objs = {}

        for channel in [Sequence.PU1, Sequence.PU2, Sequence.WAV, Sequence.NOI]:
            chain_number = getattr(raw_chain, channel)

            if self.song_data.chain_alloc_table[chain_number]:
                chain_objs[channel] = self._chains[chain_number]

    def __setitem__(self, index, value_dict):
        _assert_index_sane(index, len(self.song_data.song))

        for channel in value_dict:
            assert (channel in
                    [Sequence.PU1, Sequence.PU2, Sequence.WAV, Sequence.NOI],
                    "Channel '%d' is not a valid channel" % (channel))

            chain_number = value_dict[channel]

            _assert_index_sane(chain_number,
                               len(self.song_data.chain_alloc_table))

            assert self.song_data.chain_alloc_table[chain_number], (
                "Assigning a chain (%d) that has not been allocated" % (
                    chain_number))

            setattr(self.song_data.song[index], channel, chain_number)

class Synths(object):
    def __init__(self, song_data):
        self.song_data = song_data

    def __getitem__(self, index):
        _assert_index_sane(index, len(self.song_data.softsynth_params))

        return Synth(self.song_data, index)

class Song(object):
    """A song consists of a sequence of chains, one per channel.
    """
    def __init__(self, song_data):
        # Check checksums
        assert song_data.mem_init_flag_1 == 'rb'
        assert song_data.mem_init_flag_2 == 'rb'
        assert song_data.mem_init_flag_3 == 'rb'

        # Everything we do to the song or any of its components should update
        # the song data object, so that we can rely on bread's writer to write
        # it back out in the right format
        self.song_data = song_data

        # Stitch together allocated phrases
        self._phrases = AllocTable(
            alloc_table = self.song_data.phrase_alloc_table,
            object_class = Phrase,
            field_prefix = "phrase_",
            fields = ["notes", "fx", "fx_val", "instruments"])

        # Stitch together allocated chains
        self._chains = AllocTable(
            alloc_table = self.song_data.chain_alloc_table,
            object_class = Chain,
            field_prefix = "chain_",
            fields = ["phrases", "transposes"])

        # Stitch together allocated tables
        self._tables = AllocTable(
            alloc_table = self.song_data.table_alloc_table,
            object_class = Table,
            field_prefix = "table_",
            fields = ["transposes", "fx", "fx_val", "fx2", "fx2_val",
                      "envelope"])

        self._instruments = Instruments(self.song_data)
        self._grooves = Grooves(self.song_data)
        self._speech_instrument = SpeechInstrument(self.song_data)
        self._synths = Synths(self.song_data)

    @property
    def clock(self):
        return Clock(self.song_data.clock)

    @property
    def global_clock(self):
        return Clock(self.song_data.global_clock)

    @property
    def phrases(self):
        return self._phrases

    @property
    def chains(self):
        return self._chains

    @property
    def grooves(self):
        return self._grooves

    @property
    def song_version(self):
        return self.song_data.version

    @song_version.setter
    def song_version(self, version):
        self.song_data.version = version

    @property
    def speech_instrument(self):
        return self._speech_instrument

    @property
    def synths(self):
        return self._synths

# For fields with a one-to-one correspondence with song data, we'll
# programmatically insert properties to avoid repetition
for field in ["tempo", "tune_setting", "key_delay", "key_repeat",
              "font", "sync_setting", "colorset", "clone",
              "file_changed", "power_save", "prelisten", "bookmarks",
              "wave_synth_overwrite_lock"]:
    def field_getter(self):
        return getattr(self.song_data, field)

    def field_setter(self, value):
        setattr(self.song_data, field, value)

    setattr(Song, field, property(fset=field_setter, fget=field_getter))
