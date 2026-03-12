"""Check raw parT chunk bytes for comp 11516."""
from __future__ import annotations

from aep_parser.kaitai.aep import Aep
from aep_parser.kaitai.utils import (
    find_by_type,
    find_by_list_type,
    str_contents,
)

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


for item_id_target in (155, 11516):
    all_items = find_all(root_chunks, "Item")
    for item_chunk in all_items:
        try:
            idta = find_by_type(chunks=item_chunk.chunks, chunk_type="idta")
            if idta.id != item_id_target:
                continue
        except Exception:
            continue

        all_sspc = find_all(item_chunk.chunks, "sspc")
        for sspc in all_sspc:
            fnam = find_by_type(chunks=sspc.chunks, chunk_type="fnam")
            name = str_contents(fnam.chunk)
            if name != "Transform":
                continue

            print(f"=== Item {item_id_target} - sspc '{name}' ===")

            # Find parT
            try:
                part = find_by_list_type(chunks=sspc.chunks, list_type="parT")
                print(f"  parT chunk_type={part.chunk_type}, list_type={part.list_type}")
                print(f"  parT child count: {len(part.chunks)}")
                for i, c in enumerate(part.chunks):
                    ct = c.chunk_type
                    lt = getattr(c, "list_type", None)
                    sz = getattr(c, "len_data", None)
                    print(f"    [{i}] type={ct} list={lt} size={sz}")
                    if ct == "tdmn":
                        print(f"         tdmn={str_contents(c)}")
            except Exception as e:
                print(f"  NO parT: {e}")
