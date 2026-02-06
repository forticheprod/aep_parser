"""
Analyze output module settings in AEP render queue files.

This script compares output module chunks between files to identify
the binary format of output module settings like:
- Audio output (on/off, mono/stereo, bit depth, sample rate)
- Channels (RGB, Alpha)
- Color settings (straight/premultiplied)
- Preserve RGB
- Crop settings
- Resize settings
- Project link / XMP metadata

Output modules are stored in: LRdr/LItm/list/ldat and LRdr/LItm/LOm/Roou

FINDINGS:
=========
The output module settings are stored in three main chunks:

1. ldat chunk (128 bytes) in LIST 'list' - Output module flags:
   - Offset 11 (0x0b): Dirty flag (0=unchanged, 1=modified)
   - Offset 19 (0x13): Channels (0=RGB, 2=RGB+Alpha)
   - Offset 23 (0x17): Resize quality (1=high, 0=low)
   - Offset 27 (0x1b): Resize enabled (0=off, 1=on)
   - Offset 31 (0x1f): Crop enabled (0=off, 1=on)
   - Offset 47 (0x2f): Include Project Link (1=on, 0=off)
   - Offset 92 (0x5c): Base state flag (1=base, 0=modified)
   - Offset 94 (0x5e): Preserve RGB (0=off, 1=on)

2. Roou chunk (154 bytes) - Audio and color settings:
   - Offset 0-3: "FXTC" magic
   - Offset 4-7: Byte order indicator ("FXTC" or "CTXF")
   - Offset 26-29: Format code (e.g., "H264")
   - Offset 32-35: Width
   - Offset 36-39: Height
   - Offset 67 (0x43): Format/template indicator
   - Offset 77 (0x4d): Matted flag (1=matted/premultiplied, 0=unmatted/straight)
   - Offset 81 (0x51): Alpha interpretation (1=premultiplied, 0=straight)
   - Offset 100-107 (0x64-0x6b): Audio sample rate as IEEE 754 double (big-endian)
   - Offset 111 (0x6f): Audio bit depth (1=8-bit, 2=16-bit, 255=disabled)
   - Offset 113 (0x71): Audio channels (0=disabled, 1=mono, 2=stereo)

3. Ropt chunk (~34KB) - Contains embedded PremiereData XML with codec-specific settings:
   - Format header with "H264" and "NICKavc1" codec identifier
   - XML section with ADBEVideo* and ADBEAudio* parameters
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aep_parser.kaitai.aep_optimized import Aep
from aep_parser.kaitai.utils import find_by_list_type


def get_all_lom_chunks_detailed(filepath: str | Path) -> list[dict]:
    """Get detailed information about all chunks in LOm area."""
    aep = Aep.from_file(str(filepath))
    lrdr = find_by_list_type(chunks=aep.data.chunks, list_type="LRdr")
    litm = find_by_list_type(chunks=lrdr.data.chunks, list_type="LItm")
    
    chunks_info = []
    
    for chunk in litm.data.chunks:
        if chunk.chunk_type == "LIST" and hasattr(chunk.data, "list_type"):
            if chunk.data.list_type == "LOm ":
                for i, om_chunk in enumerate(chunk.data.chunks):
                    info = {
                        "index": i,
                        "type": om_chunk.chunk_type,
                        "size": len(om_chunk._raw_data) if hasattr(om_chunk, "_raw_data") else 0,
                    }
                    
                    if om_chunk.chunk_type == "LIST" and hasattr(om_chunk.data, "list_type"):
                        info["list_type"] = om_chunk.data.list_type
                        info["children"] = []
                        for j, nested in enumerate(om_chunk.data.chunks):
                            child_info = {
                                "index": j,
                                "type": nested.chunk_type,
                                "size": len(nested._raw_data) if hasattr(nested, "_raw_data") else 0,
                            }
                            info["children"].append(child_info)
                    
                    chunks_info.append(info)
    
    return chunks_info


def get_roou_chunk(filepath: str | Path) -> bytes | None:
    """Get the Roou (output options) chunk data."""
    aep = Aep.from_file(str(filepath))
    lrdr = find_by_list_type(chunks=aep.data.chunks, list_type="LRdr")
    litm = find_by_list_type(chunks=lrdr.data.chunks, list_type="LItm")

    for chunk in litm.data.chunks:
        if chunk.chunk_type == "LIST" and hasattr(chunk.data, "list_type"):
            if chunk.data.list_type == "LOm ":
                for om_chunk in chunk.data.chunks:
                    if om_chunk.chunk_type == "Roou":
                        return om_chunk._raw_data
    return None


def get_ldat_chunk(filepath: str | Path) -> bytes | None:
    """Get the ldat (list data) chunk from LIST 'list' area."""
    aep = Aep.from_file(str(filepath))
    lrdr = find_by_list_type(chunks=aep.data.chunks, list_type="LRdr")
    litm = find_by_list_type(chunks=lrdr.data.chunks, list_type="LItm")

    for chunk in litm.data.chunks:
        if chunk.chunk_type == "LIST" and hasattr(chunk.data, "list_type"):
            if chunk.data.list_type == "list":
                for sub_chunk in chunk.data.chunks:
                    if sub_chunk.chunk_type == "ldat":
                        return sub_chunk._raw_data
    return None


def get_ropt_chunk(filepath: str | Path) -> bytes | None:
    """Get the Ropt (render options) chunk data."""
    aep = Aep.from_file(str(filepath))
    lrdr = find_by_list_type(chunks=aep.data.chunks, list_type="LRdr")
    litm = find_by_list_type(chunks=lrdr.data.chunks, list_type="LItm")
    
    for chunk in litm.data.chunks:
        if chunk.chunk_type == "LIST" and hasattr(chunk.data, "list_type"):
            if chunk.data.list_type == "LOm ":
                for om_chunk in chunk.data.chunks:
                    if om_chunk.chunk_type == "Ropt":
                        return om_chunk._raw_data
    return None


def compare_bytes(base: bytes, other: bytes, max_diffs: int = 200) -> list[tuple[int, int | None, int | None]]:
    """Compare two byte sequences and return differences."""
    diffs = []
    max_len = max(len(base), len(other))
    
    for i in range(max_len):
        base_val = base[i] if i < len(base) else None
        other_val = other[i] if i < len(other) else None
        
        if base_val != other_val:
            diffs.append((i, base_val, other_val))
            if len(diffs) >= max_diffs:
                break
    
    return diffs


def hex_dump(data: bytes, start: int = 0, length: int = 64) -> str:
    """Create a hex dump of bytes."""
    lines = []
    for i in range(0, min(length, len(data) - start), 16):
        offset = start + i
        chunk = data[offset:offset + 16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{offset:04x}: {hex_part:<48} {ascii_part}")
    return "\n".join(lines)


def extract_xml_param(data: bytes, param_name: str) -> str | None:
    """Extract a parameter value from the XML in Ropt data.
    
    The Ropt XML uses <ParamIdentifier> tags instead of <identifier> tags.
    Values can be in ParamOrdinalValue or other param fields.
    """
    text = data.decode("latin-1", errors="ignore")
    
    # Look for ParamIdentifier structure used in Premiere/AE XML
    # Format: <ParamIdentifier>PARAM_NAME</ParamIdentifier>
    # followed by ParamOrdinalValue or ParamAuxValue
    pattern = rf'<ParamIdentifier>{param_name}</ParamIdentifier>.*?<Param(?:Ordinal|Aux)Value>([^<]+)</Param(?:Ordinal|Aux)Value>'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1)
    return None


def main():
    samples_dir = Path(__file__).parent.parent / "samples" / "debug"
    base_file = samples_dir / "render_queue_base.aep"
    
    files_to_compare = {
        "audio_output_on": samples_dir / "render_queue_output_module_audio_output_on.aep",
        "audio_output_off": samples_dir / "render_queue_output_module_audio_output_off.aep",
        "audio_mono": samples_dir / "render_queue_output_module_audio_mono.aep",
        "audio_8bit": samples_dir / "render_queue_output_module_audio_8bit.aep",
        "audio_16000hz": samples_dir / "render_queue_output_module_audio_16000hz.aep",
        "audio_44100hz": samples_dir / "render_queue_output_module_audio_44100hz.aep",
        "channels_alpha": samples_dir / "render_queue_output_module_channels_alpha.aep",
        "color_straight_unmatted": samples_dir / "render_queue_output_module_color_straight_unmatted.aep",
        "preserve_rgb": samples_dir / "render_queue_output_module_preserve_rgb.aep",
        "crop_checked": samples_dir / "render_queue_output_module_crop_checked.aep",
        "resize_checked": samples_dir / "render_queue_output_module_resize_checked.aep",
        "resize_quality_low": samples_dir / "render_queue_output_module_resize_quality_low.aep",
        "include_project_link_off": samples_dir / "render_queue_output_module_include_project_link_off.aep",
        "include_source_xmp_data_on": samples_dir / "render_queue_output_module_include_source_xmp_data_on.aep",
    }
    
    print("=" * 100)
    print("OUTPUT MODULE BINARY ANALYSIS")
    print("=" * 100)
    
    if not base_file.exists():
        print(f"ERROR: Base file not found: {base_file}")
        return
    
    # Show chunk structure
    print("\nCHUNK STRUCTURE (LOm area):")
    print("-" * 80)
    chunks_info = get_all_lom_chunks_detailed(base_file)
    for info in chunks_info:
        if "list_type" in info:
            print(f"  [{info['index']:2d}] LIST '{info['list_type']}' ({info['size']} bytes)")
            if "children" in info:
                for child in info["children"]:
                    print(f"        [{child['index']:2d}] {child['type']} ({child['size']} bytes)")
        else:
            print(f"  [{info['index']:2d}] {info['type']} ({info['size']} bytes)")
    
    # Collect all data
    base_roou = get_roou_chunk(base_file)
    base_ropt = get_ropt_chunk(base_file)
    base_ldat = get_ldat_chunk(base_file)

    all_roou = {"base": base_roou}
    all_ropt = {"base": base_ropt}
    all_ldat = {"base": base_ldat}
    for name, path in files_to_compare.items():
        if path.exists():
            all_roou[name] = get_roou_chunk(path)
            all_ropt[name] = get_ropt_chunk(path)
            all_ldat[name] = get_ldat_chunk(path)

    print(f"\nBase Roou size: {len(base_roou)} bytes")
    print(f"Base Ropt size: {len(base_ropt)} bytes")
    print(f"Base ldat size: {len(base_ldat)} bytes")
    
    # Show base Roou hex dump
    print("\nBASE Roou HEX DUMP:")
    print("-" * 80)
    print(hex_dump(base_roou, 0, len(base_roou)))
    
    # Compare Roou chunks
    print("\n" + "=" * 100)
    print("ROOU DIFFERENCES (excluding byte order at offset 4-7)")
    print("=" * 100)
    
    offset_changes: dict[int, list[tuple[str, int | None, int | None]]] = {}
    
    for name, other_roou in all_roou.items():
        if name == "base" or other_roou is None:
            continue
        
        diffs = compare_bytes(base_roou, other_roou)
        meaningful_diffs = [(o, b, v) for o, b, v in diffs if o not in (4, 5, 6, 7)]
        
        if meaningful_diffs:
            print(f"\n{name}:")
            for offset, bv, ov in meaningful_diffs:
                context = ""
                if 100 <= offset <= 107:
                    context = " <- audio sample rate (double)"
                elif offset == 111:
                    context = " <- audio bit depth (1=8bit, 2=16bit)"
                elif offset == 113:
                    context = " <- audio channels (0=off, 1=mono, 2=stereo)"
                elif offset == 77:
                    context = " <- matted (1=yes, 0=no)"
                elif offset == 81:
                    context = " <- alpha (1=premul, 0=straight)"
                elif offset == 67:
                    context = " <- format indicator"
                
                print(f"  offset {offset:3d} (0x{offset:02x}): {bv:3d} -> {ov:3d}{context}")
                
                if offset not in offset_changes:
                    offset_changes[offset] = []
                offset_changes[offset].append((name, bv, ov))
    
    # Analyze patterns
    print("\n" + "=" * 100)
    print("ANALYSIS BY SETTING TYPE")
    print("=" * 100)
    
    # Audio settings
    print("\nAUDIO SETTINGS (Roou):")
    print("-" * 80)
    
    print("\n  Sample Rate (offset 100-107, IEEE 754 double big-endian):")
    for name in ["base", "audio_16000hz", "audio_44100hz", "audio_output_off"]:
        if name in all_roou and all_roou[name]:
            roou = all_roou[name]
            raw = roou[100:108]  # 8 bytes for double
            rate = struct.unpack(">d", raw)[0]
            print(f"    {name:25s}: {raw.hex()} = {rate:.0f} Hz")
    
    print("\n  Channels (offset 113): 0=off, 1=mono, 2=stereo")
    for name in ["base", "audio_mono", "audio_output_off"]:
        if name in all_roou and all_roou[name]:
            print(f"    {name:25s}: {all_roou[name][113]}")
    
    print("\n  Bit Depth (offset 111): 1=8-bit, 2=16-bit, 255=disabled")
    for name in ["base", "audio_8bit", "audio_output_off"]:
        if name in all_roou and all_roou[name]:
            print(f"    {name:25s}: {all_roou[name][111]}")
    
    # Color settings
    print("\nCOLOR SETTINGS (Roou):")
    print("-" * 80)
    
    print("\n  Matted flag (offset 77): 1=matted/premultiplied, 0=unmatted/straight")
    print("  Alpha interpretation (offset 81): 1=premultiplied, 0=straight")
    for name in ["base", "color_straight_unmatted", "preserve_rgb"]:
        if name in all_roou and all_roou[name]:
            roou = all_roou[name]
            print(f"    {name:25s}: matted={roou[77]}, alpha={roou[81]}")
    
    # Ropt XML analysis
    print("\n" + "=" * 100)
    print("ROPT XML ANALYSIS")
    print("=" * 100)
    
    params = [
        "ADBEVideoChannels",          # Not used - it's ADBEVideoCodec
        "ADBEAudioRatePerSecond",     # Audio sample rate
        "ADBEAudioNumChannels",       # Audio channel count
        "ADBEAudioSampleType",        # Audio bit depth/sample type
        "ADBEVideoWidth",             # Video width
        "ADBEVideoHeight",            # Video height
        "ADBEVideoCodec",             # Video codec
        "ADBEAudioCodec",             # Audio codec
    ]
    
    for param in params:
        print(f"\n  {param}:")
        for name in ["base", "channels_alpha", "audio_16000hz", "audio_44100hz", "audio_mono", "audio_8bit"]:
            if name in all_ropt and all_ropt[name]:
                val = extract_xml_param(all_ropt[name], param)
                if val:
                    print(f"    {name:25s}: {val}")
    
    # Look for crop/resize in XML
    print("\n\nCROP/RESIZE SEARCH (in Ropt XML):")
    print("-" * 80)
    
    for name in ["base", "crop_checked", "resize_checked", "resize_quality_low"]:
        if name in all_ropt and all_ropt[name]:
            text = all_ropt[name].decode("latin-1", errors="ignore")
            
            crop_match = re.search(r'<identifier>([^<]*crop[^<]*)</identifier>.*?<value[^>]*>([^<]+)</value>', 
                                   text, re.IGNORECASE | re.DOTALL)
            resize_match = re.search(r'<identifier>([^<]*resize[^<]*)</identifier>.*?<value[^>]*>([^<]+)</value>',
                                     text, re.IGNORECASE | re.DOTALL)
            scale_match = re.search(r'<identifier>([^<]*scale[^<]*)</identifier>.*?<value[^>]*>([^<]+)</value>',
                                    text, re.IGNORECASE | re.DOTALL)
            
            if crop_match or resize_match or scale_match:
                print(f"\n  {name}:")
                if crop_match:
                    print(f"    {crop_match.group(1)}: {crop_match.group(2)}")
                if resize_match:
                    print(f"    {resize_match.group(1)}: {resize_match.group(2)}")
                if scale_match:
                    print(f"    {scale_match.group(1)}: {scale_match.group(2)}")
    
    # Project link / XMP
    print("\n\nPROJECT LINK / XMP SEARCH (in Ropt XML):")
    print("-" * 80)
    
    for name in ["base", "include_project_link_off", "include_source_xmp_data_on"]:
        if name in all_ropt and all_ropt[name]:
            text = all_ropt[name].decode("latin-1", errors="ignore")
            
            link_match = re.search(r'<identifier>([^<]*link[^<]*)</identifier>.*?<value[^>]*>([^<]+)</value>',
                                   text, re.IGNORECASE | re.DOTALL)
            xmp_match = re.search(r'<identifier>([^<]*xmp[^<]*)</identifier>.*?<value[^>]*>([^<]+)</value>',
                                  text, re.IGNORECASE | re.DOTALL)
            embed_match = re.search(r'<identifier>([^<]*embed[^<]*)</identifier>.*?<value[^>]*>([^<]+)</value>',
                                    text, re.IGNORECASE | re.DOTALL)
            
            matches = [m for m in [link_match, xmp_match, embed_match] if m]
            if matches:
                print(f"\n  {name}:")
                for m in matches:
                    print(f"    {m.group(1)}: {m.group(2)}")
    
    # Summary
    print("\n" + "=" * 100)
    print("SUMMARY - DISCOVERED OFFSETS")
    print("=" * 100)
    print("""
