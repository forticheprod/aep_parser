from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aep_parser.enums import (
        AudioCodec,
        MPEGAudioFormat,
        MPEGMultiplexer,
        MPEGMuxStreamCompatibility,
        VideoCodec,
    )


@dataclass
class XmlFormatOptions:
    """XML-based format-specific render options.

    Shared by output formats that store their settings as a binary header
    followed by a ``PremiereData`` XML block containing ``ExporterParam``
    elements. Applicable formats include AVI (``.AVI``), H.264 (``H264``),
    MP3 (``Mp3 ``), QuickTime (``MooV``), and WAV (``wao_``).

    Individual parameters are stored in the ``params`` dictionary, keyed by
    their Adobe parameter identifier (e.g. ``"ADBEVideoCodec"``).

    Example:
        ```python
        from aep_parser import XmlFormatOptions, parse

        app = parse("project.aep")
        om = app.project.render_queue.items[0].output_modules[0]
        if isinstance(om.format_options, XmlFormatOptions):
            print(om.format_options.video_codec)
        ```
    """

    format_code: str
    """
    The 4-character format identifier from the Ropt chunk header
    (e.g. ``".AVI"``, ``"H264"``, ``"Mp3 "``, ``"MooV"``, ``"wao_"``).
    """

    video_codec: VideoCodec | int | None
    """
    The video codec as a [VideoCodec][] FourCC integer value extracted from
    the ``ADBEVideoCodec`` parameter, or ``None`` for audio-only formats
    (MP3, WAV). Falls back to a plain ``int`` when the codec is not in the
    [VideoCodec][] enum.
    """

    audio_codec: AudioCodec | int | None
    """
    The audio codec as an [AudioCodec][] integer value extracted from the
    ``ADBEAudioCodec`` parameter, or ``None`` when the parameter is absent.
    Falls back to a plain ``int`` when the codec is not in the
    [AudioCodec][] enum.
    """

    frame_rate: float | None
    """
    The output frame rate in frames per second, derived from the
    ``ADBEVideoFPS`` parameter. Adobe stores this as ticks per frame using
    a time base of 254,016,000,000 ticks/second, so
    ``frame_rate = 254016000000 / ADBEVideoFPS``.
    ``None`` for audio-only formats (MP3, WAV).
    """

    mpeg_audio_format: MPEGAudioFormat | int | None = None
    """
    The MPEG audio format as an [MPEGAudioFormat][] FourCC integer value
    extracted from the ``ADBEMPEGAudioFormat`` parameter, or ``None`` when
    the parameter is absent. Falls back to a plain ``int`` when the value
    is not in the [MPEGAudioFormat][] enum.
    """

    mpeg_multiplexer: MPEGMultiplexer | int | None = None
    """
    The MPEG multiplexer as an [MPEGMultiplexer][] FourCC integer value
    extracted from the ``ADBEMPEGMultiplexer`` parameter, or ``None`` when
    the parameter is absent. Falls back to a plain ``int`` when the value
    is not in the [MPEGMultiplexer][] enum.
    """

    mpeg_mux_stream_compatibility: MPEGMuxStreamCompatibility | int | None = None
    """
    The MPEG mux stream compatibility as an
    [MPEGMuxStreamCompatibility][] FourCC integer value extracted from the
    ``ADBEMPEGMuxStreamCompatibility`` parameter, or ``None`` when the
    parameter is absent. Falls back to a plain ``int`` when the value is
    not in the [MPEGMuxStreamCompatibility][] enum.
    """

    params: dict[str, str] = field(default_factory=dict)
    """
    All ``ExporterParam`` key-value pairs extracted from the embedded XML
    ``PremiereData`` block. Keys are Adobe parameter identifiers such as
    ``"ADBEVideoCodec"``, ``"ADBEVideoQuality"``,
    ``"ADBEAudioInterleave"``, etc. Values are the raw string
    representations from the XML.
    """
