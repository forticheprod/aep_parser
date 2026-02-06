"""Analyze render queue ldat chunk byte-by-byte to map render settings fields."""

from __future__ import annotations

from pathlib import Path
from collections import defaultdict
import struct

from aep_parser.kaitai.aep_optimized import Aep
from aep_parser.kaitai.utils import find_by_list_type, filter_by_type, find_by_type


def get_all_ldat_chunks(aep: Aep) -> list[tuple[str, bytes]]:
    """Find all ldat chunks in the file and their context."""
    results = []
    
    def search_chunks(chunks: list, path: str = ""):
        for chunk in chunks:
            chunk_type = chunk.chunk_type.strip() if hasattr(chunk, 'chunk_type') else ""
            list_type = chunk.list_type.strip() if hasattr(chunk, 'list_type') and chunk.list_type else ""
            
            if chunk_type == "ldat":
                raw_data = chunk._raw_data if hasattr(chunk, '_raw_data') else b""
                results.append((path + "/ldat", raw_data))
            
            # Recurse into LIST chunks
            if hasattr(chunk, 'chunks') and chunk.chunks:
                new_path = path + "/" + (list_type if list_type else chunk_type)
                search_chunks(chunk.chunks, new_path)
    
    search_chunks(aep.data.chunks)
    return results


def get_lrdr_ldat(aep: Aep) -> bytes | None:
    """Get the 2246-byte ldat chunk from LRdr > list (render settings)."""
    # LRdr is at top level in the file
    lrdr = find_by_list_type(aep.data.chunks, "LRdr")
    if not lrdr:
        return None
    
    # The render settings ldat is at LRdr > list > ldat (2246 bytes)
    # Not at LRdr > LItm > list > ldat (128 bytes)
    lst = find_by_list_type(lrdr.chunks, "list")
    if not lst:
        return None
    
    ldat = find_by_type(lst.chunks, "ldat")
    if not ldat:
        return None
    
    # Get raw binary data
    return ldat._raw_data if hasattr(ldat, '_raw_data') else None


def parse_file(filepath: Path) -> tuple[bytes | None, list[tuple[str, bytes]]]:
    """Parse an AEP file and return the LRdr ldat and all ldat chunks."""
    aep = Aep.from_file(str(filepath))
    lrdr_ldat = get_lrdr_ldat(aep)
    all_ldats = get_all_ldat_chunks(aep)
    return lrdr_ldat, all_ldats


