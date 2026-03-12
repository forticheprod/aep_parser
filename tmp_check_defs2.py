"""Check parse_effect_param_defs for both comps."""
from __future__ import annotations

from aep_parser.kaitai.aep import Aep
from aep_parser.kaitai.utils import (
    find_by_type,
    find_by_list_type,
    str_contents,
)
from aep_parser.parsers.property import parse_effect_param_defs

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
        try:
            param_defs = parse_effect_param_defs(sspc.chunks)
            print(f"  parse_effect_param_defs succeeded: {len(param_defs)} defs")
            for mn, pdef in param_defs.items():
                pct = pdef.get("property_control_type")
                print(f"    {mn}: pct={pct}")
        except Exception as e:
            print(f"  parse_effect_param_defs FAILED: {e}")

        # Also test get_chunks_by_match_name on tdgp
        from aep_parser.parsers.property import get_chunks_by_match_name
        try:
            tdgp = find_by_list_type(chunks=sspc.chunks, list_type="tdgp")
            chunks_by_mn = get_chunks_by_match_name(tdgp)
            print(f"  tdgp match_names: {list(chunks_by_mn.keys())}")
        except Exception as e:
            print(f"  tdgp error: {e}")
