import bread as b

def padded_hex(pad_count):
    return lambda x: ("0x%%0%dx" % (pad_count)) % (x)

EMPTY_BLOCK = 0xff

# File management structure (starts at 0x8000)
compressed_sav_file = [
    # Up to 32 files (songs) can be saved to one cartridge
    ("filenames", b.array(32, b.string(8))),
    # Each file has a monotonically increasing version number
    ("file_versions", b.array(32, b.byte)),
    b.padding(30 * 8),
    ("sram_init_check", b.string(2)), # set to 'jk' on init
    # The file that is currently active
    ("active_file", b.byte),
    # Table mapping blocks to files.
    ("block_alloc_table", b.array(191, b.byte))
]

# Should be 0x4000 bytes long
sample_kit = [
    ("magic_number", b.string(2)), # should be 0x60, 0x40
    # The address of the first byte after each sample, or 0 if the sample is
    # unused
    ("sample_end_addresses", b.array(15, b.string(2))),
    b.padding(2 * 8),
    # For samples with names less than three characters long, sample names are
    # padded with -. Unused sample names are full of nulls.
    ("sample_names", b.array(15, b.string(3))),
    b.padding(8),
    # n/a?
    b.padding(8 * 2),
    ("kit_name", b.string(6)),
    # n/a?
    b.padding(8 * 4),
    # Samples 8-1, then 15-9
    ("force_loop", b.array(15, b.bit)),
    # n/a?
    b.padding(8 * 2),
    # 4 bits per sample at 11468Hz, in chunks of 16 bytes
    ("sample_data", b.array(127, b.array(128, b.nibble)))
]

# Max. number of phrases
NUM_PHRASES = 255

# Max. number of tables
NUM_TABLES = 32

# Number of soft-synths
NUM_SYNTHS = 16

# Waves per soft-synth
WAVES_PER_SYNTH = 16

# Number of frames per wave
FRAMES_PER_WAVE = 32

# Number of entries in each table
ENTRIES_PER_TABLE = 16

# Max. number of instruments
NUM_INSTRUMENTS = 64

# Max. number of sequences in the whole song
NUM_SONG_CHAINS = 256

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

# Max. length of a "word"
WORD_LENGTH = 0x20

# Number of "words" in the speech instrument
NUM_WORDS = 42

chain = [
    ("pu1", b.byte, {"str_format": padded_hex(2)}),
    ("pu2", b.byte, {"str_format": padded_hex(2)}),
    ("wav", b.byte, {"str_format": padded_hex(2)}),
    ("noi", b.byte, {"str_format": padded_hex(2)})]

pulse_instrument = [
    ("envelope", b.byte, {"str_format": padded_hex(2)}),
    ("phase_transpose", b.byte),
    b.padding(1),
    # If false, sound length is UNLIM
    ("has_sound_length", b.boolean),
    ("sound_length", b.intX(6)),
    ("sweep", b.byte),
    b.padding(3),
    ("automate_1", b.boolean),
    ("automate_2", b.boolean),
    ("vibrato", [
        ("type",b.semi_nibble),
        ("direction", b.enum(1, {
            0: "down",
            1: "up"
        }))
    ]),
    b.padding(2),
    ("table_on", b.boolean),
    ("table", b.intX(5)),
    ("wave", b.semi_nibble),
    ("phase_finetune", b.nibble),
    ("pan", b.enum(2, {
        0: "Invalid",
        1: "L",
        2: "R",
        3: "LR"
    })),
    b.padding(2 * 8),
    ("_default_instr_byte_1", b.byte, {"str_format": padded_hex(2)}),
    b.padding(3 * 8),
    ("_default_instr_byte_2", b.byte, {"str_format": padded_hex(2)}),
    b.padding(8)
]