def main():
    base_dir = Path("samples/debug")
    
    files = {
        "base": "render_queue_base.aep",
        "custom": "render_queue_custom.aep",
        "quality_draft": "render_queue_custom_quality_draft.aep",
        "resolution_half": "render_queue_custom_resolution_half.aep",
        "field_lower": "render_queue_field_render_lower_field_first.aep",
        "field_upper": "render_queue_field_render_upper_field_first.aep",
        "frame_blend_curr": "render_queue_frame_blending_current.aep",
        "frame_blend_off": "render_queue_frame_blending_off_for_all_layers.aep",
        "motion_blur_curr": "render_queue_motion_blur_current.aep",
        "motion_blur_off": "render_queue_motion_blur_off_for_all_layers.aep",
        "framerate_24": "render_queue_use_this_frame_rate_24.aep",
        "framerate_30": "render_queue_use_this_frame_rate_30.aep",
        "time_length_comp": "render_queue_time_span_length_of_comp.aep",
        "proxy_all": "render_queue_custom_proxy_use_use_all_proxies.aep",
        "effects_on": "render_queue_custom_effects_all_on.aep",
        "effects_off": "render_queue_custom_effects_all_off.aep",
        "solo_off": "render_queue_custom_solo_switches_all_off.aep",
        "guide_layers": "render_queue_guide_layers_current.aep",
    }
    
    # Parse all files
    print("=" * 100)
    print("PARSING FILES AND FINDING ALL ldat CHUNKS")
    print("=" * 100)
    
    data = {}
    for name, filename in files.items():
        filepath = base_dir / filename
        if not filepath.exists():
            print(f"  MISSING: {filename}")
            continue
        
        lrdr_ldat, all_ldats = parse_file(filepath)
        data[name] = lrdr_ldat
        
        print(f"\n{name} ({filename}):")
        print(f"  LRdr ldat size: {len(lrdr_ldat) if lrdr_ldat else 'N/A'} bytes")
        print(f"  All ldat chunks found:")
        for path, chunk_data in all_ldats:
            print(f"    - {path}: {len(chunk_data)} bytes")
    
    # Check if base exists
    if "base" not in data or data["base"] is None:
        print("\nERROR: Base file not found or has no LRdr ldat!")
        return
    
    base_data = data["base"]
    print(f"\n{'=' * 100}")
    print(f"BASE FILE ldat SIZE: {len(base_data)} bytes")
    print("=" * 100)
    
    # Find all differences
    print(f"\n{'=' * 100}")
    print("BYTE-BY-BYTE COMPARISON (differences from base)")
    print("=" * 100)
    
    # Group differences by offset
    differences = defaultdict(dict)  # offset -> {file_name: value}
    
    for name, ldat in data.items():
        if name == "base" or ldat is None:
            continue
        if len(ldat) != len(base_data):
            print(f"WARNING: {name} has different size: {len(ldat)} vs {len(base_data)}")
            continue
        
        for i in range(len(base_data)):
            if ldat[i] != base_data[i]:
                differences[i][name] = ldat[i]
    
    # Print differences table
    print(f"\n{'Offset':<8} {'Base':<6} {'Changed Files and Values':<80}")
    print("-" * 100)
    
    for offset in sorted(differences.keys()):
        base_val = base_data[offset]
        changes = differences[offset]
        
        # Format changes
        change_str = ", ".join([f"{name}={val:02X}" for name, val in sorted(changes.items())])
        
        # Guess what this might be
        guess = ""
        changed_files = set(changes.keys())
        
        if changed_files == {"quality_draft"}:
            guess = "Quality setting"
        elif changed_files == {"resolution_half"}:
            guess = "Resolution setting"
        elif "field_lower" in changed_files or "field_upper" in changed_files:
            if changed_files <= {"field_lower", "field_upper"}:
                guess = "Field render setting"
        elif "frame_blend_curr" in changed_files or "frame_blend_off" in changed_files:
            if changed_files <= {"frame_blend_curr", "frame_blend_off"}:
                guess = "Frame blending setting"
        elif "motion_blur_curr" in changed_files or "motion_blur_off" in changed_files:
            if changed_files <= {"motion_blur_curr", "motion_blur_off"}:
                guess = "Motion blur setting"
        elif "framerate_24" in changed_files or "framerate_30" in changed_files:
            if changed_files <= {"framerate_24", "framerate_30"}:
                guess = "Frame rate setting"
        elif changed_files == {"time_length_comp"}:
            guess = "Time span setting"
        elif changed_files == {"proxy_all"}:
            guess = "Proxy use setting"
        elif "effects_on" in changed_files or "effects_off" in changed_files:
            if changed_files <= {"effects_on", "effects_off"}:
                guess = "Effects setting"
        elif changed_files == {"solo_off"}:
            guess = "Solo switches setting"
        elif changed_files == {"guide_layers"}:
            guess = "Guide layers setting"
        
        print(f"{offset:<8} {base_val:02X}     {change_str:<60} {guess}")
    
    # Detailed analysis by setting category
    print(f"\n{'=' * 100}")
    print("DETAILED ANALYSIS BY SETTING CATEGORY")
    print("=" * 100)
    
    categories = {
        "Quality": ["quality_draft"],
        "Resolution": ["resolution_half"],
        "Field Render": ["field_lower", "field_upper"],
        "Frame Blending": ["frame_blend_curr", "frame_blend_off"],
        "Motion Blur": ["motion_blur_curr", "motion_blur_off"],
        "Frame Rate": ["framerate_24", "framerate_30"],
        "Time Span": ["time_length_comp"],
        "Proxy Use": ["proxy_all"],
        "Effects": ["effects_on", "effects_off"],
        "Solo Switches": ["solo_off"],
        "Guide Layers": ["guide_layers"],
    }
    
    for category, file_keys in categories.items():
        print(f"\n--- {category} ---")
        
        for key in file_keys:
            if key not in data or data[key] is None:
                print(f"  {key}: NOT AVAILABLE")
                continue
            
            ldat = data[key]
            if len(ldat) != len(base_data):
                print(f"  {key}: SIZE MISMATCH")
                continue
            
            diffs = []
            for i in range(len(base_data)):
                if ldat[i] != base_data[i]:
                    diffs.append((i, base_data[i], ldat[i]))
            
            print(f"  {key}:")
            if not diffs:
                print(f"    NO DIFFERENCES from base")
            else:
                for offset, base_val, new_val in diffs:
                    # Show context (4 bytes before and after)
                    context_before = base_data[max(0, offset-4):offset]
                    context_after = base_data[offset+1:min(len(base_data), offset+5)]
                    print(f"    Offset {offset}: {base_val:02X} -> {new_val:02X}")
                    print(f"      Context: [{context_before.hex(' ')}] [{base_val:02X}->{new_val:02X}] [{context_after.hex(' ')}]")
    
    # Hex dump of first 256 bytes with annotations
    print(f"\n{'=' * 100}")
    print("HEX DUMP OF BASE FILE (first 512 bytes)")
    print("=" * 100)
    
    for row in range(0, min(512, len(base_data)), 16):
        hex_part = " ".join(f"{base_data[row+i]:02X}" if row+i < len(base_data) else "  " for i in range(16))
        ascii_part = "".join(
            chr(base_data[row+i]) if row+i < len(base_data) and 32 <= base_data[row+i] < 127 else "."
            for i in range(16)
        )
        
        # Mark bytes that differ in any file
        markers = ""
        for i in range(16):
            if row + i in differences:
                markers += "*"
            else:
                markers += " "
        
        print(f"{row:04X}  {hex_part}  |{ascii_part}|  {markers}")
    
    # Check for patterns - look at potential struct boundaries
    print(f"\n{'=' * 100}")
    print("POTENTIAL INTEGER VALUES AT KEY OFFSETS")
    print("=" * 100)
    
    def read_u16_be(data: bytes, offset: int) -> int:
        return (data[offset] << 8) | data[offset + 1]
    
    def read_u32_be(data: bytes, offset: int) -> int:
        return (data[offset] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | data[offset + 3]
    
    def read_u16_le(data: bytes, offset: int) -> int:
        return data[offset] | (data[offset + 1] << 8)
    
    def read_u32_le(data: bytes, offset: int) -> int:
        return data[offset] | (data[offset + 1] << 8) | (data[offset + 2] << 16) | (data[offset + 3] << 24)
    
    # Check all offsets where differences occur
    print("\nValues at difference offsets:")
    for offset in sorted(differences.keys()):
        if offset + 4 <= len(base_data):
            u32_be = read_u32_be(base_data, offset)
            u32_le = read_u32_le(base_data, offset)
            print(f"  Offset {offset}: u32_be={u32_be} (0x{u32_be:08X}), u32_le={u32_le} (0x{u32_le:08X})")
    
    # Frame rate analysis
    print(f"\n{'=' * 100}")
    print("FRAME RATE VALUE ANALYSIS")
    print("=" * 100)
    
    for key in ["framerate_24", "framerate_30"]:
        if key in data and data[key]:
            print(f"\n{key}:")
            ldat = data[key]
            for offset in sorted(differences.keys()):
                if key in differences[offset]:
                    if offset + 8 <= len(ldat):
                        # Try reading as various numeric types
                        try:
                            f64_be = struct.unpack(">d", ldat[offset:offset+8])[0]
                            f64_le = struct.unpack("<d", ldat[offset:offset+8])[0]
                            f32_be = struct.unpack(">f", ldat[offset:offset+4])[0]
                            f32_le = struct.unpack("<f", ldat[offset:offset+4])[0]
                            print(f"  Offset {offset}:")
                            print(f"    f64_be={f64_be}, f64_le={f64_le}")
                            print(f"    f32_be={f32_be}, f32_le={f32_le}")
                        except:
                            pass

    # ==========================================================================
    # FINAL FIELD MAPPING SUMMARY
    # ==========================================================================
    print(f"\n{'=' * 100}")
    print("FIELD MAPPING SUMMARY")
    print("=" * 100)
    
    field_map = {
        45: ("u8", "Frame Rate (fps)", "Integer frame rate value"),
        51: ("u8", "Field Render", "0=Off, 1=Upper First, 2=Lower First"),
        57: ("u8", "Quality", "1=Draft, 2=Best"),
        59: ("u8", "Resolution X divisor", "1=Full, 2=Half, 3=Third, 4=Quarter"),
        61: ("u8", "Resolution Y divisor", "1=Full, 2=Half, 3=Third, 4=Quarter"),
        65: ("u8", "Effects", "0=All Off, 1=All On, 2=Current Settings"),
        69: ("u8", "Proxy Use", "0=Use No Proxies, 1=Use All Proxies, 2=Use Comp Proxies Only"),
        73: ("u8", "Motion Blur", "0=Off For All Layers, 1=Current Settings, 2=On For All Layers"),
        77: ("u8", "Frame Blending", "0=Off For All Layers, 1=Current Settings, 2=On For All Layers"),
        80: ("str", "Template Name", "Null-terminated ASCII string starting at offset 80"),
        2141: ("u8", "Custom Settings Flag?", "0=Template, 1=Custom"),
        2145: ("u8", "Use This Frame Rate", "0=Comp Frame Rate, 1=Use Custom Frame Rate"),
        2149: ("u8", "Time Span Source", "0=Length of Comp, 1=Work Area Only"),
        2165: ("u8", "Solo Switches", "0=All Off, 2=Current Settings"),
        2173: ("u8", "Guide Layers", "0=All Off, 2=Current Settings"),
    }
    
    print("\nDetermined field mappings from analysis:")
    print(f"{'Offset':<8} {'Type':<6} {'Field Name':<30} {'Values'}")
    print("-" * 100)
    for offset in sorted(field_map.keys()):
        dtype, name, values = field_map[offset]
        base_val = base_data[offset] if offset < len(base_data) else 0
        print(f"{offset:<8} {dtype:<6} {name:<30} Base={base_val:02X}  {values}")
    
    # Template name extraction
    print(f"\n--- Template Name at offset 80 ---")
    name_bytes = base_data[80:80+32]  # Read up to 32 bytes
    null_idx = name_bytes.find(b'\x00')
    if null_idx > 0:
        template_name = name_bytes[:null_idx].decode('ascii', errors='replace')
        print(f"  Template name: '{template_name}'")
    else:
        print(f"  Raw bytes: {name_bytes.hex(' ')}")
    
    # Print all files' values for key fields
    print(f"\n{'=' * 100}")
    print("ALL FILES - KEY FIELD VALUES")
    print("=" * 100)
    
    key_offsets = [45, 51, 57, 59, 61, 65, 69, 73, 77, 2141, 2145, 2149, 2165, 2173]
    
    # Header
    header = f"{'File':<20}"
    for off in key_offsets:
        header += f"{off:>6}"
    print(header)
    print("-" * (20 + 6 * len(key_offsets)))
    
    for name, ldat in data.items():
        if ldat is None:
            continue
        row = f"{name:<20}"
        for off in key_offsets:
            val = ldat[off] if off < len(ldat) else 0
            row += f"{val:>6X}"
        print(row)
    
    # Compare base vs custom
    print(f"\n{'=' * 100}")
    print("BASE vs CUSTOM COMPARISON")
    print("=" * 100)
    
    if "custom" in data and data["custom"]:
        custom_data = data["custom"]
        diffs = []
        for i in range(min(len(base_data), len(custom_data))):
            if base_data[i] != custom_data[i]:
                diffs.append((i, base_data[i], custom_data[i]))
        
        if diffs:
            print("Differences between base (Best Settings) and custom:")
            for offset, base_val, custom_val in diffs:
                print(f"  Offset {offset}: {base_val:02X} -> {custom_val:02X}")
        else:
            print("No differences found (base and custom are identical)")


if __name__ == "__main__":
    main()
