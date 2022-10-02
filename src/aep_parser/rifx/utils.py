from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


from aep_parser.kaitai.aep import Aep


"""
based on https://github.com/rioam2/rifx/blob/a8114e272da2bbedae9b869d16b0d4ff45a91b12/types.go
"""


def sublist_filter(blocks, identifier):
    """
    Return a slice of child lists that have the provided identifier.
    """
    result = [
        block.data
        for block in blocks
        if block.block_type == Aep.ChunkType.lst
        and block.data.identifier == identifier
    ]
    return result


def find(blocks, func):
    """
    Perform a basic find operation over a list's blocks.
    """
    for block in blocks:
        if func(block):
            return block


def find_by_type(blocks, block_type):
    """
    Perform a find operation over a list's blocks predicated upon block type.
    """
    return find(blocks, lambda block: block.block_type == block_type)


def sublist_merge(blocks, identifier):
    """
    Filter sublists with the specified identifier and concatenates their blocks in a new list.
    """
    sublists = sublist_filter(blocks, identifier)
    return sum(sublists, [])


def sublist_find(blocks, identifier):
    """
    Perform a basic find operation over a list's child list elements based on identifer.
    """
    return [
        block
        for block in blocks
        if block.block_type == Aep.ChunkType.lst
        and block.data.identifier == identifier
    ]
