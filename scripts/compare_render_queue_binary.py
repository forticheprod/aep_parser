"""
Compare binary data between AEP files to identify render queue settings bytes.

This script analyzes the binary differences in render-related chunks
to reverse-engineer the binary format of render queue settings.

FINDINGS:
=========
The render settings are stored in: LRdr/LIST(list)/ldat (2246 bytes)

Key byte offsets:
- Offset 45 (0x002d): Template indicator (30=Best Settings template, 24=Custom)
- Offset 57 (0x0039): Quality (2=Best, 1=Draft, 0=Wireframe)
- Offset 59 (0x003b): Resolution H divisor (1=Full, 2=Half, 3=Third, 4=Quarter)
- Offset 61 (0x003d): Resolution V divisor (same values as H)
- Offset 2141 (0x085d): Custom settings flag (0=using template, 1=custom)
- Offset 2178-2181 (0x0882): Color depth (0xFFFFFFFF=Current, 0=8-bit, 1=16-bit, 2=32-bit)

Other chunks:
- LRdr/Rout: offset 4 changes to 0 when using custom settings (flag?)
- LRdr/Rhed: Static header (20 bytes)
- LRdr/LSIf/ARsi: Static render settings info (1872 bytes)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aep_parser.kaitai.aep_optimized import Aep
from aep_parser.kaitai.utils import find_by_list_type


def parse_aep(filepath: Path) -> Aep:
    """Parse an AEP file and return the Aep object."""
    return Aep.from_file(str(filepath))


def get_render_settings_ldat(filepath: str | Path) -> bytes | None:
    """
    Get the large ldat chunk (2246 bytes) that contains render queue settings.
    
    This is found at: LRdr/LIST(list)/ldat
    """
    aep = Aep.from_file(str(filepath))
    lrdr = find_by_list_type(chunks=aep.data.chunks, list_type="LRdr")
    
    for c in lrdr.data.chunks:
        if c.chunk_type == "LIST" and hasattr(c.data, "list_type"):
            if c.data.list_type == "list":
                for cc in c.data.chunks:
                    if cc.chunk_type == "ldat" and len(cc._raw_data) > 1000:
                        return cc._raw_data
    return None


def get_rout_chunk(filepath: str | Path) -> bytes | None:
    """Get the Rout chunk data."""
    aep = Aep.from_file(str(filepath))
    lrdr = find_by_list_type(chunks=aep.data.chunks, list_type="LRdr")
    
    for c in lrdr.data.chunks:
        if c.chunk_type == "Rout":
            return c._raw_data
    return None


def analyze_render_settings(data: bytes) -> dict:
    """
    Parse the render settings from the ldat binary data.
    
    Returns a dict with the extracted settings.
    """
    return {
        "template_indicator": data[45],
        "is_custom": data[45] != 30,  # 30 = "Best Settings" template
        "quality": data[57],  # 2=Best, 1=Draft, 0=Wireframe
        "quality_name": {2: "Best", 1: "Draft", 0: "Wireframe"}.get(data[57], f"Unknown({data[57]})"),
        "resolution_h_divisor": data[59],
        "resolution_v_divisor": data[61],
        "resolution_name": {
            (1, 1): "Full",
            (2, 2): "Half", 
            (3, 3): "Third",
            (4, 4): "Quarter"
        }.get((data[59], data[61]), f"Custom({data[59]}x{data[61]})"),
        "custom_settings_flag": data[2141],
        "color_depth_raw": int.from_bytes(data[2178:2182], "big"),
        "color_depth_name": {
            0xFFFFFFFF: "Current/Default",
            0: "8-bit",
            1: "16-bit", 
            2: "32-bit"
        }.get(int.from_bytes(data[2178:2182], "big"), "Unknown"),
        "template_name": data[80:144].decode("ascii", errors="ignore").rstrip("\x00"),
    }


def compare_bytes(base: bytes, other: bytes) -> list[tuple[int, int | None, int | None]]:
    """Compare two byte sequences and return differences."""
    diffs = []
    max_len = max(len(base), len(other))
    
    for i in range(max_len):
        base_val = base[i] if i < len(base) else None
        other_val = other[i] if i < len(other) else None
        
        if base_val != other_val:
            diffs.append((i, base_val, other_val))
    
    return diffs


def main():
    samples_dir = Path(__file__).parent.parent / "samples" / "debug"
    
    # Define the files to compare
    files_to_compare = {
        "base": samples_dir / "render_queue_base.aep",
        "quality_draft": samples_dir / "render_queue_custom_quality_draft.aep",
        "quality_wireframe": samples_dir / "render_queue_custom_quality_wireframe.aep",
        "resolution_half": samples_dir / "render_queue_custom_resolution_half.aep",
        "resolution_quarter": samples_dir / "render_queue_custom_resolution_quarter.aep",
        "resolution_third": samples_dir / "render_queue_custom_resolution_third.aep",
        "color_8bit": samples_dir / "render_queue_color_depth_8.aep",
        "color_16bit": samples_dir / "render_queue_color_depth_16.aep",
        "color_32bit": samples_dir / "render_queue_color_depth_32.aep",
    }
    
    print("=" * 80)
    print("RENDER QUEUE BINARY ANALYSIS")
    print("=" * 80)
    print()
    
    # Parse all files and extract settings
    results = {}
    for name, path in files_to_compare.items():
        if not path.exists():
            print(f"SKIP: {name} (file not found)")
            continue
        
        ldat = get_render_settings_ldat(path)
        if ldat is None:
            print(f"ERROR: {name} - no render settings ldat found")
            continue
        
        settings = analyze_render_settings(ldat)
        results[name] = {"ldat": ldat, "settings": settings}
    
    # Print parsed settings for each file
    print("PARSED RENDER SETTINGS:")
    print("-" * 80)
    print(f"{'File':<25} {'Quality':<12} {'Resolution':<12} {'Color Depth':<15} {'Custom'}")
    print("-" * 80)
    
    for name, data in results.items():
        s = data["settings"]
        print(f"{name:<25} {s['quality_name']:<12} {s['resolution_name']:<12} {s['color_depth_name']:<15} {s['custom_settings_flag']}")
    
    print()
    print("=" * 80)
    print("BYTE DIFFERENCES FROM BASE")
    print("=" * 80)
    
    if "base" not in results:
        print("ERROR: Base file not found")
        return
    
    base_ldat = results["base"]["ldat"]
    
    for name, data in results.items():
        if name == "base":
            continue
        
        diffs = compare_bytes(base_ldat, data["ldat"])
        if diffs:
            print(f"\n{name}:")
            for offset, bv, ov in diffs:
                bv_str = f"{bv:3d} (0x{bv:02x})" if bv is not None else "N/A"
                ov_str = f"{ov:3d} (0x{ov:02x})" if ov is not None else "N/A"
                
                # Add context for known offsets
                context = ""
                if offset == 45:
                    context = " <- template indicator"
                elif offset == 57:
                    context = " <- quality"
                elif offset in (59, 61):
                    context = " <- resolution divisor"
                elif offset == 2141:
                    context = " <- custom settings flag"
                elif 2178 <= offset <= 2181:
                    context = " <- color depth"
                
                print(f"  offset {offset:4d} (0x{offset:04x}): {bv_str} -> {ov_str}{context}")
    
    print()
    print("=" * 80)
    print("BINARY STRUCTURE SUMMARY")
    print("=" * 80)
    print()
    print("Chunk: LRdr/LIST(list)/ldat (2246 bytes)")
    print()
    print("Key offsets in ldat:")
    print("  Offset 45 (0x002d): Template indicator")
    print("    30 (0x1e) = Best Settings template")
    print("    24 (0x18) = Custom/modified settings")
    print()
    print("  Offset 57 (0x0039): Quality setting")
    print("    2 = Best")
    print("    1 = Draft")
    print("    0 = Wireframe")
    print()
    print("  Offset 59 (0x003b): Resolution H divisor")
    print("  Offset 61 (0x003d): Resolution V divisor")
    print("    1 = Full, 2 = Half, 3 = Third, 4 = Quarter")
    print()
    print("  Offset 2141 (0x085d): Custom settings flag")
    print("    0 = Using template")
    print("    1 = Custom settings")
    print()
    print("  Offset 2178-2181 (0x0882-0x0885): Color Depth (big-endian u32)")
    print("    0xFFFFFFFF = Current/Default")
    print("    0x00000000 = 8-bit")
    print("    0x00000001 = 16-bit")
    print("    0x00000002 = 32-bit")
    print()
    print("  Offset 80-143: Template name (64 bytes, null-padded ASCII)")


if __name__ == "__main__":
    main()
