import sys
from chain import Chain
from synth import Synth
from wave import Wave
from clock import Clock
from groove import Groove
from instrument import Instrument, SpeechInstrument
from phrase import Phrase
from song import Song
from table import Table
import utils
from blocks import BlockReader

class Project(object):
    # Max. number of phrases
    NUM_PHRASES = 255

    # Max. number of tables
    NUM_TABLES = 32

    # Number of soft-synths
    NUM_SYNTHS = 16

    # Waves per soft-synth
    WAVES_PER_SYNTH = 16

    # Number of entries in each table
    ENTRIES_PER_TABLE = 16

    # Max. number of instruments
    NUM_INSTRUMENTS = 64

    # Max. instrument name length
    INSTRUMENT_NAME_LENGTH = 5

    # Max. number of chains
    NUM_CHAINS = 128

    # Max. number of phrases per chain
    PHRASES_PER_CHAIN = 16

    # Max. number of grooves
    NUM_GROOVES = 32

    # Steps per phrase
    STEPS_PER_PHRASE = 16

    # Steps per groove
    STEPS_PER_GROOVE = 16

    # Number of channels
    NUM_CHANNELS = 4

    # Steps per table
    STEPS_PER_TABLE = 16

    # Max. length of a "word"
    WORD_LENGTH = 0x20

    # Number of "words" in the speech instrument
    NUM_WORDS = 42

    # Max. length of a word name
    WORD_NAME_LENGTH = 4

    # Notes for phrases
    PHRASE_NOTES = (0, 0xfef)

    # Bookmarks
    BOOKMARKS = (0x0ff0, 0x102f)

    # Empty section #1
    EMPTY_SECTION_1 = (0x1030, 0x108f)

    # Grooves
    GROOVES = (0x1090, 0x128f)

    # Chain numbers for song
    CHAINNOS = (0x1290, 0x168f)

    # Envelopes for tables
    TABLE_ENVELOPES = (0x1690, 0x188f)

    # Speech instrument "words"
    SPEECH_INSTR_WORDS = (0x1890, 0x1dcf)

    # Word names
    WORD_NAMES = (0x1dd0, 0x1e77)

    # Mem initialized flag #1 (should be 'rb')
    MEM_INIT_FLAG_1 = (0x1e78, 0x1e79)

    # Instrument names
    INSTR_NAMES = (0x1e7a, 0x1fb9)

    # Empty section #2
    EMPTY_SECTION_2 = (0x2000, 0x201f)

    # Table allocation table (1 for allocated, 0 for unallocated)
    TABLE_ALLOC_TABLE = (0x2020, 0x203f)

    # Instrument allocation table (1 for allocated, 0 for unallocated)
    INSTR_ALLOC_TABLE = (0x2040, 0x207f)

    # Phrase numbers for chains
    CHAIN_PHRASES = (0x2080, 0x287f)

    # Transposes for chains
    CHAIN_TRANSPOSES = (0x2880, 0x307f)

    # Instrument params
    INSTR_PARAMS = (0x3080, 0x347f)

    # Table transposes
    TABLE_TRANSPOSES = (0x3480, 0x367f)

    # Table FX
    TABLE_FX = (0x3680, 0x387f)

    # Table FX values
    TABLE_FX_VALS = (0x3880, 0x3a7f)

    # Table FX 2
    TABLE_FX_2 = (0x3a80, 0x3c7f)

    # Table FX 2 values
    TABLE_FX_2_VALS = (0x3c80, 0x3e7f)

    # "Memory initialized" flag (should be 'rb')
    MEM_INIT_FLAG_2 = (0x3e80, 0x3e81)

    # Phrase allocation table
    PHRASE_ALLOC_TABLE = (0x3e82, 0x3ea1)

    # Chain allocation table
    CHAIN_ALLOC_TABLE = (0x3ea2, 0x3eb1)

    # Soft synth parameters
    SOFT_SYNTH_PARAMS = (0x3eb2, 0x3fb1)

    # Clock
    CLOCK_HOURS = 0x3fb2
    CLOCK_MINUTES = 0x3fb3

    # Tempo
    TEMPO = 0x3fb4

    # Tune setting
    TUNE_SETTING = 0x3fb5

    # Total clock
    TOTAL_CLOCK_DAYS = 0x3fb6
    TOTAL_CLOCK_HOURS = 0x3fb7
    TOTAL_CLOCK_MINUTES = 0x3fb8
    TOTAL_CLOCK_CHECKSUM = 0x3fb9

    # Key delay
    KEY_DELAY = 0x3fba

    # Key repeat
    KEY_REPEAT = 0x3fbb

    # Font
    FONT = 0x3fbc

    # Sync setting
    SYNC_SETTING = 0x3fbd

    # Colorset
    COLORSET = 0x3fbe

    # Empty section #3
    EMPTY_SECTION_3 = (0x3fbf, 0x3fbf)

    # Clone (0 = deep, 1 = slim)
    CLONE = 0x3fc0

    # Has the file changed?
    FILE_CHANGED = 0x3fc1

    # Power save mode
    POWER_SAVE = 0x3fc2

    # Pre-listen mode
    PRELISTEN = 0x3fc3

    # Wave synth overwrite locks
    WAVE_SYNTH_OVERWRITE_LOCKS = (0x3fc4, 0x3fc5)

    # Phrase FX
    PHRASE_FX = (0x4000, 0x4fef)

    # Phrase FX values
    PHRASE_FX_VALS = (0x4ff0, 0x5fdf)

    # Wave frames
    WAVE_FRAMES = (0x6000, 0x6fff)

    # Phrase instruments
    PHRASE_INSTR = (0x7000, 0x7fef)

    # "Memory initialized" flag (should be 'rb')
    MEM_INIT_FLAG_3 = (0x7ff0, 0x7ff1)

    # Empty section #4
    EMPTY_SECTION_4 = (0x7ff2, 0x7ffe)

    # Version byte (0 = < 3.6.0, 1 = 3.6.0, 2 = >= 3.6.1)
    VERSION_BYTE = 0x7fff

    def __init__(self, name, version, blocks):
        self.name = name
        self.version = version

        reader = BlockReader()

        raw_data = reader.read(blocks)

        self.tables = []
        self.instruments = []
        self.phrases = []
        self.chains = []
        self.grooves = []
        self.synths = []
        self.bookmarks = []

        self.song = Song()

        self.clock = Clock()
        self.total_clock = Clock()
        self.tempo = None
        self.tune_setting = None
        self.key_delay = None
        self.key_repeat = None
        self.font = None
        self.sync_setting = None
        self.colorset = None
        self.clone = None

        for i in xrange(self.NUM_TABLES):
            self.tables.append(Table())

        for i in xrange(self.NUM_INSTRUMENTS):
            self.instruments.append(Instrument())

        for i in xrange(self.NUM_PHRASES):
            self.phrases.append(Phrase())

        for i in xrange(self.NUM_CHAINS):
            self.chains.append(Chain())

        for i in xrange(self.NUM_GROOVES):
            self.grooves.append(Groove())

        for i in xrange(self.NUM_SYNTHS):
            synth = Synth()

            for j in xrange(self.WAVES_PER_SYNTH):
                synth.waves.append(Wave())

            self.synths.append(synth)

        self._copy_values_into_list(raw_data, self.PHRASE_NOTES,
                                    self.STEPS_PER_PHRASE,
                                    self.phrases, "notes")

        self.bookmarks = raw_data[self.BOOKMARKS[0] : self.BOOKMARKS[1] + 1]

        self._copy_values_into_list(raw_data, self.GROOVES,
                                    self.STEPS_PER_GROOVE,
                                    self.grooves, "ticks")

        for i in xrange(self.CHAINNOS[0], self.CHAINNOS[1] + 1,
                        self.NUM_CHANNELS):
            self.song.chain_numbers.append(raw_data[i:i + self.NUM_CHANNELS])

        self._copy_values_into_list(raw_data, self.TABLE_ENVELOPES,
                                    self.STEPS_PER_TABLE, self.tables,
                                    "envelopes")

        self.speech_instrument = SpeechInstrument()

        # Speech instrument is always allocated
        speech_instrument.allocated = True

        for i in xrange(self.SPEECH_INSTR_WORDS[0],
                        self.SPEECH_INSTR_WORDS[1] + 1, self.WORD_LENGTH):
            speech_instrument.words.append(raw_data[i:i + self.WORD_LENGTH])

        for i in xrange(self.WORD_NAMES[0], self.WORD_NAMES[1] + 1,
                        self.WORD_NAME_LENGTH):
            speech_instrument.word_names.append(
                raw_data[i:i + self.WORD_NAME_LENGTH])

        utils.check_mem_init_flag(raw_data, self.MEM_INIT_FLAG_1[0],
                                  self.MEM_INIT_FLAG_1[1])

        self._copy_values_into_list(raw_data, self.INSTR_NAMES,
                                    self.INSTRUMENT_NAME_LENGTH,
                                    self.instruments, "name")

        self._copy_from_decompressed_table(
            raw_data, self.TABLE_ALLOC_TABLE, self.tables, "allocated")

        self._copy_from_decompressed_table(
            raw_data, self.INSTR_ALLOC_TABLE, self.instruments, "allocated")

        self._copy_values_into_list(raw_data, self.CHAIN_PHRASES,
                                    self.PHRASES_PER_CHAIN, self.chains,
                                    "phrases")

        self._copy_values_into_list(raw_data, self.CHAIN_TRANSPOSES,
                                    self.PHRASES_PER_CHAIN, self.chains,
                                    "transposes")

        self._copy_values_into_list(raw_data, self.INSTR_PARAMS,
                                    Instrument.NUM_PARAMS,
                                    self.instruments, "params")

        self._copy_values_into_list(raw_data, self.TABLE_TRANSPOSES,
                                    self.ENTRIES_PER_TABLE, self.tables,
                                    "transposes")

        self._copy_values_into_list(raw_data, self.TABLE_FX,
                                    self.ENTRIES_PER_TABLE, self.tables, "fx")

        self._copy_values_into_list(raw_data, self.TABLE_FX_VALS,
                                    self.ENTRIES_PER_TABLE, self.tables,
                                    "fx_vals")

        self._copy_values_into_list(raw_data, self.TABLE_FX_2,
                                    self.ENTRIES_PER_TABLE, self.tables, "fx2")

        self._copy_values_into_list(raw_data, self.TABLE_FX_2_VALS,
                                    self.ENTRIES_PER_TABLE, self.tables,
                                    "fx2_vals")

        utils.check_mem_init_flag(raw_data, self.MEM_INIT_FLAG_2[0],
                                  self.MEM_INIT_FLAG_2[1])

        self._decompress_alloc_table(raw_data, self.PHRASE_ALLOC_TABLE,
                                     self.phrases, "allocated",
                                     self.NUM_PHRASES)

        self._decompress_alloc_table(raw_data, self.CHAIN_ALLOC_TABLE,
                                     self.chains, "allocated",
                                     self.NUM_CHAINS)

        self._copy_values_into_list(raw_data, self.SOFT_SYNTH_PARAMS,
                                    self.WAVES_PER_SYNTH,
                                    self.synths, "params")

        self.clock.hours = raw_data[self.CLOCK_HOURS]
        self.clock.minutes = raw_data[self.CLOCK_MINUTES]
        self.tempo = raw_data[self.TEMPO]
        self.tune_setting = raw_data[self.TUNE_SETTING]
        self.total_clock.days = raw_data[self.TOTAL_CLOCK_DAYS]
        self.total_clock.hours = raw_data[self.TOTAL_CLOCK_HOURS]
        self.total_clock.minutes = raw_data[self.TOTAL_CLOCK_MINUTES]

        # total_clock_checksum = raw_data[self.TOTAL_CLOCK_CHECKSUM]
        # expected_checksum = self.total_clock.days + \
        #     self.total_clock.hours + self.total_clock.minutes

        # if total_clock_checksum != expected_checksum:
        #     sys.exit(".sav file appears to be corrupted; total clock checksum "
        #              "mismatch (s/b %d, is %d)" % (total_clock_checksum,
        #                                            expected_checksum))

        self.key_delay = raw_data[self.KEY_DELAY]
        self.key_repeat = raw_data[self.KEY_REPEAT]
        self.font = raw_data[self.FONT]
        self.sync_setting = raw_data[self.SYNC_SETTING]
        self.colorset = raw_data[self.COLORSET]
        self.clone = raw_data[self.CLONE]
        self.file_changed = raw_data[self.FILE_CHANGED]
        self.power_save = raw_data[self.POWER_SAVE]
        self.prelisten = raw_data[self.PRELISTEN]
        self.wave_synth_overwrite_locks = raw_data[
            self.WAVE_SYNTH_OVERWRITE_LOCKS[0] :
            self.WAVE_SYNTH_OVERWRITE_LOCKS[1] + 1]
        self.version_byte = raw_data[self.VERSION_BYTE]

        self._copy_values_into_list(raw_data, self.PHRASE_FX,
                                    self.STEPS_PER_PHRASE, self.phrases, "fx")

        self._copy_values_into_list(raw_data, self.PHRASE_FX_VALS,
                                    self.STEPS_PER_PHRASE, self.phrases,
                                    "fx_vals")

        wave_id = 0
        for i in xrange(self.WAVE_FRAMES[0], self.WAVE_FRAMES[1] + 1,
                        Wave.NUM_FRAMES):
            synth_id = wave_id / self.WAVES_PER_SYNTH
            synth_wave_id = wave_id % self.WAVES_PER_SYNTH

            self.synths[synth_id].waves[synth_wave_id].frames = \
                raw_data[i:i + Wave.NUM_FRAMES]

            wave_id += 1

        self._copy_values_into_list(raw_data, self.PHRASE_INSTR,
                                    self.STEPS_PER_PHRASE, self.phrases,
                                    "instruments")

        utils.check_mem_init_flag(raw_data,
                                  self.MEM_INIT_FLAG_3[0],
                                  self.MEM_INIT_FLAG_3[1])

    def _copy_values_into_list(self, raw_data, index_range, index_delta,
                               obj_list, field_name):
        current_obj_id = 0

        for i in xrange(index_range[0], index_range[1] + 1, index_delta):
            obj_list[current_obj_id].__dict__[field_name] \
                = raw_data[i:i + index_delta]
            current_obj_id += 1

    def _copy_from_decompressed_table(self, raw_data, index_range, obj_list,
                                      obj_field):
        object_id = 0
        for i in xrange(index_range[0], index_range[1] + 1):
            self.obj_list[object_id].__dict__[obj_field] = raw_data[i]
            object_id += 1

    def _decompress_alloc_table(self, raw_data, index_range, objects,
                                object_field, num_objects):
        object_id = 0
        for i in xrange(index_range[0], index_range[1] + 1):
            current_bits = utils.get_bits(raw_data[i])

            for j in xrange(len(current_bits)):
                objects[object_id].__dict__[object_field] = current_bits[j]
                object_id += 1

                if object_id == num_objects:
                    break


    def get_raw_data(self):
        raw_data = []

        self._append_field_from_objects(raw_data, self.phrases, "notes")
        raw_data.extend(self.bookmarks)
        self._append_empty_section(raw_data, self.EMPTY_SECTION_1)
        self._append_field_from_objects(raw_data, self.grooves, "ticks")
        raw_data.extend(self.song.chain_numbers)
        self._append_field_from_objects(raw_data, self.tables, "envelopes")

        for word in self.speech_instrument.words:
            raw_data.extend(word)

        for word_name in self.speech_instrument.word_names:
            raw_data.extend(word_name)

        # Memory check bit
        raw_data.extend(['r', 'b'])

        # Make sure we're at the right offset
        assert len(raw_data) == MEM_INIT_FLAG_1[1] + 1, "At this point in "\
            "raw data generation, we are at an incorrect offset in the file"

        self._append_field_from_objects(raw_data, self.instruments, "name")

        for table in self.tables:
            raw_data.append(int(instr.allocated))

        for instr in self.instruments:
            raw_data.append(int(instr.allocated))

        self._append_field_from_objects(raw_data, self.chains, "phrases")
        self._append_field_from_objects(raw_data, self.chains, "transposes")
        self._append_field_from_objects(raw_data, self.instruments, "params")
        self._append_field_from_objects(raw_data, self.tables, "transposes")
        self._append_field_from_objects(raw_data, self.tables, "fx")
        self._append_field_from_objects(raw_data, self.tables, "fx_vals")
        self._append_field_from_objects(raw_data, self.tables, "fx2")
        self._append_field_from_objects(raw_data, self.tables, "fx2_vals")

        # Add second memory check bytes
        raw_data.extend(['r', 'b'])

        # Make sure our offset's still right
        assert len(raw_data) == MEM_INIT_FLAG_2[1] + 1, "At this point in "\
            "raw data generation, we are at an incorrect offset in the file"

        self._append_condensed_allocation_table(
            raw_data, self.phrases, "allocated")

        self._append_condensed_allocation_table(
            raw_data, self.chains, "allocated")

        self._append_field_from_objects(raw_data, self.synths, "params")

        raw_data.append(self.clock.hours)
        raw_data.append(self.clock.minutes)
        raw_data.append(self.tempo)
        raw_data.append(self.tune_setting)
        raw_data.append(self.total_clock.days)
        raw_data.append(self.total_clock.hours)
        raw_data.append(self.total_clock.minutes)
        raw_data.append(self.key_delay)
        raw_data.append(self.key_repeat)
        raw_data.append(self.font)
        raw_data.append(self.sync_setting)
        raw_data.append(self.colorset)

        self._append_empty_section(raw_data, EMPTY_SECTION_3)

        raw_data.append(self.clone)
        raw_data.append(self.file_changed)
        raw_data.append(self.power_save)
        raw_data.append(self.prelisten)
        raw_data.extend(self.wave_synth_overwrite_locks)

        self._append_field_from_objects(raw_data, self.phrases, "fx")
        self._append_field_from_objects(raw_data, self.phrases, "fx_vals")

        for synth in self.synths:
            for wave in synth.waves:
                raw_data.extend(wave.frames)

        self._append_field_from_objects(raw_data, self.phrases, "instruments")

        raw_data.extend(['r', 'b'])

        # Make sure we're at the right offset
        assert len(raw_data) == MEM_INIT_FLAG_3[1] + 1, "At this point in "\
            "raw data generation, we are at an incorrect offset in the file"

        self._append_empty_section(raw_data, EMPTY_SECTION_4)

        raw_data.append(self.version_byte)

        # Make sure the data is the right size
        assert len(raw_data) == 0x8000, "Raw data was not assigned"

        return raw_data

    def _append_field_from_objects(self, raw_data, obj_list, field_name):
        for obj in obj_list:
            raw_data.extend(obj.__dict__[field_name])

    def _append_empty_section(self, raw_data, section_boundaries):
        for i in xrange(section_boundaries[1] - section_boundaries[0] + 1):
            raw_data.append(0)

    def _append_condensed_allocation_table(self, raw_data, objects,
                                           field_name):
        obj_bits = []

        for obj in objects:
            obj_bits.append(obj.__dict__(field_name))

            if len(obj_bits) == 8:
                raw_data.append(utils.get_byte(obj_bits))
                obj_bits = []