wave_instrument = [
    b.padding(1),
    ("volume", b.enum(2, {
        0: 0,
        1: 3,
        2: 2,
        3: 1
    })),
    b.padding(5),
    ("synth", b.nibble),
    ("repeat", b.nibble),
    b.padding(8 * 2 + 3),
    ("automate_1", b.boolean),
    ("automate_2", b.boolean),
    ("vibrato", [
        ("type",b.semi_nibble),
        ("direction", b.enum(1,{
            0: "down",
            1: "up"
        }))
    ]),
    b.padding(2),
    ("table_on", b.boolean),
    ("table", b.intX(5)),
    b.padding(6),
    ("pan", b.enum(2, {
        0: "Invalid",
        1: "L",
        2: "R",
        3: "LR"
    })),
    b.padding(8 + 6),
    ("play_type", b.enum(2, {
        0: "once",
        1: "loop",
        2: "ping-pong",
        3: "manual"
    })),
    b.padding(8 * 4),
    ("steps", b.nibble),
    ("speed", b.nibble, {"str_format": hex, "offset": 1}),
    b.padding(8)
]

kit_instrument = [
    ("volume", b.byte),
    ("keep_attack_1", b.boolean),
    ("half_speed", b.boolean),
    ("kit", b.intX(6), {"offset": 1}),
    # 0 == "auto"
    ("length_1", b.byte),
    b.padding(9),
    ("loop_1", b.boolean),
    ("loop_2", b.boolean),
    ("automate_1", b.boolean),
    ("automate_2", b.boolean),
    ("vibrato", [
        ("type",b.semi_nibble),
        ("direction", b.enum(1,{
            0: "down",
            1: "up"
        }))
    ]),
    b.padding(2),
    ("table_on", b.boolean),
    ("table", b.intX(5)),
    b.padding(6),
    ("pan", b.enum(2, {
        0: "Invalid",
        1: "L",
        2: "R",
        3: "LR"
    })),
    ("pitch", b.byte),
    ("keep_attack_2", b.boolean),
    b.padding(1),
    ("kit_2", b.intX(6), {"offset": 1}),
    ("dist_type", b.enum(8, {
        0xd0: "clip",
        0xd1: "shape",
        0xd2: "shap2",
        0xd3: "wrap"
    })),
    # 0 == "auto"
    ("length_2", b.byte),
    ("offset", b.byte),
    ("offset_2", b.byte),
    b.padding(8 * 2)
]

noise_instrument = [
    ("envelope", b.byte),
    ("s_cmd", b.enum(8, {
        0: "free",
        1: "stable"
    })),
    b.padding(1),
    # If false, sound length is UNLIM
    ("has_sound_length", b.boolean),
    ("sound_length", b.intX(6)),
    ("sweep", b.byte),
    b.padding(3),
    ("automate_1", b.boolean),
    ("automate_2", b.boolean),
    b.padding(5),
    ("table_on", b.boolean),
    ("table", b.intX(5)),
    b.padding(6),
    ("pan", b.enum(2, {
        0: "Invalid",
        1: "L",
        2: "R",
        3: "LR"
    })),
    b.padding(8 * 8)
]

instrument = [
    ("instrument_type", b.enum(8, {
        0: "pulse",
        1: "wave",
        2: "kit",
        3: "noise"
    }, default = "invalid")),
    (b.CONDITIONAL, "instrument_type", {
        "pulse" : pulse_instrument,
        "wave" : wave_instrument,
        "kit" : kit_instrument,
        "noise" : noise_instrument,
        "invalid": [b.padding(15 * 8)]
    })
]

softsynth_sound_params = [
    ("volume", b.byte),
    ("filter_cutoff", b.byte),
    ("phase_amount", b.byte),
    ("vertical_shift", b.byte)
]

softsynth = [
    ("waveform", b.enum(8, {
        0: "sawtooth",
        1: "square",
        2: "sine"
    })),
    ("filter_type", b.enum(8, {
        0: "lowpass",
        1: "highpass",
        2: "bandpass",
        3: "allpass"
    })),
    ("filter_resonance", b.byte),
    ("distortion", b.enum(8, {
        0: "clip",
        1: "wrap"
    })),
    ("phase_type", b.enum(8, {
        0: "normal",
        1: "resync",
        2: "resync2"
    })),
    ("start", softsynth_sound_params),
    ("end", softsynth_sound_params),
    b.padding(8 * 3)
]

