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

class Project(object):
    # Byte used to denote run-length encoding
    RLE_BYTE = 0xc0

    # Byte used to denote special action
    SPECIAL_BYTE = 0xe0

    # Byte used to denote end of file (appears after special byte)
    EOF_BYTE = 0xff

    # Byte used to denote default instrument
    DEFAULT_INSTR_BYTE = 0xf1

    # Byte used to denote default wave
    DEFAULT_WAVE_BYTE = 0xf0

    # Binary data for default instrument
    DEFAULT_INSTR = [0xa8, 0, 0, 0xff, 0, 0, 3, 0, 0, 0xd0, 0, 0, 0, 0xf3, 0, 0]

    # Binary data for default wave
    DEFAULT_WAVE = [0x8e, 0xcd, 0xcc, 0xbb, 0xaa, 0xa9, 0x99, 0x88, 0x87, 0x76,
                    0x66, 0x55, 0x54, 0x43, 0x32, 0x31]

    # State machine states for __init__
    STATE_BYTES = 0
    STATE_RLE_BYTE = 1
    STATE_RLE_COUNT = 2
    STATE_SPECIAL_BYTE = 3
    STATE_DEFAULT_INSTR = 4
    STATE_DEFAULT_WAVE = 5
    STATE_DONE = 6

    # Max. number of phrases
    NUM_PHRASES = 255

    # Max. number of tables
    NUM_TABLES = 32

    # Number of soft-synths
    NUM_SYNTHS = 16

    # Waves per soft-synth
    WAVES_PER_SYNTH = 16

    # Frames per wave
    FRAMES_PER_WAVE = 16

    # Number of entries in each table
    ENTRIES_PER_TABLE = 16

    # Max. number of instruments
    NUM_INSTRUMENTS = 64

    # Max. number of parameters per instrument
    PARAMS_PER_INSTRUMENT = 16

    # Max. number of chains
    NUM_CHAINS = 128

    # Max. number of phrases per chain
    PHRASES_PER_CHAIN = 16

    # Max. number of grooves
    NUM_GROOVES = 32

    # Notes for phrases
    PHRASE_NOTES = (0, 0xfef)

    # Steps per phrase
    STEPS_PER_PHRASE = 16

    # Grooves
    GROOVES = (0x1090, 0x128f)

    # Steps per groove
    STEPS_PER_GROOVE = 16

    # Chain numbers for song
    CHAINNOS = (0x1290, 0x168f)

    # Number of channels
    NUM_CHANNELS = 4

    # Envelopes for tables
    TABLE_ENVELOPES = (0x1690, 0x188f)

    # Steps per table
    STEPS_PER_TABLE = 16

    # Speech instrument "words"
    SPEECH_INSTR_WORDS = (0x1890, 0x1dcf)

    # Max. length of a "word"
    WORD_LENGTH = 0x20

    # Number of "words" in the speech instrument
    NUM_WORDS = 42

    # Word names
    WORD_NAMES = (0x1dd0, 0x1e77)

    # Max. length of a word name
    WORD_NAME_LENGTH = 4

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

    # Table FX 2 Values
    TABLE_FX_2_VALS = (0x3c80, 0x3e7f)

    # "Memory initialized" flag (should be 'rb')
    MEM_INIT_FLAG = (0x3e80, 0x3e81)

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

    # Subsong mask (one of 0x0f, 0x1f, 0x3f, 0x7f, 0xff)
    SUBSONG_MASK = 0x3fbf

    # Clone (0 = deep, 1 = slim)
    CLONE = 0x3fc0

    # Phrase FX
    PHRASE_FX = (0x4000, 0x4fef)

    # Phrase FX values
    PHRASE_FX_VALS = (0x4ff0, 0x5fdf)

    # Wave frames
    WAVE_FRAMES = (0x6000, 0x6fff)

    # Phrase instruments
    PHRASE_INSTR = (0x7000, 0x7fef)

    # "Memory initialized" flag (should be 'rb')
    MEM_INITIALIZED_FLAG = (0x7ff0, 0x7ff1)

    def __init__(self, name, version, blocks):
        self.name = name
        self.version = version

        raw_data = self.parse_blocks(blocks)

        self.tables = []
        self.instruments = []
        self.phrases = []
        self.chains = []
        self.grooves = []
        self.synths = []

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
        self.subsong_mask = None
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


        phrase_id = 0
        for i in xrange(self.PHRASE_NOTES[0], self.PHRASE_NOTES[1] + 1,
                        self.STEPS_PER_PHRASE):
            self.phrases[phrase_id].notes = \
                raw_data[i:i + self.STEPS_PER_PHRASE]
            phrase_id += 1

        groove_id = 0
        for i in xrange(self.GROOVES[0], self.GROOVES[1] + 1,
                        self.STEPS_PER_GROOVE):
            self.grooves[groove_id].ticks = \
                raw_data[i:i + self.STEPS_PER_GROOVE]
            groove_id += 1


        for i in xrange(self.CHAINNOS[0], self.CHAINNOS[1] + 1,
                        self.NUM_CHANNELS):
            self.song.chain_numbers.append(raw_data[i:i + self.NUM_CHANNELS])

        table_id = 0
        for i in xrange(self.TABLE_ENVELOPES[0], self.TABLE_ENVELOPES[1] + 1,
                        self.STEPS_PER_TABLE):
            self.tables[table_id].envelopes = \
                raw_data[i:i + self.STEPS_PER_TABLE]
            table_id += 1

        speech_instrument = SpeechInstrument()

        # Speech instrument is always allocated
        speech_instrument.allocated = True

        for i in xrange(self.SPEECH_INSTR_WORDS[0],
                        self.SPEECH_INSTR_WORDS[1] + 1, self.WORD_LENGTH):
            speech_instrument.words.append(raw_data[i:i + self.WORD_LENGTH])

        for i in xrange(self.WORD_NAMES[0], self.WORD_NAMES[1] + 1,
                        self.WORD_NAME_LENGTH):
            speech_instrument.word_names.append(
                raw_data[i:i + self.WORD_NAME_LENGTH])

        self.instruments.append(speech_instrument)

        table_id = 0
        for i in xrange(self.TABLE_ALLOC_TABLE[0],
                        self.TABLE_ALLOC_TABLE[1] + 1):
            self.tables[table_id].allocated = bool(raw_data[i])
            table_id += 1

        instr_id = 0
        for i in xrange(self.INSTR_ALLOC_TABLE[0],
                        self.INSTR_ALLOC_TABLE[1] + 1):
            self.instruments[instr_id].allocated = bool(raw_data[i])
            instr_id += 1

        chain_id = 0
        for i in xrange(self.CHAIN_PHRASES[0], self.CHAIN_PHRASES[1] + 1,
                        self.PHRASES_PER_CHAIN):
            self.chains[chain_id].phrases = \
                raw_data[i:i + self.PHRASES_PER_CHAIN]
            chain_id += 1

        chain_id = 0
        for i in xrange(self.CHAIN_TRANSPOSES[0], self.CHAIN_TRANSPOSES[1] + 1,
                        self.PHRASES_PER_CHAIN):
            self.chains[chain_id].transposes = \
                raw_data[i:i+ self.PHRASES_PER_CHAIN]
            chain_id += 1

        instr_id = 0
        for i in xrange(self.INSTR_PARAMS[0], self.INSTR_PARAMS[1] + 1,
                        self.PARAMS_PER_INSTRUMENT):
            self.instruments[instr_id].params = \
                raw_data[i:i + self.PARAMS_PER_INSTRUMENT]
            instr_id += 1

        table_id = 0
        for i in xrange(self.TABLE_TRANSPOSES[0], self.TABLE_TRANSPOSES[1] + 1,
                        self.ENTRIES_PER_TABLE):
            self.tables[table_id].transposes = \
                raw_data[i:i + self.ENTRIES_PER_TABLE]
            table_id += 1

        table_id = 0
        for i in xrange(self.TABLE_FX[0], self.TABLE_FX[1] + 1,
                        self.ENTRIES_PER_TABLE):
            self.tables[table_id].transposes = \
                raw_data[i:i + self.ENTRIES_PER_TABLE]
            table_id += 1

        table_id = 0
        for i in xrange(self.TABLE_FX_VALS[0], self.TABLE_FX_VALS[1] + 1,
                        self.ENTRIES_PER_TABLE):
            self.tables[table_id].transposes = \
                raw_data[i:i + self.ENTRIES_PER_TABLE]
            table_id += 1

        table_id = 0
        for i in xrange(self.TABLE_FX_2[0], self.TABLE_FX_2[1] + 1,
                        self.ENTRIES_PER_TABLE):
            self.tables[table_id].transposes = \
                raw_data[i:i + self.ENTRIES_PER_TABLE]
            table_id += 1

        table_id = 0
        for i in xrange(self.TABLE_FX_2_VALS[0], self.TABLE_FX_2_VALS[1] + 1,
                        self.ENTRIES_PER_TABLE):
            self.tables[table_id].transposes = \
                raw_data[i:i + self.ENTRIES_PER_TABLE]
            table_id += 1

        utils.check_mem_init_flag(raw_data, self.MEM_INIT_FLAG[0],
                                  self.MEM_INIT_FLAG[1])

        phrase_id = 0
        for i in xrange(self.PHRASE_ALLOC_TABLE[0],
                        self.PHRASE_ALLOC_TABLE[1] + 1):
            current_bits = utils.get_bits(raw_data[i])

            for j in xrange(len(current_bits)):
                self.phrases[phrase_id].allocated = bool(current_bits[j])
                phrase_id += 1

                if phrase_id == self.NUM_PHRASES:
                    break

        chain_id = 0
        for i in xrange(self.CHAIN_ALLOC_TABLE[0],
                        self.CHAIN_ALLOC_TABLE[1] + 1):
            current_bits = utils.get_bits(raw_data[i])

            for j in xrange(len(current_bits)):
                self.chains[chain_id].allocated = bool(current_bits[j])
                chain_id += 1

        synth_id = 0
        for i in xrange(self.SOFT_SYNTH_PARAMS[0],
                        self.SOFT_SYNTH_PARAMS[1] + 1,
                        self.WAVES_PER_SYNTH):
            self.synths[synth_id].params = raw_data[i:i + self.WAVES_PER_SYNTH]
            synth_id += 1

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
        self.subsong_mask = raw_data[self.SUBSONG_MASK]
        self.clone = raw_data[self.CLONE]

        phrase_id = 0
        for i in xrange(self.PHRASE_FX[0], self.PHRASE_FX[1] + 1,
                        self.STEPS_PER_PHRASE):
            self.phrases[phrase_id].fx = raw_data[i:i + self.STEPS_PER_PHRASE]
            phrase_id += 1

        phrase_id = 0
        for i in xrange(self.PHRASE_FX_VALS[0], self.PHRASE_FX_VALS[1] + 1,
                        self.STEPS_PER_PHRASE):
            self.phrases[phrase_id].fx_vals = \
                raw_data[i:i + self.STEPS_PER_PHRASE]
            phrase_id += 1

        wave_id = 0
        for i in xrange(self.WAVE_FRAMES[0], self.WAVE_FRAMES[1] + 1,
                        self.FRAMES_PER_WAVE):
            synth_id = wave_id / self.WAVES_PER_SYNTH
            synth_wave_id = wave_id % self.WAVES_PER_SYNTH

            self.synths[synth_id].waves[synth_wave_id].frames = \
                raw_data[i:i + self.FRAMES_PER_WAVE]

            wave_id += 1

        phrase_id = 0
        for i in xrange(self.PHRASE_INSTR[0], self.PHRASE_INSTR[1] + 1,
                        self.STEPS_PER_PHRASE):
            self.phrases[phrase_id].instruments = \
                raw_data[i:i + self.STEPS_PER_PHRASE]
            phrase_id += 1

        utils.check_mem_init_flag(raw_data,
                                  self.MEM_INITIALIZED_FLAG[0],
                                  self.MEM_INITIALIZED_FLAG[1])

    def parse_blocks(self, blocks):
        raw_data = []

        state = self.STATE_BYTES

        current_block_index = sorted(blocks.keys())[0]
        current_block = blocks[current_block_index]
        current_block_offset = 0

        rle_byte_value = None

        while state != self.STATE_DONE:
            data_byte = current_block[current_block_offset]
            current_block_offset += 1

            if state == self.STATE_BYTES:
                if data_byte == self.RLE_BYTE:
                    state = self.STATE_RLE_BYTE
                elif data_byte == self.SPECIAL_BYTE:
                    state = self.STATE_SPECIAL_BYTE
                else:
                    raw_data.append(data_byte)

            elif state == self.STATE_RLE_BYTE:
                if data_byte == self.RLE_BYTE:
                    raw_data.append(data_byte)
                    state = self.STATE_BYTES
                else:
                    rle_byte_value = data_byte
                    state = self.STATE_RLE_COUNT

            elif state == self.STATE_RLE_COUNT:
                for i in xrange(data_byte):
                    raw_data.append(rle_byte_value)
                state = self.STATE_BYTES

            elif state == self.STATE_SPECIAL_BYTE:
                if data_byte == self.SPECIAL_BYTE:
                    raw_data.append(data_byte)
                    state = self.STATE_BYTES
                elif data_byte == self.DEFAULT_INSTR_BYTE:
                    state = self.STATE_DEFAULT_INSTR
                elif data_byte == self.DEFAULT_WAVE_BYTE:
                    state = self.STATE_DEFAULT_WAVE
                elif data_byte == self.EOF_BYTE:
                    # End of file reached; can stop parsing
                    state = self.STATE_DONE
                else:
                    current_block_index = data_byte
                    current_block = blocks[current_block_index]
                    current_block_offset = 0
                    state = self.STATE_BYTES

            elif state == self.STATE_DEFAULT_INSTR:
                for i in xrange(data_byte):
                    raw_data.extend(self.DEFAULT_INSTR)

                state = self.STATE_BYTES
            elif state == self.STATE_DEFAULT_WAVE:
                for i in xrange(data_byte):
                    raw_data.extend(self.DEFAULT_WAVE)

                state = self.STATE_BYTES
            else:
                sys.exit("Encountered invalid state %d" % (state))

        return raw_data
