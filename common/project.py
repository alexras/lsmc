import sys
from chain import Chain
from synth import Synth
import wave
from clock import Clock
from groove import Groove
import instrument
from phrase import Phrase
import song
from table import Table
import utils
import consts
import filepack
from pulse_instrument import PulseInstrument
from wave_instrument import WaveInstrument
from kit_instrument import KitInstrument
from noise_instrument import NoiseInstrument
import speech_instrument
from rich_comparable_mixin import RichComparableMixin

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

# Steps per table
STEPS_PER_TABLE = 16

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
EMPTY_SECTION_2 = (0x1fba, 0x201f)

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

# Empty section #4
EMPTY_SECTION_4 = (0x3fc6, 0x3fff)

# Phrase FX
PHRASE_FX = (0x4000, 0x4fef)

# Phrase FX values
PHRASE_FX_VALS = (0x4ff0, 0x5fdf)

# Empty section #5
EMPTY_SECTION_5 = (0x5fe0, 0x5fff)

# Wave frames
WAVE_FRAMES = (0x6000, 0x6fff)

# Phrase instruments
PHRASE_INSTR = (0x7000, 0x7fef)

# "Memory initialized" flag (should be 'rb')
MEM_INIT_FLAG_3 = (0x7ff0, 0x7ff1)

# Empty section #6
EMPTY_SECTION_6 = (0x7ff2, 0x7ffe)

# Version byte (0 = < 3.6.0, 1 = 3.6.0, 2 = >= 3.6.1)
VERSION_BYTE = 0x7fff


