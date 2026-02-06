"""Analyze the detailed structure of the render queue ldat chunk."""

from __future__ import annotations

from aep_parser.kaitai.aep_optimized import Aep
from aep_parser.kaitai.utils import find_by_list_type, find_by_type


def get_lrdr_ldat(path: str) -> bytes:
    a = Aep.from_file(path)
    lrdr = find_by_list_type(a.data.chunks, "LRdr")
    lst = find_by_list_type(lrdr.chunks, "list")
    ldat = find_by_type(lst.chunks, "ldat")
    return ldat._raw_data


base = get_lrdr_ldat("samples/debug/render_queue_base.aep")

# Analyze first 100 bytes structure
print("STRUCTURE ANALYSIS - First 100 bytes")
print("=" * 80)
print()

# Header
print("Bytes 0-3 (magic/version?):", base[0:4].hex(" "))
print("Bytes 4-7:", base[4:8].hex(" "))
print("Bytes 8-11:", base[8:12].hex(" "))
print("Bytes 12-15:", base[12:16].hex(" "))
print()

# Looking at 4-byte boundaries
print("4-byte values (big-endian):")
for i in range(0, 80, 4):
    val = int.from_bytes(base[i : i + 4], "big")
    print(f"  Offset {i:3}: 0x{val:08X} = {val}")

print()
print("Template name area (80-112):")
print("  Raw:", base[80:112].hex(" "))
# Find the actual name
name_start = 90  # Based on hex dump, 'Best Settings' starts at 90
name_end = base.find(b"\x00", name_start)
if name_end > name_start:
    name = base[name_start:name_end].decode("ascii", errors="replace")
    print(f'  Name (starting at 90): "{name}"')
else:
    print("  Name: (no null terminator found)")

# Check end of chunk
print()
print("End of chunk (2140-2246):")
print("  Raw:", base[2140:].hex(" "))

# Print hex dump of all 2246 bytes with annotations
print()
print("=" * 80)
print("FULL HEX DUMP WITH ANNOTATIONS")
print("=" * 80)

annotations = {
    0: "--- Header ---",
    44: "--- Settings Block ---",
    45: "Frame Rate (30fps = 0x1E)",
    51: "Field Render (0=Off)",
    57: "Quality (2=Best)",
    59: "Resolution X (1=Full)",
    61: "Resolution Y (1=Full)",
    65: "Effects (2=Current)",
    69: "Proxy Use (0=None)",
    73: "Motion Blur (1=Current)",
    77: "Frame Blending (1=Current)",
    80: "--- Template Name Area ---",
    90: "'Best Settings' string",
    2140: "--- Footer/Flags ---",
    2141: "Custom Settings Flag",
    2145: "Use This Frame Rate Flag",
    2149: "Time Span Source",
    2165: "Solo Switches",
    2173: "Guide Layers",
}

for row in range(0, len(base), 16):
    # Check for annotations
    for offset in range(row, min(row + 16, len(base))):
        if offset in annotations:
            print(f"  [{offset:4}] {annotations[offset]}")

    hex_part = " ".join(
        f"{base[row+i]:02X}" if row + i < len(base) else "  " for i in range(16)
    )
    ascii_part = "".join(
        chr(base[row + i])
        if row + i < len(base) and 32 <= base[row + i] < 127
        else "."
        for i in range(16)
    )
    print(f"{row:04X}  {hex_part}  |{ascii_part}|")

# Summary
print()
print("=" * 80)
print("FIELD MAPPING SUMMARY")
print("=" * 80)
print(
    """
Offset 45:   Frame Rate (u8) - Integer fps value (e.g., 24=0x18, 30=0x1E)
Offset 51:   Field Render (u8) - 0=Off, 1=Upper First, 2=Lower First
Offset 57:   Quality (u8) - 1=Draft, 2=Best
Offset 59:   Resolution X divisor (u8) - 1=Full, 2=Half, 3=Third, 4=Quarter
Offset 61:   Resolution Y divisor (u8) - 1=Full, 2=Half, 3=Third, 4=Quarter
Offset 65:   Effects (u8) - 0=All Off, 1=All On, 2=Current Settings
Offset 69:   Proxy Use (u8) - 0=No Proxies, 1=All Proxies, 2=Comp Proxies Only
Offset 73:   Motion Blur (u8) - 0=Off All, 1=Current, 2=On All
Offset 77:   Frame Blending (u8) - 0=Off All, 1=Current, 2=On All
Offset 90:   Template Name (null-terminated ASCII string, ~32 bytes max)

Offset 2141: Custom Settings Flag (u8) - 0=Using Template, 1=Custom
Offset 2145: Use This Frame Rate Flag (u8) - 0=Use Comp Rate, 1=Use Custom Rate
Offset 2149: Time Span Source (u8) - 0=Length of Comp, 1=Work Area Only
Offset 2165: Solo Switches (u8) - 0=All Off, 2=Current Settings
Offset 2173: Guide Layers (u8) - 0=All Off, 2=Current Settings

Note: The render settings ldat is at path: LRdr > list > ldat (2246 bytes)
      There's also a render item ldat at: LRdr > LItm > list > ldat (128 bytes)
"""
)
