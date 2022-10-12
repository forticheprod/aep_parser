from __future__ import absolute_import
from __future__ import unicode_literals


from aep_parser.kaitai.aep import Aep


"""
based on https://github.com/rioam2/rifx/blob/a8114e272da2bbedae9b869d16b0d4ff45a91b12/types.go
"""


def find_block(blocks, func):
    """
    Perform a basic find operation over a blocks list.
    """
    for block in blocks:
        if func(block):
            return block


def find_by_type(blocks, block_type):
    """
    Perform a find operation over a blocks list predicated upon block type.
    """
    return find_block(
        blocks,
        lambda block: block.block_type == block_type
    )


def find_by_identifier(blocks, identifier):
    """
    Perform a find operation over a blocks list predicated upon block type.
    """
    return find_block(
        blocks,
        lambda block: (
            block.block_type == Aep.ChunkType.lst
            and block.data.identifier == identifier
        )
    )

def filter_blocks(blocks, func):
    """
    Perform a basic filter operation over a blocks list.
    """
    return list(filter(func, blocks))


def filter_by_identifier(blocks, identifier):
    """
    Return blocks that have the provided identifier.
    """
    return filter_blocks(
        blocks,
        lambda block: (
            block.block_type == Aep.ChunkType.lst
            and block.data.identifier == identifier
        )
    )


def filter_by_type(blocks, block_type):
    """
    Return blocks that have the provided block type.
    """
    return filter_blocks(
        blocks,
        lambda block: (
            block.block_type == block_type
        )
    )

def str_contents(block):
    text = block.data.data
    return text.rstrip("\x00")
