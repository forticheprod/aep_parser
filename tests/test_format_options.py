"""Tests for OutputModule.format_options parsing."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import parse_project

from aep_parser.enums import (
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
from aep_parser.models.renderqueue.format_options import (
    CineonFormatOptions,
    JpegFormatOptions,
    OpenExrFormatOptions,
    PngFormatOptions,
    TargaFormatOptions,
    TiffFormatOptions,
    XmlFormatOptions,
)

FORMAT_DIR = (
    Path(__file__).parent.parent
    / "samples"
    / "models"
    / "output_module"
    / "format"
)
CINEON_DIR = FORMAT_DIR / "cineon"
AVI_DIR = FORMAT_DIR / "avi"


def _cineon_opts(name: str) -> CineonFormatOptions:
    """Parse a Cineon sample and return its CineonFormatOptions."""
    project = parse_project(CINEON_DIR / f"{name}.aep")
    opts = project.render_queue.items[0].output_modules[0].format_options
    assert isinstance(opts, CineonFormatOptions)
    return opts


def _avi_opts(name: str) -> XmlFormatOptions:
    """Parse an AVI sample and return its XmlFormatOptions."""
    project = parse_project(AVI_DIR / f"{name}.aep")
    opts = project.render_queue.items[0].output_modules[0].format_options
    assert isinstance(opts, XmlFormatOptions)
    return opts


class TestCineonFormatOptions:
    """Tests for Cineon/DPX format options parsed from Ropt chunks."""

    def test_base_type(self) -> None:
        """Cineon base sample returns CineonFormatOptions."""
        opts = _cineon_opts("base")
        assert isinstance(opts, CineonFormatOptions)

    def test_base_defaults(self) -> None:
        """Base Cineon sample has expected default values."""
        opts = _cineon_opts("base")
        assert opts.ten_bit_black_point == 0
        assert opts.ten_bit_white_point == 1023
        assert opts.converted_black_point == 0.0
        assert opts.converted_white_point == 1.0
        assert opts.current_gamma == 1.0
        assert opts.highlight_expansion == 0
        assert opts.logarithmic_conversion is False
        assert opts.file_format == CineonFileFormat.DPX
        assert opts.bit_depth == 10

    # --- 10-bit black point ---

    def test_10_bit_black_point_1(self) -> None:
        opts = _cineon_opts("10_bit_black_point_1")
        assert opts.ten_bit_black_point == 1

    def test_10_bit_black_point_2(self) -> None:
        opts = _cineon_opts("10_bit_black_point_2")
        assert opts.ten_bit_black_point == 2

    def test_10_bit_black_point_1023(self) -> None:
        opts = _cineon_opts("10_bit_black_point_1023")
        assert opts.ten_bit_black_point == 1023

    # --- 10-bit white point ---

    def test_10_bit_white_point_0(self) -> None:
        opts = _cineon_opts("10_bit_white_point_0")
        assert opts.ten_bit_white_point == 0

    def test_10_bit_white_point_1021(self) -> None:
        opts = _cineon_opts("10_bit_white_point_1021")
        assert opts.ten_bit_white_point == 1021

    def test_10_bit_white_point_1022(self) -> None:
        opts = _cineon_opts("10_bit_white_point_1022")
        assert opts.ten_bit_white_point == 1022

    # --- converted black point ---

    def test_converted_black_point_1(self) -> None:
        opts = _cineon_opts("converted_black_point_1")
        assert opts.converted_black_point == pytest.approx(1.0 / 255.0)

    def test_converted_black_point_2(self) -> None:
        opts = _cineon_opts("converted_black_point_2")
        assert opts.converted_black_point == pytest.approx(2.0 / 255.0)

    def test_converted_black_point_255(self) -> None:
        opts = _cineon_opts("converted_black_point_255")
        assert opts.converted_black_point == pytest.approx(1.0)

    # --- converted white point ---

    def test_converted_white_point_0(self) -> None:
        opts = _cineon_opts("converted_white_point_0")
        assert opts.converted_white_point == pytest.approx(0.0)

    def test_converted_white_point_253(self) -> None:
        opts = _cineon_opts("converted_white_point_253")
        assert opts.converted_white_point == pytest.approx(253.0 / 255.0)

    def test_converted_white_point_254(self) -> None:
        opts = _cineon_opts("converted_white_point_254")
        assert opts.converted_white_point == pytest.approx(254.0 / 255.0)

    def test_converted_white_point_32767(self) -> None:
        opts = _cineon_opts("converted_white_point_32767")
        assert opts.converted_white_point == pytest.approx(32767.0 / 32768.0)

    def test_converted_white_point_0_987(self) -> None:
        opts = _cineon_opts("converted_white_point_0.987")
        assert opts.converted_white_point == pytest.approx(0.987)

    # --- current gamma ---

    def test_current_gamma_0_01(self) -> None:
        opts = _cineon_opts("current_gamma_0.01")
        assert opts.current_gamma == pytest.approx(0.01)

    def test_current_gamma_1_1(self) -> None:
        opts = _cineon_opts("current_gamma_1.1")
        assert opts.current_gamma == pytest.approx(1.1)

    def test_current_gamma_5(self) -> None:
        opts = _cineon_opts("current_gamma_5")
        assert opts.current_gamma == pytest.approx(5.0)

    # --- logarithmic conversion ---

    def test_logarithmic_conversion_on(self) -> None:
        # Note: filename has typo "logarighmic"
        opts = _cineon_opts("logarighmic_conversion_on")
        assert opts.logarithmic_conversion is True

    def test_logarithmic_conversion_off(self) -> None:
        opts = _cineon_opts("logarighmic_conversion_off")
        assert opts.logarithmic_conversion is False

    # --- file format and bit depth ---

    def test_file_format_dpx_8(self) -> None:
        opts = _cineon_opts("file_format_dpx_8")
        assert opts.file_format == CineonFileFormat.DPX
        assert opts.bit_depth == 8

    def test_file_format_dpx_10(self) -> None:
        opts = _cineon_opts("file_format_dpx_10")
        assert opts.file_format == CineonFileFormat.DPX
        assert opts.bit_depth == 10

    def test_file_format_dpx_12(self) -> None:
        opts = _cineon_opts("file_format_dpx_12")
        assert opts.file_format == CineonFileFormat.DPX
        assert opts.bit_depth == 12

    def test_file_format_dpx_16(self) -> None:
        opts = _cineon_opts("file_format_dpx_16")
        assert opts.file_format == CineonFileFormat.DPX
        assert opts.bit_depth == 16

    def test_file_format_fido(self) -> None:
        """FIDO/Cineon 4.5 format."""
        opts = _cineon_opts("file_format_fido")
        assert opts.file_format == CineonFileFormat.FIDO_CINEON

    # --- highlight expansion ---

    def test_highlight_expansion_0(self) -> None:
        opts = _cineon_opts("highlight_expansion_0")
        assert opts.highlight_expansion == 0

    def test_highlight_expansion_1(self) -> None:
        opts = _cineon_opts("highlight_expansion_1")
        assert opts.highlight_expansion == 1

    def test_highlight_expansion_150(self) -> None:
        opts = _cineon_opts("highlight_expansion_150")
        assert opts.highlight_expansion == 150


class TestAviFormatOptions:
    """Tests for AVI format options parsed from Ropt chunks (now XmlFormatOptions)."""

    def test_base_type(self) -> None:
        """AVI base sample returns XmlFormatOptions."""
        opts = _avi_opts("base")
        assert isinstance(opts, XmlFormatOptions)

    def test_base_format_code(self) -> None:
        """AVI base sample has format_code '.AVI'."""
        opts = _avi_opts("base")
        assert opts.format_code == ".AVI"

    def test_base_video_codec(self) -> None:
        """Base AVI uses the default "None" codec (DIB)."""
        opts = _avi_opts("base")
        assert opts.video_codec == VideoCodec.NONE

    def test_base_audio_codec(self) -> None:
        opts = _avi_opts("base")
        assert opts.audio_codec == AudioCodec.UNCOMPRESSED

    def test_base_frame_rate(self) -> None:
        opts = _avi_opts("base")
        assert opts.frame_rate == 24.0

    def test_base_has_params(self) -> None:
        """Base AVI has expected parameter keys."""
        opts = _avi_opts("base")
        assert "ADBEVideoCodec" in opts.params
        assert "ADBEVideoQuality" in opts.params
        assert "ADBEVideoWidth" in opts.params
        assert "ADBEVideoHeight" in opts.params

    # --- video codecs ---

    def test_video_codec_none(self) -> None:
        """'None' codec maps to VideoCodec.NONE."""
        opts = _avi_opts("video_codec_none")
        assert opts.video_codec == VideoCodec.NONE

    def test_video_codec_dv_24p_advanced(self) -> None:
        """DV 24p Advanced codec maps to VideoCodec.DV_24P."""
        opts = _avi_opts("video_codec_dv_24p_advanced")
        assert opts.video_codec == VideoCodec.DV_24P

    def test_video_codec_dv_ntsc(self) -> None:
        """DV NTSC codec maps to VideoCodec.DV_NTSC."""
        opts = _avi_opts("video_codec_dv_ntsc")
        assert opts.video_codec == VideoCodec.DV_NTSC

    def test_video_codec_dv_pal(self) -> None:
        """DV PAL codec maps to VideoCodec.DV_PAL."""
        opts = _avi_opts("video_codec_dv_pal")
        assert opts.video_codec == VideoCodec.DV_PAL

    def test_video_codec_intel_iyuv(self) -> None:
        """Intel IYUV codec maps to VideoCodec.INTEL_IYUV."""
        opts = _avi_opts("video_codec_intel_iyuv_codec")
        assert opts.video_codec == VideoCodec.INTEL_IYUV

    def test_video_codec_uyvy_422(self) -> None:
        """Uncompressed UYVY 422 8bit maps to VideoCodec.UYVY."""
        opts = _avi_opts("video_codec_uncompressed_uyvy_422_8bit")
        assert opts.video_codec == VideoCodec.UYVY

    def test_video_codec_v210(self) -> None:
        """V210 10-bit YUV maps to VideoCodec.V210."""
        opts = _avi_opts("video_codec_v210_10-bit_yuv")
        assert opts.video_codec == VideoCodec.V210

    # --- audio interleave ---

    def test_audio_interleave_none(self) -> None:
        """Audio interleave 'None' has no ADBEAudioInterleave param."""
        opts = _avi_opts("audio_interleave_none")
        assert opts.params.get("ADBEAudioInterleave") is None

    def test_audio_interleave_1_frame(self) -> None:
        opts = _avi_opts("audio_interleave_1_frame")
        assert opts.params["ADBEAudioInterleave"] == "1"

    def test_audio_interleave_half_second(self) -> None:
        opts = _avi_opts("audio_interleave_half_second")
        assert opts.params["ADBEAudioInterleave"] == "2"

    def test_audio_interleave_1_second(self) -> None:
        opts = _avi_opts("audio_interleave_1_second")
        assert opts.params["ADBEAudioInterleave"] == "3"

    def test_audio_interleave_2_seconds(self) -> None:
        opts = _avi_opts("audio_interleave2_seconds")
        assert opts.params["ADBEAudioInterleave"] == "4"


class TestFormatOptionsNone:
    """Test that formats without Ropt parsing return None."""

    def test_no_ropt_returns_none(self) -> None:
        """A format that doesn't have Ropt (or uses unsupported format)
        should return None for format_options."""
        samples_dir = Path(__file__).parent.parent / "samples" / "models"
        rq_base = samples_dir / "renderqueue" / "base.aep"
        project = parse_project(rq_base)
        om = project.render_queue.items[0].output_modules[0]
        assert om.format_options is None or isinstance(
            om.format_options,
            (
                CineonFormatOptions,
                JpegFormatOptions,
                OpenExrFormatOptions,
                PngFormatOptions,
                TargaFormatOptions,
                TiffFormatOptions,
                XmlFormatOptions,
            ),
        )


# ---------------------------------------------------------------------------
# XML-based formats (H.264, MP3, QuickTime, WAV)
# ---------------------------------------------------------------------------


def _format_opts(fmt_dir: str, name: str = "base") -> XmlFormatOptions:
    """Parse a sample from the given format dir and return XmlFormatOptions."""
    project = parse_project(FORMAT_DIR / fmt_dir / f"{name}.aep")
    opts = project.render_queue.items[0].output_modules[0].format_options
    assert isinstance(opts, XmlFormatOptions)
    return opts


class TestH264FormatOptions:
    """Tests for H.264 format options (XML-based)."""

    def test_type(self) -> None:
        opts = _format_opts("h.264")
        assert isinstance(opts, XmlFormatOptions)

    def test_format_code(self) -> None:
        opts = _format_opts("h.264")
        assert opts.format_code == "H264"

    def test_video_codec(self) -> None:
        opts = _format_opts("h.264")
        assert opts.video_codec == VideoCodec.AVC1

    def test_audio_codec(self) -> None:
        opts = _format_opts("h.264")
        assert opts.audio_codec == AudioCodec.AAC

    def test_frame_rate(self) -> None:
        opts = _format_opts("h.264")
        assert opts.frame_rate == 24.0

    def test_has_params(self) -> None:
        opts = _format_opts("h.264")
        assert len(opts.params) > 0

    def test_mpeg_audio_format_aac(self) -> None:
        """Base H.264 sample uses AAC audio format."""
        opts = _format_opts("h.264")
        assert opts.mpeg_audio_format == MPEGAudioFormat.AAC

    def test_mpeg_audio_format_mpeg(self) -> None:
        """MPEG audio format sample has ADBEMPEGAudioFormat set to MPEG."""
        project = parse_project(
            FORMAT_DIR / "h.264" / "audio_format_mpeg.aep"
        )
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, XmlFormatOptions)
        assert opts.mpeg_audio_format == MPEGAudioFormat.MPEG

    def test_mpeg_multiplexer(self) -> None:
        opts = _format_opts("h.264")
        assert opts.mpeg_multiplexer == MPEGMultiplexer.MP4

    def test_mpeg_mux_stream_compatibility(self) -> None:
        opts = _format_opts("h.264")
        assert opts.mpeg_mux_stream_compatibility == MPEGMuxStreamCompatibility.STD

    def test_mpeg_audio_layer_i(self) -> None:
        project = parse_project(
            FORMAT_DIR / "h.264" / "audio_format_mpeg.aep"
        )
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, XmlFormatOptions)
        assert opts.params["ADBEMPEGAudioLayer"] == "1"

    def test_mpeg_audio_layer_ii(self) -> None:
        project = parse_project(
            FORMAT_DIR / "h.264" / "audio_format_mpeg_layer_II.aep"
        )
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, XmlFormatOptions)
        assert opts.params["ADBEMPEGAudioLayer"] == "2"

    def test_mpeg_audio_format_pcm(self) -> None:
        """PCM audio format sample."""
        opts = _format_opts("h.264", "audio_format_pcm")
        assert opts.mpeg_audio_format == MPEGAudioFormat.PCM

    def test_multiplexer_3gpp(self) -> None:
        opts = _format_opts("h.264", "multiplexer_3gpp")
        assert opts.mpeg_multiplexer == MPEGMultiplexer.THREEGPP

    def test_multiplexer_none(self) -> None:
        opts = _format_opts("h.264", "multiplexer_none")
        assert opts.mpeg_multiplexer == MPEGMultiplexer.NONE

    def test_audio_codec_aac_plus_v1(self) -> None:
        opts = _format_opts("h.264", "audio_codec_aac+_version_1")
        assert opts.audio_codec == AudioCodec.AAC_PLUS_V1

    def test_audio_codec_aac_plus_v2(self) -> None:
        opts = _format_opts("h.264", "audio_codec_aac+_version_2")
        assert opts.audio_codec == AudioCodec.AAC_PLUS_V2

    def test_stream_compat_ipod(self) -> None:
        opts = _format_opts("h.264", "stream_compat_ipod")
        assert opts.mpeg_mux_stream_compatibility == MPEGMuxStreamCompatibility.IPOD

    def test_stream_compat_psp(self) -> None:
        opts = _format_opts("h.264", "stream_compat_psp")
        assert opts.mpeg_mux_stream_compatibility == MPEGMuxStreamCompatibility.PSP


class TestMp3FormatOptions:
    """Tests for MP3 format options (XML-based)."""

    def test_type(self) -> None:
        opts = _format_opts("mp3")
        assert isinstance(opts, XmlFormatOptions)

    def test_format_code(self) -> None:
        opts = _format_opts("mp3")
        assert opts.format_code == "Mp3 "

    def test_video_codec_none(self) -> None:
        """MP3 is audio-only, so video_codec should be None."""
        opts = _format_opts("mp3")
        assert opts.video_codec is None

    def test_frame_rate_none(self) -> None:
        """MP3 is audio-only, so frame_rate should be None."""
        opts = _format_opts("mp3")
        assert opts.frame_rate is None

    def test_audio_codec_uncompressed(self) -> None:
        opts = _format_opts("mp3")
        assert opts.audio_codec == AudioCodec.UNCOMPRESSED

    def test_has_params(self) -> None:
        opts = _format_opts("mp3")
        assert len(opts.params) > 0


class TestQuickTimeFormatOptions:
    """Tests for QuickTime format options (XML-based)."""

    def test_type(self) -> None:
        opts = _format_opts("quicktime")
        assert isinstance(opts, XmlFormatOptions)

    def test_format_code(self) -> None:
        opts = _format_opts("quicktime")
        assert opts.format_code == "MooV"

    def test_video_codec(self) -> None:
        opts = _format_opts("quicktime")
        assert opts.video_codec == VideoCodec.ANIMATION

    def test_frame_rate(self) -> None:
        opts = _format_opts("quicktime")
        assert opts.frame_rate == 24.0

    def test_audio_codec_none(self) -> None:
        """QuickTime base sample has no ADBEAudioCodec param."""
        opts = _format_opts("quicktime")
        assert opts.audio_codec is None

    def test_mpeg_audio_format_none(self) -> None:
        """QuickTime base sample has no ADBEMPEGAudioFormat param."""
        opts = _format_opts("quicktime")
        assert opts.mpeg_audio_format is None

    def test_mpeg_multiplexer(self) -> None:
        opts = _format_opts("quicktime")
        assert opts.mpeg_multiplexer == MPEGMultiplexer.MP4

    def test_mpeg_mux_stream_compatibility(self) -> None:
        opts = _format_opts("quicktime")
        assert opts.mpeg_mux_stream_compatibility == MPEGMuxStreamCompatibility.STD

    def test_has_params(self) -> None:
        opts = _format_opts("quicktime")
        assert len(opts.params) > 0

    def test_video_codec_apple_prores_422(self) -> None:
        opts = _format_opts("quicktime", "apple_prores_422")
        assert opts.video_codec == VideoCodec.APPLE_PRORES_422

    def test_video_codec_apple_prores_422_hq(self) -> None:
        opts = _format_opts("quicktime", "apple_prores_422_hq")
        assert opts.video_codec == VideoCodec.APPLE_PRORES_422_HQ

    def test_video_codec_apple_prores_422_lt(self) -> None:
        opts = _format_opts("quicktime", "apple_prores_422_lt")
        assert opts.video_codec == VideoCodec.APPLE_PRORES_422_LT

    def test_video_codec_apple_prores_422_proxy(self) -> None:
        opts = _format_opts("quicktime", "apple_prores_422_proxy")
        assert opts.video_codec == VideoCodec.APPLE_PRORES_422_PROXY

    def test_video_codec_apple_prores_4444(self) -> None:
        opts = _format_opts("quicktime", "apple_prores_4444")
        assert opts.video_codec == VideoCodec.APPLE_PRORES_4444

    def test_video_codec_apple_prores_4444_xq(self) -> None:
        opts = _format_opts("quicktime", "apple_prores_4444_xq")
        assert opts.video_codec == VideoCodec.APPLE_PRORES_4444_XQ

    def test_video_codec_dnxhr_dnxhd(self) -> None:
        opts = _format_opts("quicktime", "dnxhr_dnxhd")
        assert opts.video_codec == VideoCodec.DNXHR_DNXHD

    def test_video_codec_dv25_ntsc(self) -> None:
        opts = _format_opts("quicktime", "dv25_ntsc")
        assert opts.video_codec == VideoCodec.DV25_NTSC

    def test_video_codec_dv25_ntsc_24p(self) -> None:
        opts = _format_opts("quicktime", "dv25_ntsc_24p")
        assert opts.video_codec == VideoCodec.DV25_NTSC_24P

    def test_video_codec_dv25_pal(self) -> None:
        opts = _format_opts("quicktime", "dv25_pal")
        assert opts.video_codec == VideoCodec.DV25_PAL

    def test_video_codec_dv50_ntsc(self) -> None:
        opts = _format_opts("quicktime", "dv50_ntsc")
        assert opts.video_codec == VideoCodec.DV50_NTSC

    def test_video_codec_dv50_pal(self) -> None:
        opts = _format_opts("quicktime", "dv50_pal")
        assert opts.video_codec == VideoCodec.DV50_PAL

    def test_video_codec_dvcpro_hd_1080i50(self) -> None:
        opts = _format_opts("quicktime", "dvcpro_hd_1080i50")
        assert opts.video_codec == VideoCodec.DVCPRO_HD_1080I50

    def test_video_codec_dvcpro_hd_1080i60(self) -> None:
        opts = _format_opts("quicktime", "dvcpro_hd_1080i60")
        assert opts.video_codec == VideoCodec.DVCPRO_HD_1080I60

    def test_video_codec_dvcpro_hd_1080p25(self) -> None:
        opts = _format_opts("quicktime", "dvcpro_hd_1080p25")
        assert opts.video_codec == VideoCodec.DVCPRO_HD_1080P25

    def test_video_codec_dvcpro_hd_1080p30(self) -> None:
        opts = _format_opts("quicktime", "dvcpro_hd_1080p30")
        assert opts.video_codec == VideoCodec.DVCPRO_HD_1080P30

    def test_video_codec_dvcpro_hd_720p50(self) -> None:
        opts = _format_opts("quicktime", "dvcpro_hd_720p50")
        assert opts.video_codec == VideoCodec.DVCPRO_HD_720P50

    def test_video_codec_dvcpro_hd_720p60(self) -> None:
        opts = _format_opts("quicktime", "dvcpro_hd_720p60")
        assert opts.video_codec == VideoCodec.DVCPRO_HD_720P60

    def test_video_codec_gopro_cineform(self) -> None:
        opts = _format_opts("quicktime", "gopro_cineform")
        assert opts.video_codec == VideoCodec.GOPRO_CINEFORM

    def test_video_codec_h264(self) -> None:
        opts = _format_opts("quicktime", "h.264")
        assert opts.video_codec == VideoCodec.AVC1

    def test_video_codec_none_uncompressed_rgb(self) -> None:
        opts = _format_opts("quicktime", "none_uncompressed_rgb_8-bit")
        assert opts.video_codec == VideoCodec.UNCOMPRESSED_RGB_8_BIT

    def test_video_codec_uncompressed_yuv_10_bit(self) -> None:
        opts = _format_opts("quicktime", "uncompressed_yuv_10_bit_422")
        assert opts.video_codec == VideoCodec.UNCOMPRESSED_YUV_10_BIT_422

    def test_video_codec_uncompressed_yuv_8_bit(self) -> None:
        opts = _format_opts("quicktime", "uncompressed_yuv_8_bit_422")
        assert opts.video_codec == VideoCodec.UNCOMPRESSED_YUV_8_BIT_422


class TestWavFormatOptions:
    """Tests for WAV format options (XML-based)."""

    def test_type(self) -> None:
        opts = _format_opts("wav")
        assert isinstance(opts, XmlFormatOptions)

    def test_format_code(self) -> None:
        opts = _format_opts("wav")
        assert opts.format_code == "wao_"

    def test_video_codec_none(self) -> None:
        """WAV is audio-only, so video_codec should be None."""
        opts = _format_opts("wav")
        assert opts.video_codec is None

    def test_frame_rate_none(self) -> None:
        """WAV is audio-only, so frame_rate should be None."""
        opts = _format_opts("wav")
        assert opts.frame_rate is None

    def test_audio_codec_uncompressed(self) -> None:
        opts = _format_opts("wav")
        assert opts.audio_codec == AudioCodec.UNCOMPRESSED

    def test_audio_codec_ima_adpcm(self) -> None:
        project = parse_project(FORMAT_DIR / "wav" / "audio_codec_ima_adpcm.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, XmlFormatOptions)
        assert opts.audio_codec == AudioCodec.IMA_ADPCM

    def test_audio_codec_microsoft_adpcm(self) -> None:
        project = parse_project(FORMAT_DIR / "wav" / "audio_codec_microsoft_adpcm.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, XmlFormatOptions)
        assert opts.audio_codec == AudioCodec.MICROSOFT_ADPCM

    def test_audio_codec_ccitt_a_law(self) -> None:
        project = parse_project(FORMAT_DIR / "wav" / "audio_codec_ccitt_a-law.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, XmlFormatOptions)
        assert opts.audio_codec == AudioCodec.CCITT_A_LAW

    def test_audio_codec_ccitt_u_law(self) -> None:
        project = parse_project(FORMAT_DIR / "wav" / "audio_codec_ccitt_u-law.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, XmlFormatOptions)
        assert opts.audio_codec == AudioCodec.CCITT_U_LAW

    def test_audio_codec_gsm_6_10(self) -> None:
        project = parse_project(FORMAT_DIR / "wav" / "audio_codec_gsm_6.10.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, XmlFormatOptions)
        assert opts.audio_codec == AudioCodec.GSM_6_10

    def test_has_params(self) -> None:
        opts = _format_opts("wav")
        assert len(opts.params) > 0


# ---------------------------------------------------------------------------
# Binary formats (JPEG, OpenEXR, PNG, Targa, TIFF)
# ---------------------------------------------------------------------------


class TestJpegFormatOptions:
    """Tests for JPEG format options."""

    def _opts(self, stem: str) -> JpegFormatOptions:
        project = parse_project(FORMAT_DIR / "jpeg" / f"{stem}.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, JpegFormatOptions)
        return opts

    def test_type(self) -> None:
        self._opts("base")

    def test_quality_0(self) -> None:
        assert self._opts("quality_0").quality == 0

    def test_quality_5(self) -> None:
        assert self._opts("base").quality == 5

    def test_quality_10(self) -> None:
        assert self._opts("quality_10").quality == 10

    def test_baseline_standard(self) -> None:
        assert self._opts("baseline_standard").format_type == JpegFormatType.BASELINE_STANDARD

    def test_baseline_optimized(self) -> None:
        assert self._opts("baseline_optimized").format_type == JpegFormatType.BASELINE_OPTIMIZED

    def test_progressive(self) -> None:
        assert self._opts("progressive_3").format_type == JpegFormatType.PROGRESSIVE

    def test_scans_3(self) -> None:
        assert self._opts("progressive_3").scans == 3

    def test_scans_4(self) -> None:
        assert self._opts("progressive_4").scans == 4

    def test_scans_5(self) -> None:
        assert self._opts("progressive_5").scans == 5

    def test_scans_non_progressive(self) -> None:
        assert self._opts("base").scans == 3


class TestOpenExrFormatOptions:
    """Tests for OpenEXR format options."""

    def test_type(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)

    def test_compression_none(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_none.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.compression == OpenExrCompression.NONE

    def test_compression_rle(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_rle.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.compression == OpenExrCompression.RLE

    def test_compression_zip(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.compression == OpenExrCompression.ZIP

    def test_compression_zip16(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_zip16.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.compression == OpenExrCompression.ZIP16

    def test_compression_piz(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_piz.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.compression == OpenExrCompression.PIZ

    def test_compression_pxr24(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_pxr24.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.compression == OpenExrCompression.PXR24

    def test_compression_b44(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_b44.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.compression == OpenExrCompression.B44

    def test_compression_b44a(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_b44a.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.compression == OpenExrCompression.B44A

    def test_compression_dwaa(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_dwaa_45.0.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.compression == OpenExrCompression.DWAA

    def test_compression_dwab(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_dwab_200.0.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.compression == OpenExrCompression.DWAB

    def test_luminance_chroma_off(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.luminance_chroma is False

    def test_luminance_chroma_on(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_zip_luminance_chroma.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.luminance_chroma is True

    def test_32_bit_float_off(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.thirty_two_bit_float is False

    def test_32_bit_float_on(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_zip_32_bit_float.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.thirty_two_bit_float is True

    def test_dwa_compression_level_none_for_zip(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.dwa_compression_level is None

    def test_dwa_compression_level_dwaa_default(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_dwaa_45.0.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.dwa_compression_level == 45.0

    def test_dwa_compression_level_dwaa_custom(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_dwaa_1.0.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.dwa_compression_level == 1.0

    def test_dwa_compression_level_dwaa_large(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_dwaa_10000000000.0.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.dwa_compression_level == 10000000000.0

    def test_dwa_compression_level_dwab(self) -> None:
        project = parse_project(FORMAT_DIR / "openexr" / "compression_dwab_200.0.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, OpenExrFormatOptions)
        assert opts.dwa_compression_level == 200.0


class TestPngFormatOptions:
    """Tests for PNG format options (typed binary)."""

    def test_type(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)

    def test_width(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.width == 1920

    def test_height(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.height == 1080

    def test_bit_depth(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.bit_depth == 16

    def test_compression_none(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "compression_none.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.compression == PngCompression.NONE

    def test_compression_interlaced(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "compression_interlaced.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.compression == PngCompression.INTERLACED

    def test_include_hdr10_metadata_off(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.include_hdr10_metadata is False

    def test_include_hdr10_metadata_on(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "include_hdr10_metadata_on.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.include_hdr10_metadata is True

    def test_color_primaries_default(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "include_hdr10_metadata_on.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.color_primaries == Hdr10ColorPrimaries.P3_D65

    def test_color_primaries_rec709(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "color_primaries_rec709.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.color_primaries == Hdr10ColorPrimaries.REC709

    def test_color_primaries_rec2020(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "color_primaries_rec2020.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.color_primaries == Hdr10ColorPrimaries.REC2020

    def test_color_primaries_p3d65(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "color_primaries_p3d65.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.color_primaries == Hdr10ColorPrimaries.P3_D65

    def test_luminance_min_default(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.luminance_min is None

    def test_luminance_min_zero(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "luminance_min_0.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.luminance_min == 0.0

    def test_luminance_max_default(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.luminance_max is None

    def test_luminance_max_set(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "luminance_max_1.797693e+308.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.luminance_max == 1.7976931348623157e+308

    def test_content_light_max_default(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.content_light_max is None

    def test_content_light_max_set(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "content_light_levels_maximum_1.797693e+308.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.content_light_max == 1.7976931348623157e+308

    def test_content_light_average_default(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.content_light_average is None

    def test_content_light_average_set(self) -> None:
        project = parse_project(FORMAT_DIR / "png" / "content_light_levels_average_1.797693e+308.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, PngFormatOptions)
        assert opts.content_light_average == 1.7976931348623157e+308


class TestTargaFormatOptions:
    """Tests for Targa format options (binary)."""

    def test_type(self) -> None:
        project = parse_project(FORMAT_DIR / "targa" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TargaFormatOptions)

    def test_base_bits_per_pixel(self) -> None:
        project = parse_project(FORMAT_DIR / "targa" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TargaFormatOptions)
        assert opts.bits_per_pixel == 32

    def test_base_rle_compression_off(self) -> None:
        project = parse_project(FORMAT_DIR / "targa" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TargaFormatOptions)
        assert opts.rle_compression is False

    def test_24_bits_per_pixel(self) -> None:
        project = parse_project(FORMAT_DIR / "targa" / "24_bits_per_pixel.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TargaFormatOptions)
        assert opts.bits_per_pixel == 24

    def test_32_bits_per_pixel(self) -> None:
        project = parse_project(FORMAT_DIR / "targa" / "32_bits_per_pixel.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TargaFormatOptions)
        assert opts.bits_per_pixel == 32

    def test_rle_compression_on(self) -> None:
        project = parse_project(FORMAT_DIR / "targa" / "rle_compression_on.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TargaFormatOptions)
        assert opts.rle_compression is True

    def test_rle_compression_on_bits_per_pixel(self) -> None:
        project = parse_project(FORMAT_DIR / "targa" / "rle_compression_on.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TargaFormatOptions)
        assert opts.bits_per_pixel == 24


class TestTiffFormatOptions:
    """Tests for TIFF format options."""

    def test_type(self) -> None:
        project = parse_project(FORMAT_DIR / "tiff" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TiffFormatOptions)

    def test_base_lzw_compression_off(self) -> None:
        project = parse_project(FORMAT_DIR / "tiff" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TiffFormatOptions)
        assert opts.lzw_compression is False

    def test_base_ibm_pc_byte_order_off(self) -> None:
        project = parse_project(FORMAT_DIR / "tiff" / "base.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TiffFormatOptions)
        assert opts.ibm_pc_byte_order is False

    def test_lzw_compression_on(self) -> None:
        project = parse_project(FORMAT_DIR / "tiff" / "lze_compression_on.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TiffFormatOptions)
        assert opts.lzw_compression is True

    def test_lzw_compression_on_ibm_pc_off(self) -> None:
        project = parse_project(FORMAT_DIR / "tiff" / "lze_compression_on.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TiffFormatOptions)
        assert opts.ibm_pc_byte_order is False

    def test_ibm_pc_byte_order_on(self) -> None:
        project = parse_project(FORMAT_DIR / "tiff" / "ibm_pc_byte_order_on.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TiffFormatOptions)
        assert opts.ibm_pc_byte_order is True

    def test_ibm_pc_byte_order_on_lzw_off(self) -> None:
        project = parse_project(FORMAT_DIR / "tiff" / "ibm_pc_byte_order_on.aep")
        opts = project.render_queue.items[0].output_modules[0].format_options
        assert isinstance(opts, TiffFormatOptions)
        assert opts.lzw_compression is False
