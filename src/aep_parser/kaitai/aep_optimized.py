"""Optimized Aep class with dict-based chunk type lookup.

This module wraps the auto-generated aep.py and applies performance
optimizations without modifying the generated file. After regenerating
aep.py from aep.ksy, no manual changes are needed.

The optimization replaces the large if/elif chain in Chunk._read()
with a dict lookup for better performance.
"""

from __future__ import annotations

import ast
import inspect
import textwrap
from io import BytesIO

from kaitaistruct import KaitaiStream

# Import the generated Aep class
from .aep import Aep


def _get_string_value(node: ast.expr) -> str | None:
    """Extract a string value from an AST expression node.

    Handles ``ast.Constant`` (Python 3.8+) and the legacy ``ast.Str``
    (Python 3.7) transparently.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    # Python < 3.8 used ast.Str instead of ast.Constant
    if hasattr(ast, "Str") and isinstance(node, ast.Str):  # type: ignore[attr-defined]
        return node.s  # type: ignore[attr-defined]
    return None


def _extract_on_comparison(test: ast.expr) -> str | None:
    """Extract the string from an ``_on == "..."`` comparison node."""
    if not isinstance(test, ast.Compare):
        return None
    if len(test.ops) != 1 or not isinstance(test.ops[0], ast.Eq):
        return None
    if not (isinstance(test.left, ast.Name) and test.left.id == "_on"):
        return None
    if len(test.comparators) != 1:
        return None
    return _get_string_value(test.comparators[0])


def _extract_class_name(stmts: list[ast.stmt]) -> str | None:
    """Find ``self.data = Aep.ClassName(...)`` in a list of statements.

    Returns the *ClassName* portion, or ``None`` if no matching
    assignment is found.
    """
    for stmt in stmts:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
            continue
        target = stmt.targets[0]
        if not (
            isinstance(target, ast.Attribute)
            and target.attr == "data"
            and isinstance(target.value, ast.Name)
            and target.value.id == "self"
        ):
            continue
        if not isinstance(stmt.value, ast.Call):
            continue
        func = stmt.value.func
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "Aep"
        ):
            return func.attr
    return None


def _walk_if_chain(
    node: ast.If,
) -> tuple[dict[str, str], str | None]:
    """Walk an if/elif/else chain, yielding (chunk_type, class_name) pairs.

    Returns:
        Tuple of (mapping from chunk_type to class_name, fallback
        class_name from the ``else`` clause or ``None``).
    """
    mapping: dict[str, str] = {}
    fallback: str | None = None
    current: ast.If | None = node

    while current is not None:
        chunk_type = _extract_on_comparison(current.test)
        if chunk_type is not None:
            class_name = _extract_class_name(current.body)
            if class_name is not None:
                mapping[chunk_type] = class_name

        orelse = current.orelse
        if not orelse:
            current = None
        elif len(orelse) == 1 and isinstance(orelse[0], ast.If):
            current = orelse[0]  # elif
        else:
            # else clause
            fallback = _extract_class_name(orelse)
            current = None

    return mapping, fallback


def _build_chunk_type_mapping() -> tuple[dict[str, type], type]:
    """Build chunk type to class mapping by introspecting Chunk._read.

    Parses the AST of ``Chunk._read`` and walks the if/elif/else chain
    to extract (chunk_type, Aep subclass) pairs structurally -- no
    regular expressions involved.

    Returns:
        Tuple of (mapping dict, fallback class).

    Raises:
        RuntimeError: If the mapping cannot be built from the source.
    """
    try:
        source = textwrap.dedent(inspect.getsource(Aep.Chunk._read))
    except (OSError, TypeError) as exc:
        raise RuntimeError(
            "Cannot read source of Aep.Chunk._read for optimization"
        ) from exc

    tree = ast.parse(source)
    func_def = tree.body[0]
    if not isinstance(func_def, ast.FunctionDef):
        raise RuntimeError(
            "Expected a FunctionDef at top level of Chunk._read source"
        )

    # Find the if/elif chain that switches on _on
    if_node: ast.If | None = None
    for stmt in func_def.body:
        if isinstance(stmt, ast.If):
            if _extract_on_comparison(stmt.test) is not None:
                if_node = stmt
                break

    if if_node is None:
        raise RuntimeError(
            "Could not find the _on switch in Aep.Chunk._read"
        )

    name_mapping, fallback_name = _walk_if_chain(if_node)

    if not name_mapping:
        raise RuntimeError(
            "No chunk_type -> class mappings found in Aep.Chunk._read"
        )
    if fallback_name is None:
        raise RuntimeError(
            "No fallback (else) class found in Aep.Chunk._read"
        )

    # Resolve class name strings to actual Aep.* classes
    mapping: dict[str, type] = {}
    for chunk_type, class_name in name_mapping.items():
        cls = getattr(Aep, class_name, None)
        if cls is None:
            raise RuntimeError(
                f"Class Aep.{class_name} referenced in Chunk._read "
                "not found on Aep"
            )
        mapping[chunk_type] = cls

    fallback_class = getattr(Aep, fallback_name, None)
    if fallback_class is None:
        raise RuntimeError(
            f"Fallback class Aep.{fallback_name} not found on Aep"
        )

    return mapping, fallback_class


# Build the mapping and fallback dynamically from aep.py
_CHUNK_TYPE_TO_CLASS, _FALLBACK_CLASS = _build_chunk_type_mapping()


def _optimized_chunk_read(self: Aep.Chunk) -> None:
    """Optimized _read method for Chunk using dict lookup instead of if/elif."""
    self.chunk_type = (self._io.read_bytes(4)).decode("ascii")
    self.len_data = self._io.read_u4be()
    self._raw_data = self._io.read_bytes(
        (self._io.size() - self._io.pos())
        if self.len_data > (self._io.size() - self._io.pos())
        else self.len_data
    )
    _io__raw_data = KaitaiStream(BytesIO(self._raw_data))

    # Use dict lookup instead of if/elif chain
    try:
        chunk_class = _CHUNK_TYPE_TO_CLASS[self.chunk_type]
    except KeyError:
        chunk_class = _FALLBACK_CLASS
    self.data = chunk_class(_io__raw_data, self, self._root)

    if (self.len_data % 2) != 0:
        self.padding = self._io.read_bytes(1)


def _chunk_getattr(self: Aep.Chunk, name: str) -> object:
    """Delegate attribute access to chunk.data if not found on chunk itself.

    This allows writing ``chunk.list_type`` instead of
    ``chunk.data.list_type``.  ``__getattr__`` is only invoked after
    normal lookup has already failed, so ``self.data`` is safe to
    access directly (it is always set by ``_read``).
    """
    data = object.__getattribute__(self, "data")
    if data is not None and hasattr(data, name):
        return getattr(data, name)
    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


# Apply optimizations on import
Aep.Chunk._read = _optimized_chunk_read
Aep.Chunk.__getattr__ = _chunk_getattr

__all__ = ["Aep"]
