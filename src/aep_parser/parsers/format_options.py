"""Parsers for format-specific render options (Ropt chunk)."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from typing import Any, Union

from ..enums import (
    AudioCodec,
    CineonFileFormat,
    Hdr10ColorPrimaries,
    JpegFormatType,
    MPEGAudioFormat,
    MPEGMultiplexer,
    MPEGMuxStreamCompatibility,
    OpenExrCompression,
    PngCompression,
    VideoCodec,
)
from ..kaitai import Aep
from ..kaitai.utils import filter_by_type, str_contents
from ..models.renderqueue.format_options import (
    CineonFormatOptions,
    JpegFormatOptions,
    OpenExrFormatOptions,
    PngFormatOptions,
    TargaFormatOptions,
    TiffFormatOptions,
    XmlFormatOptions,
)

FormatOptions = Union[
    CineonFormatOptions,
    JpegFormatOptions,
    OpenExrFormatOptions,
    PngFormatOptions,
    TargaFormatOptions,
    TiffFormatOptions,
    XmlFormatOptions,
]

# Format codes that use XML-based PremiereData options
_XML_FORMAT_CODES = {".AVI", "H264", "Mp3 ", "MooV", "wao_"}


def _parse_exporter_params(xml_text: str) -> dict[str, str]:
    """Extract parameter key-value pairs from PremiereData XML.

    Parses ``ExporterParam`` elements regardless of child-tag order and
    returns a mapping of identifier to value. Container groups (numeric
    identifiers) are skipped.

    Args:
        xml_text: The decoded XML string.

    Returns:
        Dictionary mapping parameter identifiers to their string values.
    """
    params: dict[str, str] = {}
    root = ET.fromstring(xml_text)
    for elem in root.iter("ExporterParam"):
        id_elem = elem.find("ParamIdentifier")
        val_elem = elem.find("ParamValue")
        if id_elem is None or id_elem.text is None:
            continue
        if val_elem is None:
            continue
        identifier = id_elem.text
        if identifier.isdigit():
            continue
        params[identifier] = val_elem.text or ""
    return params


def _parse_jpeg_format_options(
    body: Aep.JpegRoptData,
) -> JpegFormatOptions:
    """Parse JPEG format options from the typed Ropt body.

    Args:
        body: The Kaitai-parsed JPEG Ropt data.

    Returns:
        Populated [JpegFormatOptions][].
    """
    # Scans are encoded as an index: binary 1 = 3 scans, 2 = 4 scans, 3 = 5 scans.
    actual_scans = body.scans + 2
    return JpegFormatOptions(
        quality=body.quality,
        format_type=JpegFormatType(body.format_type),
        scans=actual_scans,
    )


def _parse_cineon_format_options(
    body: Aep.CineonRoptData,
) -> CineonFormatOptions:
    """Parse Cineon/DPX format options from a parsed Ropt body.

    Args:
        body: The Kaitai-parsed Cineon Ropt data.

    Returns:
        Populated CineonFormatOptions.
    """
    return CineonFormatOptions(
        ten_bit_black_point=body.ten_bit_black_point,
        ten_bit_white_point=body.ten_bit_white_point,
        converted_black_point=body.converted_black_point,
        converted_white_point=body.converted_white_point,
        current_gamma=body.current_gamma,
        highlight_expansion=body.highlight_expansion,
        logarithmic_conversion=body.logarithmic_conversion != 0,
        file_format=CineonFileFormat(body.file_format),
        bit_depth=body.bit_depth,
    )


def _parse_xml_format_options(
    format_code: str,
    body: Aep.RoptGenericData,
) -> XmlFormatOptions:
    """Parse XML-based format options from a generic Ropt body.

    The raw bytes contain a short binary header followed by XML
    ``PremiereData`` with ``ExporterParam`` elements. Shared by AVI,
    H.264, MP3, QuickTime, and WAV formats.

    Args:
        format_code: The 4-character format identifier.
        body: The Kaitai-parsed generic Ropt data (raw bytes after the
            4-byte format code).

    Returns:
        Populated [XmlFormatOptions][].
    """
    raw = bytes(body.raw)
    params: dict[str, str] = {}

    # Find the XML portion (starts with "<?xml")
    xml_start = raw.find(b"<?xml")
    if xml_start >= 0:
        xml_bytes = raw[xml_start:]
        # Decode as UTF-8 and strip trailing null bytes
        xml_text = xml_bytes.decode("utf-8", errors="replace").rstrip("\x00")
        params = _parse_exporter_params(xml_text)

    video_codec: VideoCodec | int | None = None
    codec_str = params.get("ADBEVideoCodec", "")
    if codec_str:
        try:
            raw_value = int(codec_str)
            try:
                video_codec = VideoCodec(raw_value)
            except ValueError:
                video_codec = raw_value
        except ValueError:
            pass

    audio_codec: AudioCodec | int | None = None
    audio_str = params.get("ADBEAudioCodec", "")
    if audio_str:
        try:
            raw_value = int(audio_str)
            try:
                audio_codec = AudioCodec(raw_value)
            except ValueError:
                audio_codec = raw_value
        except ValueError:
            pass

    # Adobe stores FPS as ticks-per-frame with a 254016000000 tick base.
    _ADOBE_TICKS_PER_SECOND = 254016000000
    frame_rate: float | None = None
    fps_str = params.get("ADBEVideoFPS", "")
    if fps_str:
        try:
            ticks = int(fps_str)
            if ticks > 0:
                frame_rate = _ADOBE_TICKS_PER_SECOND / ticks
        except ValueError:
            pass

    mpeg_audio_format: MPEGAudioFormat | int | None = None
    maf_str = params.get("ADBEMPEGAudioFormat", "")
    if maf_str:
        try:
            raw_value = int(maf_str)
            try:
                mpeg_audio_format = MPEGAudioFormat(raw_value)
            except ValueError:
                mpeg_audio_format = raw_value
        except ValueError:
            pass

    mpeg_multiplexer: MPEGMultiplexer | int | None = None
    mux_str = params.get("ADBEMPEGMultiplexer", "")
    if mux_str:
        try:
            raw_value = int(mux_str)
            try:
                mpeg_multiplexer = MPEGMultiplexer(raw_value)
            except ValueError:
                mpeg_multiplexer = raw_value
        except ValueError:
            pass

    mpeg_mux_compat: MPEGMuxStreamCompatibility | int | None = None
    msc_str = params.get("ADBEMPEGMuxStreamCompatibility", "")
    if msc_str:
        try:
            raw_value = int(msc_str)
            try:
                mpeg_mux_compat = MPEGMuxStreamCompatibility(raw_value)
            except ValueError:
                mpeg_mux_compat = raw_value
        except ValueError:
            pass

    return XmlFormatOptions(
        format_code=format_code,
        video_codec=video_codec,
        audio_codec=audio_codec,
        frame_rate=frame_rate,
        mpeg_audio_format=mpeg_audio_format,
        mpeg_multiplexer=mpeg_multiplexer,
        mpeg_mux_stream_compatibility=mpeg_mux_compat,
        params=params,
    )


def _parse_targa_format_options(
    body: Aep.TargaRoptData,
) -> TargaFormatOptions:
    """Parse Targa format options from the typed Ropt body.

    Args:
        body: The Kaitai-parsed Targa Ropt data.

    Returns:
        Populated [TargaFormatOptions][].
    """
    return TargaFormatOptions(
        bits_per_pixel=body.bits_per_pixel,
        rle_compression=body.rle_compression != 0,
    )


def _parse_openexr_format_options(
    body: Aep.OpenexrRoptData,
) -> OpenExrFormatOptions:
    """Parse OpenEXR format options from the typed Ropt body.

    Args:
        body: The Kaitai-parsed OpenEXR Ropt data.

    Returns:
        Populated [OpenExrFormatOptions][].
    """
    compression = OpenExrCompression(body.compression)
    dwa_level: float | None = None
    if compression in (OpenExrCompression.DWAA, OpenExrCompression.DWAB):
        dwa_level = body.dwa_compression_level
    return OpenExrFormatOptions(
        compression=compression,
        luminance_chroma=body.luminance_chroma != 0,
        thirty_two_bit_float=body.thirty_two_bit_float != 0,
        dwa_compression_level=dwa_level,
    )


def _parse_png_hdr10_json(utf8_json: str) -> dict[str, Any]:
    """Parse HDR10 metadata from the Utf8 JSON chunk.

    Parses the JSON string stored in the first ``Utf8`` chunk of the
    output module, which holds HDR10/color-metadata settings for PNG
    exports. Returns an empty dict when the JSON is empty or invalid.

    Args:
        utf8_json: The raw JSON string from the first Utf8 chunk.

    Returns:
        Parsed dict with any of the following keys:
        ``colorMetadataPresent``, ``displayPrimaries``,
        ``minLuminance``, ``maxLuminance``,
        ``maxContentLightLevel``, ``maxFrameAverageLightLevel``.
    """
    try:
        result = json.loads(utf8_json)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, ValueError):
        pass
    return {}


def _parse_png_format_options(
    body: Aep.PngRoptData,
    hdr10_json: str,
) -> PngFormatOptions:
    """Parse PNG format options from the typed Ropt body and HDR10 JSON.

    Args:
        body: The Kaitai-parsed PNG Ropt data with width, height, and
            bit depth fields.
        hdr10_json: JSON string from the first ``Utf8`` chunk in the
            output module, containing HDR10 metadata settings.

    Returns:
        Populated [PngFormatOptions][].
    """
    meta = _parse_png_hdr10_json(hdr10_json)

    include_hdr10 = bool(meta.get("colorMetadataPresent", False))

    # displayPrimaries: 0=Rec.709, absent=P3 D65 (default=1), 2=Rec.2020
    raw_primaries = meta.get("displayPrimaries")
    if raw_primaries is None:
        color_primaries = Hdr10ColorPrimaries.P3_D65
    else:
        color_primaries = Hdr10ColorPrimaries(int(raw_primaries))

    lum_min_raw = meta.get("minLuminance")
    lum_max_raw = meta.get("maxLuminance")
    cl_max_raw = meta.get("maxContentLightLevel")
    cl_avg_raw = meta.get("maxFrameAverageLightLevel")

    return PngFormatOptions(
        width=body.width,
        height=body.height,
        bit_depth=body.bit_depth,
        compression=PngCompression(body.compression),
        include_hdr10_metadata=include_hdr10,
        color_primaries=color_primaries,
        luminance_min=float(lum_min_raw) if lum_min_raw is not None else None,
        luminance_max=float(lum_max_raw) if lum_max_raw is not None else None,
        content_light_max=float(cl_max_raw) if cl_max_raw is not None else None,
        content_light_average=float(cl_avg_raw) if cl_avg_raw is not None else None,
    )


def _parse_tiff_format_options(
    body: Aep.TiffRoptData,
) -> TiffFormatOptions:
    """Parse TIFF format options from the typed Ropt body.

    Args:
        body: The Kaitai-parsed TIFF Ropt data.

    Returns:
        Populated [TiffFormatOptions][].
    """
    return TiffFormatOptions(
        lzw_compression=body.lzw_compression != 0,
        ibm_pc_byte_order=body.ibm_pc_byte_order != 0,
    )


def parse_format_options(
    chunks: list[Aep.Chunk],
) -> FormatOptions | None:
    """Parse format-specific options from the Ropt chunk, if present.

    Args:
        chunks: List of chunks belonging to an output module.

    Returns:
        A format-specific options object, or ``None`` when the Ropt chunk
        is absent or the format is not yet supported.
    """
    ropt_chunks = filter_by_type(chunks=chunks, chunk_type="Ropt")
    if not ropt_chunks:
        return None

    ropt_chunk = ropt_chunks[0]
    format_code = ropt_chunk.format_code

    if format_code == "sDPX":
        return _parse_cineon_format_options(ropt_chunk.body)
    if format_code == "JPEG":
        return _parse_jpeg_format_options(ropt_chunk.body)
    if format_code == "TPIC":
        return _parse_targa_format_options(ropt_chunk.body)
    if format_code == "TIF ":
        return _parse_tiff_format_options(ropt_chunk.body)
    if format_code == "oEXR":
        return _parse_openexr_format_options(ropt_chunk.body)
    if format_code == "png!":
        # Utf8[0] is a JSON chunk containing HDR10 metadata settings.
        utf8_chunks = filter_by_type(chunks=chunks, chunk_type="Utf8")
        hdr10_json = str_contents(utf8_chunks[0]) if utf8_chunks else "{}"
        return _parse_png_format_options(ropt_chunk.body, hdr10_json)
    if format_code in _XML_FORMAT_CODES:
        return _parse_xml_format_options(format_code, ropt_chunk.body)

    return None
