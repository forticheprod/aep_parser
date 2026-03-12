"""Check tdb4 flags for effect properties in both comps."""
from __future__ import annotations

from aep_parser.kaitai.aep import Aep
from aep_parser.kaitai.utils import (
    find_by_type,
    find_by_list_type,
    filter_by_list_type,
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


# Find all Item chunks
all_items = find_all(root_chunks, "Item")
print(f"Found {len(all_items)} Item chunks")

for item_chunk in all_items:
    try:
        idta = find_by_type(chunks=item_chunk.chunks, chunk_type="idta")
        item_id = idta.id
    except Exception:
        item_id = -1
    try:
        pin_chunk = find_by_type(chunks=item_chunk.chunks, chunk_type="pin ")
        item_name = str_contents(pin_chunk.chunk)
    except Exception:
        item_name = "?"

    if item_id not in (155, 11516):
        continue

    print(f"\n=== Item id={item_id} ===")
    layr_chunks = filter_by_list_type(chunks=item_chunk.chunks, list_type="Layr")
    if not layr_chunks:
        print("  No layers")
        continue

    layr = layr_chunks[0]
    sspc_chunks = []
    try:
        sspc_chunks = filter_by_list_type(chunks=layr.chunks, list_type="sspc")
    except Exception:
        pass

    if not sspc_chunks:
        print("  No sspc in first layer")
        continue

    for sspc in sspc_chunks:
        fnam = find_by_type(chunks=sspc.chunks, chunk_type="fnam")
        name = str_contents(fnam.chunk)
        print(f"  sspc: {name}")

        try:
            find_by_list_type(chunks=sspc.chunks, list_type="parT")
            print("    has parT: True")
        except Exception:
            print("    has parT: False")

        try:
            tdgp = find_by_list_type(chunks=sspc.chunks, list_type="tdgp")
        except Exception:
            continue

        for chunk in tdgp.chunks:
            if hasattr(chunk, "list_type") and chunk.list_type == "tdbs":
                try:
                    tdsn = find_by_type(chunks=chunk.chunks, chunk_type="tdsn")
                    prop_name = str_contents(tdsn.chunk)
                except Exception:
                    prop_name = "?"

                try:
                    tdmn = find_by_type(chunks=chunk.chunks, chunk_type="tdmn")
                    mn = str_contents(tdmn)
                except Exception:
                    mn = "?"

                try:
                    tdb4 = find_by_type(chunks=chunk.chunks, chunk_type="tdb4")
                    print(
                        f"    {mn} ('{prop_name}'): "
                        f"int={tdb4.integer}, vec={tdb4.vector}, "
                        f"dim={tdb4.dimensions}, spatial={tdb4.is_spatial}, "
                        f"color={tdb4.color}"
                    )
                except Exception as e:
                    print(f"    {mn}: tdb4 error: {e}")