table_command = [
    ("fx", b.array(NUM_TABLES, b.array(STEPS_PER_TABLE, b.enum(8, {
        0: '-',
        1: 'A',
        2: 'C',
        4: 'E',
        5: 'F',
        6: 'G',
        7: 'H',
        8: 'K',
        9: 'L',
        10: 'M',
        11: 'O',
        12: 'P',
        13: 'R',
        14: 'S',
        15: 'T',
        16: 'V',
        17: 'W',
        18: 'Z'
    })))),
    ("val", b.array(NUM_TABLES, b.array(STEPS_PER_TABLE, b.byte)))
]

song = [
    ("phrase_notes", b.array(NUM_PHRASES, b.array(STEPS_PER_PHRASE, b.byte))),
    ("bookmarks", b.array(64, b.byte)),
    b.padding(96 * 8),
    ("grooves", b.array(NUM_GROOVES, b.array(STEPS_PER_GROOVE, b.byte))),
    ("song", b.array(NUM_SONG_CHAINS, chain)),
    ("table_envelopes", b.array(NUM_TABLES, b.array(STEPS_PER_TABLE, b.byte))),
    ("words", b.array(NUM_WORDS, b.array(WORD_LENGTH, b.byte))),
    ("word_names", b.array(NUM_WORDS, b.string(4))),
    # Set to 'rb' on init
    ("mem_init_flag_1", b.string(2)),
    ("instrument_names", b.array(NUM_INSTRUMENTS, b.string(5))),
    b.padding(70 * 8),
    # Beginning of bank 1
    b.padding(32 * 8),
    ("table_alloc_table", b.array(NUM_TABLES, b.byte)),
    ("instr_alloc_table", b.array(NUM_INSTRUMENTS, b.byte)),
    ("chain_phrases", b.array(
        NUM_CHAINS, b.array(PHRASES_PER_CHAIN, b.byte))),
    ("chain_transposes", b.array(
        NUM_CHAINS, b.array(PHRASES_PER_CHAIN, b.byte))),
    ("instruments", b.array(NUM_INSTRUMENTS, instrument)),
    ("table_transposes", b.array(NUM_TABLES, b.array(STEPS_PER_TABLE, b.byte))),
    ("table_cmd1", table_command),
    ("table_cmd2", table_command),
    # Set to 'rb' on init
    ("mem_init_flag_2", b.string(2)),
    ("phrase_alloc_table", b.array(NUM_PHRASES, b.boolean)),
    # There are only 255 valid phrases, but the allocation table is 256 bits
    # long, so we ignore the last bit
    b.padding(1),
    ("chain_alloc_table", b.array(NUM_CHAINS, b.boolean)),
    ("softsynth_params", b.array(NUM_SYNTHS, softsynth)),
    ("clock", [
        ("hours", b.byte),
        ("minutes", b.byte)]),
    ("tempo", b.byte),
    ("tune_setting", b.byte),
    ("total_clock", [
        ("days", b.byte),
        ("hours", b.byte),
        ("minutes", b.byte),
        ("checksum", b.byte)
    ]),
    ("key_delay", b.byte),
    ("key_repeat", b.byte),
    ("font", b.byte),
    ("sync_setting", b.byte),
    ("colorset", b.byte),
    b.padding(8),
    ("clone", b.enum(8, {
        0: "deep",
        1: "slim"
    })),
    ("file_changed", b.byte),
    ("power_save", b.byte),
    ("prelisten", b.byte),
    ("wave_synth_overwrite_lock", b.array(2, b.byte)),
    b.padding(8 * 58),
    # Beginning of bank 2
    ("phrase_fx", b.array(NUM_PHRASES, b.array(STEPS_PER_PHRASE, b.byte))),
    ("phrase_fx_val", b.array(NUM_PHRASES, b.array(STEPS_PER_PHRASE, b.byte))),
    b.padding(32 * 8),
    # Beginning of bank 3
    ("wave_frames",
     b.array(NUM_SYNTHS,
             b.array(WAVES_PER_SYNTH,
                     b.array(FRAMES_PER_WAVE, b.nibble)))),
    ("phrase_instruments",
     b.array(NUM_PHRASES, b.array(STEPS_PER_PHRASE, b.byte))),
    # Set to 'rb' on init
    ("mem_init_flag_3", b.string(2)),
    b.padding(13 * 8),
    ("version", b.byte)
]

# .lsdsng format
lsdsng_preamble = [
    ("name", b.string(8)),
    ("version", b.byte)
]
