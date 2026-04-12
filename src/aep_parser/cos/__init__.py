"""COS (Carousel Object Syntax) parser and serializer."""

from .cos import CosParser, IndirectObject, IndirectReference, Stream
from .descriptors import CosField
from .serializer import serialize

__all__ = [
    "CosField",
    "CosParser",
    "IndirectObject",
    "IndirectReference",
    "Stream",
    "serialize",
]
