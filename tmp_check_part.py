"""Investigate parT contents for both sspc instances."""
from __future__ import annotations

from aep_parser.kaitai.aep import Aep
from aep_parser.kaitai.utils import (
    find_by_type,
    find_by_list_type,
    filter_by_list_type,
    str_contents,
)
from aep_parser.parsers.property import parse_effect_param_defs
from aep_parser.parsers.utils import get_chunks_by_match_name

raw = Aep.from_file("samples/bugs/29.97_fps_time_scale_3.125.aep")
root_chunks = raw.data.chunks


def find_all(chunks, list_type):
    results = []
    for c in chunks:
        if hasattr(c, "list_type") and c.list_type == list_type:
            results.append(c)
        if hasattr(c, "chunks") and c.chunks:
            results.extend(find_all(c.chunks, list_type))
    return results


# Check EfdG at project level
print("=== Project-level EfdG ===")
try:
    efdg = find_by_list_type(chunks=root_chunks, list_type="EfdG")
    efdf_chunks = filter_by_list_type(chunks=efdg.chunks, list_type="EfDf")
    print(f"  Found {len(efdf_chunks)} EfDf chunks")
    for efdf in efdf_chunks:
        tdmn = find_by_type(chunks=efdf.chunks, chunk_type="tdmn")
        mn = str_contents(tdmn)
        sspc = find_by_list_type(chunks=efdf.chunks, list_type="sspc")
        defs = parse_effect_param_defs(sspc.chunks)
        print(f"  {mn}: {len(defs)} param defs")
except Exception as e:
    print(f"  No EfdG: {e}")


# Check both comp instances
all_items = find_all(root_chunks, "Item")
for item_chunk in all_items:
    try:
        idta = find_by_type(chunks=item_chunk.chunks, chunk_type="idta")
        item_id = idta.id
    except Exception:
        continue
    if item_id not in (155, 11516):
        continue

    print(f"\n=== Item id={item_id} ===")
    all_sspc = find_all(item_chunk.chunks, "sspc")
    for sspc in all_sspc:
        fnam = find_by_type(chunks=sspc.chunks, chunk_type="fnam")
        name = str_contents(fnam.chunk)
        print(f"  sspc: {name}")

        # Check parT directly
        try:
            part = find_by_list_type(chunks=sspc.chunks, list_type="parT")
            cbm = get_chunks_by_match_name(part)
            print(f"    parT has {len(cbm)} match_name groups")
            for i, (mn, chunks) in enumerate(cbm.items()):
                ctypes = [c.chunk_type for c in chunks]
                print(f"      [{i}] {mn}: {ctypes}")
        except Exception as e:
            print(f"    NO parT: {e}")
