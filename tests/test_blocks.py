import os, sys, json

sys.path.append(
    os.path.dirname(os.path.abspath(os.path.join(__file__, os.path.pardir))))

import common.blockutils as bl
import common.filepack as filepack

def test_simple_read_write():
    data = [i % 10 for i in xrange(bl.BLOCK_SIZE * 5 + 17)]

    reader = bl.BlockReader()
    writer = bl.BlockWriter()
    factory = bl.BlockFactory()

    block_ids = writer.write(data, factory)

    blocks = {}

    for i in block_ids:
        blocks[i] = factory.blocks[i]

    recovered_data = reader.read(blocks)

    assert data == recovered_data

def test_sample_file():
    reader = bl.BlockReader()
    writer = bl.BlockWriter()
    factory = bl.BlockFactory()

    with open("test_data/sample_song_blocks.json", "r") as fp:
        song_block_data = json.load(fp)

    song_blocks = {}

    # Dummy block for file table header
    factory.new_block()

    for i, key in enumerate(sorted(map(int, song_block_data.keys()))):
        song_blocks[i + 1] = factory.new_block()
        song_blocks[i + 1].data = bytearray(song_block_data[str(key)])

    with open("test_data/sample_song_compressed.json", "r") as fp:
        compressed = json.load(fp)

    assembled_from_blocks = reader.read(song_blocks)
    assert assembled_from_blocks == compressed


    factory = bl.BlockFactory()
    factory.new_block()

    block_ids = writer.write(assembled_from_blocks, factory)

    assert len(block_ids) == 10

    block_map = dict(factory.blocks)
    del block_map[0]

    assembled_from_write = reader.read(block_map)

    assert assembled_from_write == compressed
