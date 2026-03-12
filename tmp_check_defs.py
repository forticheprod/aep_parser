"""Debug: check effect_param_defs and why comp 11516 has wrong pct."""
from __future__ import annotations

from aep_parser import parse
from aep_parser.kaitai.aep import Aep
from aep_parser.kaitai.utils import (
    find_by_type,
    find_by_list_type,
    filter_by_list_type,
    str_contents,
)

app = parse("samples/bugs/29.97_fps_time_scale_3.125.aep")
project = app.project

# Check project-level effect param defs
print("=== Project-level _effect_param_defs ===")
for eff_mn, param_defs in project._effect_param_defs.items():
    print(f"  {eff_mn}:")
    for param_mn, pdef in param_defs.items():
        pct = pdef.get("property_control_type")
        print(f"    {param_mn}: pct={pct}")


# Check raw binary: does comp 11516's layer have parT in sspc?
raw = Aep.from_file("samples/bugs/29.97_fps_time_scale_3.125.aep")
root_chunks = raw.data.chunks
fold_chunks = filter_by_list_type(chunks=root_chunks, list_type="Fold")

for fold_chunk in fold_chunks:
    item_chunks = filter_by_list_type(chunks=fold_chunk.chunks, list_type="Item")
    for item_chunk in item_chunks:
        try:
            idta_chunk = find_by_type(chunks=item_chunk.chunks, chunk_type="idta")
            item_id = idta_chunk.item_id
        except Exception:
            continue

        if item_id in (155, 11516):
            print(f"\n=== Item id={item_id} ===")
            try:
                layr_chunks = filter_by_list_type(
                    chunks=item_chunk.chunks, list_type="Layr"
                )
                for layr_chunk in layr_chunks[:1]:
                    sspc_chunks = filter_by_list_type(
                        chunks=layr_chunk.chunks, list_type="sspc"
                    )
                    for sspc_chunk in sspc_chunks:
                        fnam = find_by_type(
                            chunks=sspc_chunk.chunks, chunk_type="fnam"
                        )
                        name = str_contents(fnam.chunk)
                        print(f"  sspc: {name}")
                        try:
                            find_by_list_type(
                                chunks=sspc_chunk.chunks, list_type="parT"
                            )
                            print("    has parT: True")
                        except Exception:
                            print("    has parT: False")
            except Exception as e:
                print(f"  Error: {e}")
