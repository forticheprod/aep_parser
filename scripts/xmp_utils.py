"""Utilities for stripping metadata from AEP project XMP packets.

Usage::

    python scripts/xmp_utils.py samples/models/composition/bgColor_custom.aep
    python scripts/xmp_utils.py file1.aep file2.aep file3.aep
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from py_aep import parse as parse_aep

NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xmp": "http://ns.adobe.com/xap/1.0/",
    "xmpMM": "http://ns.adobe.com/xap/1.0/mm/",
    "stEvt": "http://ns.adobe.com/xap/1.0/sType/ResourceEvent#",
    "dc": "http://purl.org/dc/elements/1.1/",
    "x": "adobe:ns:meta/",
}

# Register namespaces so ET.tostring preserves the original prefixes.
for _prefix, _uri in NS.items():
    ET.register_namespace(_prefix, _uri)

#: XMP child elements to remove from `rdf:Description`.
_ELEMENTS_TO_REMOVE = [
    "xmp:CreateDate",
    "xmp:MetadataDate",
    "xmp:ModifyDate",
    "xmp:CreatorTool",
    "xmpMM:InstanceID",
    "xmpMM:DocumentID",
    "xmpMM:OriginalDocumentID",
]

#: Attribute on `x:xmpmeta` to remove.
_XMPTK_ATTR = f"{{{NS['x']}}}xmptk"


def strip_xmp(xmp: ET.Element) -> ET.Element:
    """Strip dates, IDs, history, creator tool and xmptk from *xmp*.

    Modifies *xmp* **in-place** and returns it for convenience.

    * Empties `<xmpMM:History> / <rdf:Seq>` (removes all `<rdf:li>`).
    * Removes `xmp:CreateDate`, `xmp:MetadataDate`, `xmp:ModifyDate`,
      `xmpMM:InstanceID`, `xmpMM:DocumentID`,
      `xmpMM:OriginalDocumentID`, `xmp:CreatorTool`.
    * Removes the `x:xmptk` attribute from the root `<x:xmpmeta>` element.
    """
    # Remove x:xmptk attribute from root element.
    if _XMPTK_ATTR in xmp.attrib:
        del xmp.attrib[_XMPTK_ATTR]

    desc = xmp.find(".//rdf:Description", NS)
    if desc is None:
        return xmp

    # Empty History/Seq.
    history = desc.find("xmpMM:History", NS)
    if history is not None:
        seq = history.find("rdf:Seq", NS)
        if seq is not None:
            for li in list(seq):
                seq.remove(li)

    # Remove elements.
    for tag in _ELEMENTS_TO_REMOVE:
        el = desc.find(tag, NS)
        if el is not None:
            desc.remove(el)

    return xmp


def strip_xmp_and_save(aep_path: Path) -> None:
    """Parse *aep_path*, strip its XMP metadata and overwrite the file.

    The file is saved to a temporary path first, then the original is
    replaced atomically (rename) to minimise the risk of data loss.
    """
    aep_path = Path(aep_path).resolve()
    tmp_path = aep_path.with_suffix(".aep.tmp")

    app = parse_aep(aep_path)
    project = app.project

    # xmp_packet getter re-parses each time, so we must read, modify, write.
    project.xmp_packet = strip_xmp(project.xmp_packet)

    project.save(tmp_path)
    aep_path.unlink()
    tmp_path.rename(aep_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <file.aep> [file2.aep ...]")
        sys.exit(1)

    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.exists():
            print(f"File not found: {path}")
            continue
        print(f"Stripping XMP metadata from {path} ... ", end="", flush=True)
        strip_xmp_and_save(path)
        print("done.")
