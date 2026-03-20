from __future__ import annotations

import json
import typing
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from typing import Any, cast

from kaitaistruct import KaitaiStream

from ..descriptors import ChunkField, ChunkInstanceField
from ..enums import (
    BitsPerChannel,
    ColorManagementSystem,
    FeetFramesFilmType,
    FootageTimecodeDisplayStartType,
    FramesCountType,
    GpuAccelType,
    LutInterpolationMethod,
    TimeDisplayType,
)
from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    str_contents,
    toggle_flag_chunk,
)
from ..validators import validate_one_of
from .items.composition import CompItem
from .items.folder import FolderItem
from .items.footage import FootageItem

if typing.TYPE_CHECKING:
    from aep_parser.kaitai import Aep  # type: ignore[attr-defined]

    from .items.item import Item
    from .layers.layer import Layer
    from .renderqueue.render_queue import RenderQueue


def _reverse_working_gamma(value: float, _body: Any) -> dict[str, int]:
    """Decompose working gamma into binary selector.

    AE stores a single selector byte: 0 → 2.2, nonzero → 2.4.
    """
    return {"working_gamma_selector": 0 if value == 2.2 else 1}


class Project:
    """
    The `Project` object represents an After Effects project. Attributes
    provide access to specific objects within the project, such as imported
    files or footage and compositions, and also to project settings such as the
    timecode base.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        project = app.project
        print(project.file)
        for item in project:
            ...
        ```

    See: https://ae-scripting.docsforadobe.dev/general/project/
    """

    # ---- Chunk-backed descriptors (nnhd) ----

    bits_per_channel = ChunkField[BitsPerChannel](
        "_nnhd",
        "bits_per_channel",
        transform=BitsPerChannel.from_binary,
        reverse=BitsPerChannel.to_binary,
    )
    """The color depth of the current project, either 8, 16, or 32 bits.
    Read / Write."""

    feet_frames_film_type = ChunkField[FeetFramesFilmType](
        "_nnhd",
        "feet_frames_film_type",
        transform=FeetFramesFilmType.from_binary,
        reverse=FeetFramesFilmType.to_binary,
    )
    """The film type for feet+frames timecode display, either MM16 (16mm) or
    MM35 (35mm). Read / Write."""

    footage_timecode_display_start_type = ChunkField[FootageTimecodeDisplayStartType](
        "_nnhd",
        "footage_timecode_display_start_type",
        transform=FootageTimecodeDisplayStartType.from_binary,
        reverse=FootageTimecodeDisplayStartType.to_binary,
    )
    """The Footage Start Time setting in the Project Settings dialog box,
    which is enabled when Timecode is selected as the time display style.
    Read / Write."""

    _frame_rate = ChunkField[float]("_nnhd", "frame_rate")
    """The frame rate of the project. Used as default value for new
    Compositions? Read-only."""

    frames_count_type = ChunkField[FramesCountType](
        "_nnhd",
        "frames_count_type",
        transform=FramesCountType.from_binary,
        reverse=FramesCountType.to_binary,
        invalidates=["display_start_frame"],
    )
    """The Frame Count menu setting in the Project Settings dialog box.
    Read / Write."""

    display_start_frame = ChunkInstanceField[int](
        "_nnhd",
        "display_start_frame",
        reverse=lambda value, _body: {"frames_count_type": value},
        validate=validate_one_of((0, 1)),
        invalidates=["display_start_frame"],
    )
    """The start frame number for the project display (0 or 1). An alternate
    way of setting the Frame Count menu setting. Read / Write."""

    frames_use_feet_frames = ChunkField[int](
        "_nnhd", "frames_use_feet_frames", reverse=int
    )
    """When True, the Frames field in the UI is displayed as feet+frames.
    Read / Write."""

    time_display_type = ChunkField[TimeDisplayType](
        "_nnhd",
        "time_display_type",
        transform=TimeDisplayType.from_binary,
        reverse=TimeDisplayType.to_binary,
    )
    """The time display style, corresponding to the Time Display Style
    section in the Project Settings dialog box. Read / Write."""

    transparency_grid_thumbnails = ChunkField[bool](
        "_nnhd", "transparency_grid_thumbnails", transform=bool, reverse=int
    )
    """When `True`, thumbnail views use the transparency checkerboard
    pattern. Read / Write."""

    # ---- Chunk-backed descriptors (head) ----

    revision = ChunkField[int]("_head", "file_revision", reverse=int)
    """The current revision of the project. Every user action increases the
    revision number by one. A new project starts at revision 1. Read / Write.

    Note:
        This attribute is read-only in ExtendScript.
    """

    # ---- Chunk-backed descriptors (acer) ----

    compensate_for_scene_referred_profiles = ChunkField[bool](
        "_acer", "compensate_for_scene_referred_profiles", transform=bool, reverse=int
    )
    """When True, After Effects compensates for scene-referred profiles when
    rendering."""

    # ---- Chunk-backed descriptors (adfr) ----

    audio_sample_rate = ChunkField[float](
        "_adfr",
        "audio_sample_rate",
        reverse=float,
    )
    """The project audio sample rate in Hz (e.g. 22050.0, 44100.0, 48000.0, 96000.0).

    Note:
        Not exposed in ExtendScript"""

    # ---- Chunk-backed descriptors (dwga) ----

    working_gamma = ChunkInstanceField[float](
        "_dwga",
        "working_gamma",
        reverse=_reverse_working_gamma,
        validate=validate_one_of((2.2, 2.4)),
        invalidates=["working_gamma"],
    )
    """The gamma value used for the working color space, typically 2.2 or 2.4.
    Read / Write."""

    # ---- Chunk-backed descriptor (aep root) ----

    xmp_packet = ChunkField[ET.Element](
        "_aep",
        "xmp_packet",
        transform=ET.fromstring,
        reverse=lambda el: ET.tostring(el, encoding="unicode"),
    )
    """The XMP packet for the project, containing metadata.
    Read / Write."""

    gpu_accel_type = ChunkField[Any](
        "_utf8",
        "contents",
        transform=lambda contents: GpuAccelType.from_binary(contents.split("\x00")[0]),
        reverse=GpuAccelType.to_binary,
    )
    """The GPU acceleration type for the project. None if not
    recognised. Read / Write."""

    # ---- Regular attributes set in __init__ ----

    file: str
    """The full path to the project file."""

    items: dict[int, Item]
    """All the items in the project."""

    render_queue: RenderQueue | None
    """The Render Queue of the project."""

    active_item: Item | None
    """
    The item that is currently active and is to be acted upon, or `None` if no
    item is currently selected or if multiple items are selected.
    """

    root_folder: FolderItem | None
    """
    The root folder. This is a virtual folder that contains all items in the
    Project panel, but not items contained inside other folders in the Project
    panel.
    """

    # ---- Computed properties ----

    @property
    def _root_chunks(self) -> list[Aep.Chunk]:
        chunks: list[Aep.Chunk] = self._aep.data.chunks
        return chunks

    @property
    def linear_blending(self) -> bool:
        """When True, linear blending is used for the project. When False,
        the standard blending mode is used. Read / Write."""
        return any(c.chunk_type == "lnrb" for c in self._root_chunks)

    @linear_blending.setter
    def linear_blending(self, value: bool) -> None:
        toggle_flag_chunk(self._aep, "lnrb", "LnrbBody", value)

    @property
    def linearize_working_space(self) -> bool:
        """When True, the working color space is linearized for blending
        operations. Read / Write."""
        return any(c.chunk_type == "lnrp" for c in self._root_chunks)

    @linearize_working_space.setter
    def linearize_working_space(self, value: bool) -> None:
        toggle_flag_chunk(self._aep, "lnrp", "LnrpBody", value)

    @property
    def expression_engine(self) -> str:
        """The Expressions Engine setting in the Project Settings dialog box
        ("extendscript" or "javascript-1.0")."""
        return _get_expression_engine(self._root_chunks)

    @property
    def effect_names(self) -> list[str]:
        """The names of all effects used in the project."""
        return _get_effect_names(self._root_chunks)

    @property
    def working_space(self) -> str:
        """The name of the working color space (e.g., "sRGB IEC61966-2.1",
        "None")."""
        return _get_working_space(self._root_chunks)

    @property
    def display_color_space(self) -> str:
        """The name of the display color space used for the project (e.g.,
        "ACES/sRGB"). Only relevant when color_management_system is OCIO.
        "None" when not set.

        Note:
            Not exposed in ExtendScript
        """
        return _get_display_color_space(self._root_chunks)

    @property
    def color_management_system(self) -> ColorManagementSystem:
        """The color management system used by the project (Adobe or OCIO).
        Available in CC 2024 and later."""
        settings = _get_color_profile_settings(self._root_chunks)
        return ColorManagementSystem(int(settings["colorManagementSystem"]))

    @property
    def lut_interpolation_method(self) -> LutInterpolationMethod:
        """The LUT interpolation method for the project (Trilinear or
        Tetrahedral)."""
        settings = _get_color_profile_settings(self._root_chunks)
        return LutInterpolationMethod(int(settings["lutInterpolationMethod"]))

    @property
    def ocio_configuration_file(self) -> str:
        """The OCIO configuration file for the project. Only relevant when
        color_management_system is OCIO."""
        settings = _get_color_profile_settings(self._root_chunks)
        return str(settings["ocioConfigurationFile"])

    @property
    def project_name(self) -> str:
        """The name of the project, derived from the file name."""
        return Path(self.file).name

    def __init__(
        self,
        *,
        _nnhd: Aep.NnhdBody,
        _head: Aep.HeadBody,
        _acer: Aep.AcerBody,
        _adfr: Aep.AdfrBody,
        _dwga: Aep.DwgaBody,
        _utf8: Aep.Utf8Body,
        _aep: Aep,
        file: str,
        items: dict[int, Item],
        render_queue: RenderQueue | None,
    ) -> None:
        # Chunk body references for descriptors
        self._nnhd = _nnhd
        self._head = _head
        self._acer = _acer
        self._adfr = _adfr
        self._dwga = _dwga
        self._utf8 = _utf8
        self._aep = _aep

        # Simple attributes
        self.file = file
        self.items = items
        self.render_queue = render_queue

        # Mutable defaults
        self.active_item: Item | None = None
        self.root_folder: FolderItem | None = None
        self._effect_param_defs: dict[str, dict[str, dict[str, Any]]] = {}
        self._layers_by_uid: dict[int, Layer] | None = None
        self._compositions: list[CompItem] | None = None
        self._folders: list[FolderItem] | None = None
        self._footages: list[FootageItem] | None = None

    def __repr__(self) -> str:
        return f"Project(file={self.file!r})"

    def __iter__(self) -> typing.Iterator[Item]:
        """Return an iterator over the project's items."""
        return iter(self.items.values())

    @property
    def num_items(self) -> int:
        """
        Return the number of items in the project.

        Note:
            Equivalent to `len(project.items)`
        """
        return len(self.items)

    def layer_by_id(self, layer_id: int) -> Layer:
        """Get a layer by its unique ID."""
        if self._layers_by_uid is None:
            self._layers_by_uid = {
                layer.id: layer for comp in self.compositions for layer in comp.layers
            }
        return self._layers_by_uid[layer_id]

    @property
    def compositions(self) -> list[CompItem]:
        """All the compositions in the project."""
        if self._compositions is None:
            self._compositions = [
                cast(CompItem, item)
                for item in self.items.values()
                if item.is_composition
            ]
        return self._compositions

    @property
    def folders(self) -> list[FolderItem]:
        """All the folders in the project."""
        if self._folders is None:
            self._folders = [
                cast(FolderItem, item) for item in self.items.values() if item.is_folder
            ]
        return self._folders

    @property
    def footages(self) -> list[FootageItem]:
        """All the footages in the project."""
        if self._footages is None:
            self._footages = [
                cast(FootageItem, item)
                for item in self.items.values()
                if item.is_footage
            ]
        return self._footages

    def save(self, path: Path) -> None:
        """
        Save the project to a new .aep file at the given path. As writing is
        still experimental, overwriting is not allowed for now.

        Warning:
            This is highly experimental for now.
        """
        if path.exists():
            raise FileExistsError(
                f"The file '{path}' already exists. As writing is still experimental, "
                "overwriting is not allowed for now. Please choose a different path or "
                "delete the existing file."
            )

        aep = self._aep

        xmp_bytes = aep.xmp_packet.encode("UTF-8")
        output_size = 8 + aep.len_data + len(xmp_bytes)
        buf = BytesIO(bytearray(output_size))

        with KaitaiStream(buf) as io:
            aep._write(io)
            result = buf.getvalue()

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(result)


