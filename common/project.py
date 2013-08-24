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
import bread
import bread_spec as spec

class Project(RichComparableMixin):
    def __init__(self, name, version):
        self.name = utils.strip_nulls(name)
        self.version = version
        self.tables = None
        self.instruments = []
        self.phrases = None
        self.chains = None
        self.grooves = []
        self.synths = []
        self.bookmarks = []

        self.song = song.Song()

        self.clock = None
        self.total_clock = None
        self.tempo = None
        self.tune_setting = None
        self.key_delay = None
        self.key_repeat = None
        self.font = None
        self.sync_setting = None
        self.colorset = None
        self.clone = None

    def _reconstruct_from_alloc_table(
            self, alloc_bit_vector, features_per_item, output_class, features):
        """Each item in the set of items being constructed has a number of
        feature lists, each features_per_item long. alloc_bit_vector
        determines which groups of features correspond to valid items, and
        which are unallocated noise."""

        allocated_items = [i for i in alloc_bit_vector if alloc_bit_vector[i]]

        reconstructed_items = {}

        for item in allocated_items:
            reconstructed_item = {}

            for feature_name in features:
                reconstructed_item[feature_name] = (
                    features[feature_name][item])

            reconstructed_items[item] = output_class(**reconstructed_item)

        return reconstructed_items


    def load_data(self, raw_data):
        # Parse the raw data according to the specification for a song
        parsed_song = bread.parse(raw_data, spec.song)

        # Check checksums
        assert parsed_song.mem_init_flag_1 == 'rb'
        assert parsed_song.mem_init_flag_2 == 'rb'
        assert parsed_song.mem_init_flag_3 == 'rb'

        # Set clocks (and check their checksums)
        self.clock = Clock(
            parsed_song.clock.hours,
            parsed_song.clock.minutes,
            parsed_song.clock.seconds,
            parsed_song.clock.checksum)

        self.total_clock = Clock(
            parsed_song.total_clock.hours,
            parsed_song.total_clock.minutes,
            parsed_song.total_clock.seconds,
            parsed_song.total_clock.checksum)

        # Stitch together allocated phrases
        self.phrases = self._reconstruct_from_alloc_table(
            parsed_song.phrase_alloc_table, spec.STEPS_PER_PHRASE, Phrase,
            {
                "notes": parsed_song.phrase_notes,
                "fx": parsed_song.phrase_fx,
                "fx_val": parsed_song.phrase_fx_val,
                "instruments": parsed_song.phrase_instruments
            })

        # Stitch together allocated chains
        self.chains = self._reconstruct_from_alloc_table(
            parsed_song.chain_alloc_table, spec.PHRASES_PER_CHAIN, Chain,
            {
                "phrases": parsed_song.chain_phrases,
                "transposes": parsed_song.chain_transposes
            })

        # Stitch together allocated tables
        self.tables = self._reconstruct_from_alloc_table(
            parsed_song.table_alloc_table, spec.STEPS_PER_TABLE, Table,
            {
                "transposes": parsed_song.table_transposes,
                "fx": parsed_song.table_fx,
                "fx_val": parsed_song.table_fx_val,
                "fx2": parsed_song.table_fx2,
                "fx2_val": parsed_song.table_fx2_val,
                "envelope": parsed_song.table_envelopes
            })

        # Extract allocated instruments
        allocated_instruments = [i for i in parsed_song.instr_alloc_table
                                 if parsed_song.instr_alloc_table[i]]

        self.instruments = {}

        instrument_class = {
            "pulse": Pulse,
            "wave": Wave,
            "kit": Kit,
            "noise": Noise
        }

        for i in allocated_instruments:
            raw_instrument = parsed_song.instruments[i]
            instr_type = raw_instrument.instrument_type

            # Construct an instrument of the appropriate type from the raw
            # instrument's fields
            self.instruments.append(instrument_class[instr_type](
                parsed_song.instrument_names[i], raw_instrument))

        self.bookmarks = parsed_song.bookmarks

        self.grooves = {}

        for i in xrange(spec.NUM_GROOVES):
            self.grooves[i] = Groove(parsed_song.grooves[i])

        # Record the sequence of chain numbers for each channel that make up
        # the song
        self.song = Song(parsed_song.song)

        self.speech_instrument = speech_instrument.SpeechInstrument(
            parsed_song.words, parsed_song.word_names)

        for field in ["tempo", "tune_setting", "key_delay", "key_repeat",
                      "font", "sync_setting", "colorset", "clone",
                      "file_changed", "power_save", "prelisten"]:
            setattr(self, field, getattr(parsed_song, field))

        self.wave_synth_overwrite_lock = parsed_song.wave_synth_overwrite_lock

        self.version_byte = parsed_song.version

        for i, synth in enumerate(parsed_song.softsynth_params):
            synth_obj = Synth(synth)
            synth_obj.waves = parsed_song.wave_frames[i]
            self.synths.append(synth_obj)

        # Bind tables
        for instrument in self.instruments:
            if instrument.table_on:
                instrument.table = self.tables[instrument.table]

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
