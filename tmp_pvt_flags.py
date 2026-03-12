"""Check tdb4 raw flags for ADBE Mask Feather."""
from __future__ import annotations
from aep_parser.kaitai.aep import Aep
from aep_parser.kaitai.utils import find_by_list_type, filter_by_list_type, find_by_type
import aep_parser.kaitai.aep_optimized  # noqa: F401

parsed = Aep.from_file("samples/bugs/29.97_fps_time_scale_3.125.aep")

# Find comp 281855 (has the mask)
for fold in filter_by_list_type(chunks=parsed.data.chunks, list_type="Fold"):
    idta = find_by_type(chunks=fold.chunks, chunk_type="idta")
    if idta.item_id == 281855:
        print(f"Found comp 281855")
        # Find layers
        for layr in filter_by_list_type(chunks=fold.chunks, list_type="Layr"):
            # Find mask parade
            for tdgp in filter_by_list_type(chunks=layr.chunks, list_type="tdgp"):
                # look for tdsn with mask feather
                for sub in filter_by_list_type(chunks=tdgp.chunks, list_type="tdbs"):
                    try:
                        tdsn = find_by_type(chunks=sub.chunks, chunk_type="tdsn")
                        name = tdsn.chunk.data.decode("utf-8", errors="replace").rstrip("\x00")
                        tdb4 = find_by_type(chunks=sub.chunks, chunk_type="tdb4")
                        if "Mask Feather" in name or tdsn.chunk.data.decode("utf-8", errors="replace").find("Feather") >= 0:
                            print(f"  name={name}")
                            print(f"  is_spatial={tdb4.is_spatial}")
                            print(f"  no_value={tdb4.no_value}")
                            print(f"  color={tdb4.color}")
                            print(f"  integer={tdb4.integer}")
                            print(f"  vector={tdb4.vector}")
                            print(f"  dimensions={tdb4.dimensions}")
                    except:
                        pass
        break