# ---------------------------------------------------------------------------
# Private helpers – extract values from root chunks
# ---------------------------------------------------------------------------


def _get_expression_engine(root_chunks: list[Any]) -> str:
    """Get the expression engine used in the project."""
    try:
        exen_chunk = find_by_list_type(chunks=root_chunks, list_type="ExEn")
        utf8_chunk = find_by_type(chunks=exen_chunk.data.chunks, chunk_type="Utf8")
        return str_contents(utf8_chunk)
    except ChunkNotFoundError:
        return "extendscript"


def _get_effect_names(root_chunks: list[Any]) -> list[str]:
    """Get the list of effect names used in the project."""
    pefl_chunk = find_by_list_type(chunks=root_chunks, list_type="Pefl")
    pjef_chunks = filter_by_type(chunks=pefl_chunk.data.chunks, chunk_type="pjef")
    return [str_contents(chunk) for chunk in pjef_chunks]


def _get_color_profile_settings(root_chunks: list[Any]) -> dict[str, int | str]:
    """Get color profile settings (CMS, LUT interpolation, OCIO config)."""
    defaults: dict[str, int | str] = {
        "colorManagementSystem": 0,
        "lutInterpolationMethod": 0,
        "ocioConfigurationFile": "",
    }
    for chunk in filter_by_type(chunks=root_chunks, chunk_type="Utf8"):
        utf8_content = str_contents(chunk)
        if "lutInterpolationMethod" in utf8_content:
            cms_data = json.loads(utf8_content)
            return {**defaults, **cms_data}
    return defaults


def _get_working_space(root_chunks: list[Any]) -> str:
    """Get the working color space name from the project."""
    for chunk in filter_by_type(chunks=root_chunks, chunk_type="Utf8"):
        utf8_content = str_contents(chunk)
        if "baseColorProfile" in utf8_content:
            profile_data = json.loads(utf8_content)
            base_profile = profile_data.get("baseColorProfile", {})
            return str(base_profile.get("colorProfileName", "None"))
    if not any(c.chunk_type == "pcms" for c in root_chunks):
        return "sRGB IEC61966-2.1"
    return "None"


def _get_display_color_space(root_chunks: list[Any]) -> str:
    """Get the display color space name from the project."""
    found_working_space = False
    for chunk in filter_by_type(chunks=root_chunks, chunk_type="Utf8"):
        utf8_content = str_contents(chunk)
        if not found_working_space:
            if "baseColorProfile" in utf8_content:
                found_working_space = True
            continue
        if "baseColorProfile" in utf8_content:
            profile_data = json.loads(utf8_content)
            base_profile = profile_data.get("baseColorProfile", {})
            return str(base_profile.get("colorProfileName", "None"))
        return "None"
    return "None"