Roou chunk (154 bytes):
  Offset   0-3:  Magic "FXTC"
  Offset   4-7:  Byte order ("FXTC" or "CTXF") - changes between saves
  Offset  26-29: Format code (e.g., "H264")
  Offset  67:    Format/template indicator (changes when settings modified)
  Offset  77:    Matted flag (1=matted/premultiplied, 0=unmatted/straight)
  Offset  81:    Alpha interpretation (1=premultiplied, 0=straight)
  Offset 100-107: Audio sample rate as IEEE 754 double (big-endian)
                  48000 Hz = 0x40e7700000000000
                  44100 Hz = 0x40e5888000000000
                  16000 Hz = 0x40cf400000000000
                     -1 Hz = 0xbff0000000000000 (disabled)
  Offset 111:    Audio bit depth (1=8-bit, 2=16-bit, 255=disabled)
  Offset 113:    Audio channels (0=disabled, 1=mono, 2=stereo)

Ropt chunk (~34KB):
  Contains embedded PremiereData XML with codec-specific settings
  Structure: <ParamIdentifier>PARAM_NAME</ParamIdentifier>
             <ParamOrdinalValue>VALUE</ParamOrdinalValue>
  Parameters include ADBEVideoChannels, ADBEAudioRatePerSecond, etc.
  Crop, resize, project link, and XMP settings in XML format
""")


if __name__ == "__main__":
    main()
