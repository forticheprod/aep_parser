from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


from aep_parser.kaitai.aep import Aep


"""
based on https://github.com/rioam2/rifx/blob/a8114e272da2bbedae9b869d16b0d4ff45a91b12/types.go
"""


def find(blocks, func):
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
    return find(
        blocks,
        lambda block: block.block_type == block_type
    )


def find_by_identifier(blocks, identifier):
    """
    Perform a find operation over a blocks list predicated upon block type.
    """
    return find(
        blocks,
        lambda block: (
            block.block_type == Aep.ChunkType.lst
            and block.data.identifier == identifier
        )
    )


def sublist_find(blocks, func):
    """
    Perform a basic find operation over a blocks list's child elements.
    """
    for block in blocks:
        if block.block_type != Aep.ChunkType.lst:
            continue
        for sub_block in block.data.blocks.blocks:
            if func(sub_block):
                return sub_block


def sublist_find_by_identifier(blocks, identifier):
    """
    Perform a find operation over a blocks list's child list elements based on identifer.
    """
    return sublist_find(
        blocks,
        lambda block: (
            block.block_type == Aep.ChunkType.lst
            and block.data.identifier == identifier
        )
    )


def sublist_find_by_type(blocks, block_type):
    """
    Perform a find operation over a blocks list's child list elements based on block type.
    """
    return sublist_find(
        blocks,
        lambda block: (
            block.block_type == block_type
        )
    )


def sublist_filter(blocks, func):
    """
    Perform a basic filter operation over a blocks list's child elements.
    """
    result = []
    for block in blocks:
        if block.block_type != Aep.ChunkType.lst:
            continue
        for sub_block in block.data.blocks.blocks:
            if func(sub_block):
                result.append(sub_block)
    return result


def sublist_filter_by_identifier(blocks, identifier):
    """
    Return child list blocks that have the provided identifier.
    """
    return sublist_filter(
        blocks,
        lambda block: (
            block.block_type == Aep.ChunkType.lst
            and block.data.identifier == identifier
        )
    )


def sublist_filter_by_type(blocks, block_type):
    """
    Return child list blocks that have the provided block type.
    """
    return sublist_filter(
        blocks,
        lambda block: (
            block.block_type == block_type
        )
    )