class Project(RichComparableMixin):
    def __init__(self, name, version):
        self.name = utils.strip_nulls(name)
        self.version = version
        self.tables = []
        self.instruments = []
        self.phrases = []
        self.chains = []
        self.grooves = []
        self.synths = []
        self.bookmarks = []

        self.song = song.Song()

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

        for i in xrange(NUM_TABLES):
            self.tables.append(Table())

        for i in xrange(NUM_INSTRUMENTS):
            self.instruments.append(instrument.Instrument())

        for i in xrange(NUM_PHRASES):
            self.phrases.append(Phrase())

        for i in xrange(NUM_CHAINS):
            self.chains.append(Chain())

        for i in xrange(NUM_GROOVES):
            self.grooves.append(Groove())

        for i in xrange(NUM_SYNTHS):
            synth = Synth()

            for j in xrange(WAVES_PER_SYNTH):
                synth.waves.append(wave.Wave())

            self.synths.append(synth)

    def load_data(self, raw_data):
        self._copy_values_into_list(raw_data, PHRASE_NOTES,
                                    STEPS_PER_PHRASE,
                                    self.phrases, "notes")

        self.bookmarks = raw_data[BOOKMARKS[0] : BOOKMARKS[1] + 1]

        self._copy_values_into_list(raw_data, GROOVES,
                                    STEPS_PER_GROOVE,
                                    self.grooves, "ticks")

        self.song.chain_numbers = raw_data[CHAINNOS[0] :
                                           CHAINNOS[1] + 1]

        self._copy_values_into_list(raw_data, TABLE_ENVELOPES,
                                    STEPS_PER_TABLE, self.tables,
                                    "envelopes")

        self.speech_instrument = speech_instrument.SpeechInstrument()

        self.speech_instrument.allocated = True

        for i in xrange(SPEECH_INSTR_WORDS[0],
                        SPEECH_INSTR_WORDS[1] + 1,
                        speech_instrument.WORD_LENGTH):
            self.speech_instrument.raw_words.append(
                raw_data[i:i + speech_instrument.WORD_LENGTH])

        for i in xrange(WORD_NAMES[0], WORD_NAMES[1] + 1,
                        speech_instrument.WORD_NAME_LENGTH):
            self.speech_instrument.raw_word_names.append(
                raw_data[i:i + speech_instrument.WORD_NAME_LENGTH])

        utils.check_mem_init_flag(raw_data, MEM_INIT_FLAG_1[0],
                                  MEM_INIT_FLAG_1[1])

        self._copy_values_into_list(raw_data, INSTR_NAMES,
                                    instrument.NAME_LENGTH,
                                    self.instruments, "name")

        self._copy_from_decompressed_table(
            raw_data, TABLE_ALLOC_TABLE, self.tables, "allocated")

        self._copy_from_decompressed_table(
            raw_data, INSTR_ALLOC_TABLE, self.instruments, "allocated")

        self._copy_values_into_list(raw_data, CHAIN_PHRASES,
                                    PHRASES_PER_CHAIN, self.chains,
                                    "phrases")

        self._copy_values_into_list(raw_data, CHAIN_TRANSPOSES,
                                    PHRASES_PER_CHAIN, self.chains,
                                    "transposes")

        self._copy_values_into_list(raw_data, INSTR_PARAMS,
                                    instrument.NUM_PARAMS,
                                    self.instruments, "params")

        self._copy_values_into_list(raw_data, TABLE_TRANSPOSES,
                                    ENTRIES_PER_TABLE, self.tables,
                                    "transposes")

        self._copy_values_into_list(raw_data, TABLE_FX,
                                    ENTRIES_PER_TABLE, self.tables, "fx")

        self._copy_values_into_list(raw_data, TABLE_FX_VALS,
                                    ENTRIES_PER_TABLE, self.tables,
                                    "fx_vals")

        self._copy_values_into_list(raw_data, TABLE_FX_2,
                                    ENTRIES_PER_TABLE, self.tables, "fx2")

        self._copy_values_into_list(raw_data, TABLE_FX_2_VALS,
                                    ENTRIES_PER_TABLE, self.tables,
                                    "fx2_vals")

        utils.check_mem_init_flag(raw_data, MEM_INIT_FLAG_2[0],
                                  MEM_INIT_FLAG_2[1])

        self._decompress_alloc_table(raw_data, PHRASE_ALLOC_TABLE,
                                     self.phrases, "allocated",
                                     NUM_PHRASES)

        self._decompress_alloc_table(raw_data, CHAIN_ALLOC_TABLE,
                                     self.chains, "allocated",
                                     NUM_CHAINS)

        self._copy_values_into_list(raw_data, SOFT_SYNTH_PARAMS,
                                    WAVES_PER_SYNTH,
                                    self.synths, "params")

        self.clock.hours = raw_data[CLOCK_HOURS]
        self.clock.minutes = raw_data[CLOCK_MINUTES]
        self.tempo = raw_data[TEMPO]
        self.tune_setting = raw_data[TUNE_SETTING]
        self.total_clock.days = raw_data[TOTAL_CLOCK_DAYS]
        self.total_clock.hours = raw_data[TOTAL_CLOCK_HOURS]
        self.total_clock.minutes = raw_data[TOTAL_CLOCK_MINUTES]

        total_clock_checksum = raw_data[TOTAL_CLOCK_CHECKSUM]

        if total_clock_checksum != self.total_clock.checksum:
            assert False, (".sav file appears to be corrupted; total "
                           "clock checksum mismatch (s/b %d, is %d)" %
                           (self.total_clock.checksum,
                            total_clock_checksum))

        self.key_delay = raw_data[KEY_DELAY]
        self.key_repeat = raw_data[KEY_REPEAT]
        self.font = raw_data[FONT]
        self.sync_setting = raw_data[SYNC_SETTING]
        self.colorset = raw_data[COLORSET]
        self.clone = raw_data[CLONE]
        self.file_changed = raw_data[FILE_CHANGED]
        self.power_save = raw_data[POWER_SAVE]
        self.prelisten = raw_data[PRELISTEN]
        self.wave_synth_overwrite_locks = raw_data[
            WAVE_SYNTH_OVERWRITE_LOCKS[0] :
            WAVE_SYNTH_OVERWRITE_LOCKS[1] + 1]
        self.version_byte = raw_data[VERSION_BYTE]

        self._copy_values_into_list(raw_data, PHRASE_FX,
                                    STEPS_PER_PHRASE, self.phrases, "fx")

        self._copy_values_into_list(raw_data, PHRASE_FX_VALS,
                                    STEPS_PER_PHRASE, self.phrases,
                                    "fx_vals")

        wave_id = 0
        for i in xrange(WAVE_FRAMES[0], WAVE_FRAMES[1] + 1,
                        wave.NUM_FRAMES):
            synth_id = wave_id / WAVES_PER_SYNTH
            synth_wave_id = wave_id % WAVES_PER_SYNTH

            self.synths[synth_id].waves[synth_wave_id].frames = \
                raw_data[i:i + wave.NUM_FRAMES]

            wave_id += 1

        self._copy_values_into_list(raw_data, PHRASE_INSTR,
                                    STEPS_PER_PHRASE, self.phrases,
                                    "instruments")

        utils.check_mem_init_flag(raw_data,
                                  MEM_INIT_FLAG_3[0],
                                  MEM_INIT_FLAG_3[1])

    def postprocess(self):
        instrument_subtypes = {
            instrument.PULSE_TYPE : PulseInstrument,
            instrument.WAVE_TYPE : WaveInstrument,
            instrument.KIT_TYPE : KitInstrument,
            instrument.NOISE_TYPE : NoiseInstrument
            }

        # Turn instruments into their appropriate types and copy in tables and
        # waves
        for i, instr in enumerate(self.instruments):
            if not instr.allocated:
                continue
            subtype_instance = instrument_subtypes[instr.instrument_type]()
            subtype_instance.copy(instr)

            if hasattr(subtype_instance, "has_table") and \
                    subtype_instance.has_table:
                subtype_instance.table = \
                    self.tables[subtype_instance.table_number]

            self.instruments[i] = subtype_instance

    def _copy_values_into_list(self, raw_data, index_range, index_delta,
                               obj_list, field_name):
        current_obj_id = 0

        for i in xrange(index_range[0], index_range[1] + 1, index_delta):
            setattr(obj_list[current_obj_id], field_name,
                    raw_data[i:i + index_delta])
            current_obj_id += 1

    def _copy_from_decompressed_table(self, raw_data, index_range, obj_list,
                                      obj_field):
        object_id = 0
        for i in xrange(index_range[0], index_range[1] + 1):
            setattr(obj_list[object_id], obj_field, raw_data[i])
            object_id += 1

    def _decompress_alloc_table(self, raw_data, index_range, objects,
                                object_field, num_objects):
        object_id = 0
        for i in xrange(index_range[0], index_range[1] + 1):
            current_bits = utils.get_bits(raw_data[i])

            for j in xrange(len(current_bits)):
                setattr(objects[object_id], object_field, current_bits[j])
                object_id += 1

                if object_id == num_objects:
                    break


    def get_raw_data(self):
        raw_data = []

        self._append_field_from_objects(raw_data, self.phrases, "notes")
        raw_data.extend(self.bookmarks)
        self._append_empty_section(raw_data, EMPTY_SECTION_1)

        self._check_offset(len(raw_data), GROOVES[0])

        self._append_field_from_objects(raw_data, self.grooves, "ticks")
        self._check_offset(len(raw_data), CHAINNOS[0])

        raw_data.extend(self.song.chain_numbers)

        self._check_offset(len(raw_data), TABLE_ENVELOPES[0])

        self._append_field_from_objects(raw_data, self.tables, "envelopes")

        self._check_offset(len(raw_data), SPEECH_INSTR_WORDS[0])

        for word in self.speech_instrument.raw_words:
            raw_data.extend(word)

        for word_name in self.speech_instrument.raw_word_names:
            raw_data.extend(word_name)

        # Memory check bit
        self._append_mem_check_bytes(raw_data)

        # Make sure we're at the right offset
        self._check_offset(len(raw_data), MEM_INIT_FLAG_1[1] + 1)

        for instr in self.instruments:
            raw_data.extend(utils.string_to_bytes(
                    instr.name, instrument.NAME_LENGTH))

        self._check_offset(len(raw_data), EMPTY_SECTION_2[0])

        self._append_empty_section(raw_data, EMPTY_SECTION_2)

        self._check_offset(len(raw_data), TABLE_ALLOC_TABLE[0])

        for table in self.tables:
            raw_data.append(int(table.allocated))

        for instr in self.instruments:
            raw_data.append(int(instr.allocated))

        self._check_offset(len(raw_data), CHAIN_PHRASES[0])

        self._append_field_from_objects(raw_data, self.chains, "phrases")
        self._append_field_from_objects(raw_data, self.chains, "transposes")
        self._append_field_from_objects(raw_data, self.instruments, "params")
        self._append_field_from_objects(raw_data, self.tables, "transposes")
        self._append_field_from_objects(raw_data, self.tables, "fx")
        self._append_field_from_objects(raw_data, self.tables, "fx_vals")
        self._append_field_from_objects(raw_data, self.tables, "fx2")
        self._append_field_from_objects(raw_data, self.tables, "fx2_vals")

        # Add second memory check bytes
        self._append_mem_check_bytes(raw_data)

        # Make sure our offset's still right
        self._check_offset(len(raw_data), MEM_INIT_FLAG_2[1] + 1)

        self._append_condensed_allocation_table(
            raw_data, self.phrases, "allocated")

        self._check_offset(len(raw_data), CHAIN_ALLOC_TABLE[0])

        self._append_condensed_allocation_table(
            raw_data, self.chains, "allocated")

        self._check_offset(len(raw_data), SOFT_SYNTH_PARAMS[0])

        self._append_field_from_objects(raw_data, self.synths, "params")

        self._check_offset(len(raw_data), CLOCK_HOURS)

        raw_data.append(self.clock.hours)
        raw_data.append(self.clock.minutes)
        raw_data.append(self.tempo)
        raw_data.append(self.tune_setting)

        self._check_offset(len(raw_data), TOTAL_CLOCK_DAYS)

        raw_data.append(self.total_clock.days)
        raw_data.append(self.total_clock.hours)
        raw_data.append(self.total_clock.minutes)
        raw_data.append(self.total_clock.checksum)
        raw_data.append(self.key_delay)
        raw_data.append(self.key_repeat)
        raw_data.append(self.font)
        raw_data.append(self.sync_setting)
        raw_data.append(self.colorset)

        self._check_offset(len(raw_data), EMPTY_SECTION_3[0])

        self._append_empty_section(raw_data, EMPTY_SECTION_3)

        self._check_offset(len(raw_data), CLONE)

        raw_data.append(self.clone)
        raw_data.append(self.file_changed)
        raw_data.append(self.power_save)
        raw_data.append(self.prelisten)
        raw_data.extend(self.wave_synth_overwrite_locks)

        self._append_empty_section(raw_data, EMPTY_SECTION_4)

        self._check_offset(len(raw_data), PHRASE_FX[0])

        self._append_field_from_objects(raw_data, self.phrases, "fx")

        self._append_field_from_objects(raw_data, self.phrases, "fx_vals")

        self._append_empty_section(raw_data, EMPTY_SECTION_5)

        self._check_offset(len(raw_data), WAVE_FRAMES[0])

        for synth in self.synths:
            for wave in synth.waves:
                raw_data.extend(wave.frames)

        self._append_field_from_objects(raw_data, self.phrases, "instruments")

        self._append_mem_check_bytes(raw_data)

        # Make sure we're at the right offset
        self._check_offset(len(raw_data), MEM_INIT_FLAG_3[1] + 1)

        self._append_empty_section(raw_data, EMPTY_SECTION_6)

        raw_data.append(self.version_byte)

        # Make sure the data is the right size
        assert len(raw_data) == consts.RAW_DATA_SIZE, "Raw data generated by " \
            "get_raw_data() is not the right size (expected 0x%x, got 0x%x)" \
            % (consts.RAW_DATA_SIZE, len(raw_data))

        return raw_data

    def _append_field_from_objects(self, raw_data, obj_list, field_name):
        for obj in obj_list:
            raw_data.extend(getattr(obj, field_name))

    def _append_empty_section(self, raw_data, section_boundaries):
        for i in xrange(section_boundaries[1] - section_boundaries[0] + 1):
            raw_data.append(0)

    def _append_condensed_allocation_table(self, raw_data, objects,
                                           field_name):
        obj_bits = []

        for obj in objects:
            obj_bits.append(getattr(obj, field_name))

            if len(obj_bits) == 8:
                raw_data.append(utils.get_byte(obj_bits))
                obj_bits = []

        if len(obj_bits) != 0:
            for i in xrange(8 - len(obj_bits)):
                obj_bits.append(0)

            raw_data.append(utils.get_byte(obj_bits))

    def _append_mem_check_bytes(self, raw_data):
        raw_data.extend([ord('r'), ord('b')])

    def _check_offset(self, data_size, expected_data_size):
        assert data_size == expected_data_size, "At this point in raw data "\
            "generation, we are at an incorrect offset in the file; expected "\
            "to be at %x, but we are at %x" % (expected_data_size, data_size)
