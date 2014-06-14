from utils import assert_index_sane
import bread
import bread_spec

from synth import Synth
from table import Table
from phrase import Phrase
from chain import Chain
from speech_instrument import SpeechInstrument
from instrument import Instrument

import StringIO

# Number of channels
NUM_CHANNELS = 4

class AllocTable(object):
    def __init__(self, song, alloc_table, object_class):
        self.alloc_table = alloc_table

        self.access_objects = []

        for index in xrange(len(alloc_table)):
            self.access_objects.append(object_class(song, index))

    def __getitem__(self, index):
        assert_index_sane(index, len(self.alloc_table))

        if not self.alloc_table[index]:
            return None

        return self.access_objects[index]

    def allocate(self, index):
        self.alloc_table[index] = True

    def __len__(self):
        return len(self.alloc_table)

    def as_list(self):
        l = []
        for i in xrange(len(self.alloc_table)):
            if not self.alloc_table[i]:
                l.append(None)
            else:
                l.append(self.access_objects[i])

        return l

    def next_free(self):
        for i, occupied in enumerate(self.alloc_table):
            if not occupied:
                return i
        return None

class Instruments(object):
    specs = {
        "pulse": bread_spec.pulse_instrument,
        "wave": bread_spec.wave_instrument,
        "kit": bread_spec.kit_instrument,
        "noise": bread_spec.noise_instrument
    }

    def __init__(self, song):
        self.song = song
        self.alloc_table = song.song_data.instr_alloc_table
        self.access_objects = []

        for index in xrange(len(self.alloc_table)):
            self.access_objects.append(Instrument(song, index))

    def set_instrument_type(self, index, instrument_type):
        assert instrument_type in Instruments.specs, (
            "Invalid instrument type '%s'" % (instrument_type))

        assert_index_sane(index, len(self.song.song_data.instruments))

        # Need to change the structure of the song's data to match the new
        # instrument type. We'll do this by creating the raw data for an
        # instrument of the appropriate type, parsing a new instrument out of
        # it, and sticking that into the appropriate place in the song's data.

        instrument_length = len(self.song.song_data.instruments[index])

        instrument_type_index = Instruments.specs.keys().index(
            instrument_type)

        empty_bytes = bytearray([instrument_type_index] +
                                ([0] * (instrument_length - 1)))

        parsed_instrument = bread.parse(
            empty_bytes, Instruments.specs[instrument_type])

        self.song.song_data.instruments[index] = parsed_instrument

    def __getitem__(self, index):
        assert_index_sane(index, len(self.alloc_table))

        if not self.alloc_table[index]:
            return None

        return self.access_objects[index]

    def as_list(self):
        return self.access_objects

    def allocate(self, index, instrument_type):
        self.alloc_table[index] = True
        self.set_instrument_type(index, instrument_type)


class Grooves(object):
    def __init__(self, song):
        self.song = song

    def __getitem__(self, index):
        assert_index_sane(index, len(self.song.song_data.grooves))

        return self.song.song_data.grooves[index]

class Sequence(object):
    PU1 = "pu1"
    PU2 = "pu2"
    WAV = "wav"
    NOI = "noi"

    NO_CHAIN = 0xff

    def __init__(self, song):
        self.song = song

    def __getitem__(self, index):
        assert_index_sane(index, len(self.song.song_data.song))
        raw_chain = self.song.song_data.song[index]

        chain_objs = {}

        for channel in [Sequence.PU1, Sequence.PU2, Sequence.WAV, Sequence.NOI]:
            chain_number = getattr(raw_chain, channel)

            if chain_number != Sequence.NO_CHAIN:
                chain = self.song.chains[chain_number]
                chain_objs[channel] = chain

        return chain_objs

    def __setitem__(self, index, value_dict):
        assert_index_sane(index, len(self.song.song_data.song))

        for channel in value_dict:
            assert (channel in [Sequence.PU1, Sequence.PU2, Sequence.WAV,
                                Sequence.NOI]), \
                ("Channel '%d' is not a valid channel" % (channel))

            chain = value_dict[channel]
            chain_number = chain.index

            assert_index_sane(chain_number,
                              len(self.song.song_data.chain_alloc_table))

            assert self.song.song_data.chain_alloc_table[chain_number], (
                "Assigning a chain (%d) that has not been allocated" % (
                    chain_number))

            setattr(self.song.song_data.song[index], channel, chain_number)

    def __str__(self):
        output_str = StringIO.StringIO()

        print >>output_str, "   PU1 PU2 WAV NOI"

        for i, row in enumerate(self.song.song_data.song):
            print >>output_str, "%02x" % (i),

            for channel in ["pu1", "pu2", "wav", "noi"]:
                chain_number = getattr(row, channel)

                if chain_number == Sequence.NO_CHAIN:
                    print >>output_str, " --",
                else:
                    print >>output_str, " %02x" % (getattr(row, channel)),
            print >>output_str, ""

        string = output_str.getvalue()
        return string

class Synths(object):
    def __init__(self, song):
        self.song = song
        self.access_objects = []

        for index in xrange(bread_spec.NUM_SYNTHS):
            self.access_objects.append(Synth(self.song, index))

    def __getitem__(self, index):
        assert_index_sane(index, bread_spec.NUM_SYNTHS)

        return self.access_objects[index]

    def as_list(self):
        return self.access_objects


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

        self._instruments = Instruments(self)

        # Stitch together allocated tables
        self._tables = AllocTable(
            song = self,
            alloc_table = self.song_data.table_alloc_table,
            object_class = Table)

        # Stitch together allocated phrases
        self._phrases = AllocTable(
            song = self,
            alloc_table = self.song_data.phrase_alloc_table,
            object_class = Phrase)

        # Stitch together allocated chains
        self._chains = AllocTable(
            song = self,
            alloc_table = self.song_data.chain_alloc_table,
            object_class = Chain)

        self._grooves = Grooves(self)
        self._speech_instrument = SpeechInstrument(self)
        self._synths = Synths(self)

        self._sequence = Sequence(self)

    def __str__(self):
        output_str = StringIO.StringIO()

        print >>output_str, str(self.sequence)

        string = output_str.getvalue()
        output_str.close()

        return string

    @property
    def instruments(self):
        return self._instruments

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
    def speech_instrument(self):
        return self._speech_instrument

    @property
    def synths(self):
        return self._synths

    @property
    def clock(self):
        return Clock(self.song_data.clock)

    @property
    def global_clock(self):
        return Clock(self.song_data.global_clock)

    @property
    def song_version(self):
        return self.song_data.version

    @song_version.setter
    def song_version(self, version):
        self.song_data.version = version

    @property
    def sequence(self):
        return self._sequence

    @property
    def tables(self):
        return self._tables

# For fields with a one-to-one correspondence with song data, we'll
# programmatically insert properties to avoid repetition
for field in ["tempo", "tune_setting", "key_delay", "key_repeat",
              "font", "sync_setting", "colorset", "clone",
              "file_changed", "power_save", "prelisten", "bookmarks",
              "wave_synth_overwrite_lock"]:
    def field_getter(this):
        return getattr(this.song_data, field)

    def field_setter(this, value):
        setattr(this.song_data, field, value)

    setattr(Song, field, property(fset=field_setter, fget=field_getter))
