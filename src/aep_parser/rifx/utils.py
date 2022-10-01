from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


from aep_parser.kaitai.aep import Aep


def sublist_filter(blocks, identifier):
    """
    Return a slice of child lists that have the provided identifier.
    """
    filtered = [
        block
        for block in blocks
        if block.block_type == Aep.ChunkType.LIST
        and block.data.identifier == identifier
    ]
    return [
        block.data
        for block in filtered
    ]


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
        block.data
        for block in blocks
        if block.block_type == Aep.ChunkType.LIST
        and block.data.identifier == identifier
    ]
