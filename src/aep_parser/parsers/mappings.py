"""Mappings from binary values to ExtendScript enum values.

Binary values in AEP files often differ from ExtendScript API values.
This module provides the translation layer between Kaitai-parsed raw values
and the Python enum types that match ExtendScript.
"""

from __future__ import annotations

from ..enums import (
    AlphaMode,
    AutoOrientType,
    FastPreviewType,
    FieldSeparationType,
    FrameBlendingType,
    GpuAccelType,
    OutputAudio,
    ViewerType,
)


def map_alpha_mode(alpha_mode_raw: int, has_alpha: bool) -> AlphaMode:
    """Map binary alpha_mode value to ExtendScript AlphaMode enum.

    Args:
        alpha_mode_raw: Raw value from sspc chunk.
        has_alpha: Whether the footage has an alpha channel.

    Raises:
        ValueError: If alpha_mode_raw is not a recognized value.
    """
    if not has_alpha:
        return AlphaMode.IGNORE

    mapping = {
        0: AlphaMode.STRAIGHT,
        1: AlphaMode.PREMULTIPLIED,
        2: AlphaMode.IGNORE,
        3: AlphaMode.IGNORE,  # no_alpha treated as ignore
    }
    try:
        return mapping[alpha_mode_raw]
    except KeyError:
        raise ValueError(f"Unknown alpha_mode value: {alpha_mode_raw}") from None


def map_field_separation_type(
    field_separation_type_raw: int, field_order_raw: int
) -> FieldSeparationType:
    """Map binary field separation values to ExtendScript FieldSeparationType enum.

    Args:
        field_separation_type_raw: 0=off, 1=enabled.
        field_order_raw: 0=upper_field_first, 1=lower_field_first.
    """
    if field_separation_type_raw == 0:
        return FieldSeparationType.OFF
    if field_order_raw == 0:
        return FieldSeparationType.UPPER_FIELD_FIRST
    return FieldSeparationType.LOWER_FIELD_FIRST


def map_frame_blending_type(
    frame_blending_type_raw: int, frame_blending_enabled: bool
) -> FrameBlendingType:
    """Map binary frame_blending_type value to ExtendScript FrameBlendingType enum.

    In the binary format, frame_blending_type is stored as a 1-bit value:
    - 0 = FRAME_MIX (default when frame blending is enabled)
    - 1 = PIXEL_MOTION

    However, when frame_blending is disabled (False), the returned type
    should always be NO_FRAME_BLEND (4012), regardless of the bit value.

    Args:
        frame_blending_type_raw: The raw 1-bit value from the binary.
        frame_blending_enabled: Whether frame blending is enabled on the layer.

    Raises:
        ValueError: If frame_blending_type_raw is not a recognized value.
    """
    if not frame_blending_enabled:
        return FrameBlendingType.NO_FRAME_BLEND

    mapping = {
        0: FrameBlendingType.FRAME_MIX,
        1: FrameBlendingType.PIXEL_MOTION,
    }
    try:
        return mapping[frame_blending_type_raw]
    except KeyError:
        raise ValueError(
            f"Unknown frame_blending_type value: {frame_blending_type_raw}"
        ) from None


def map_auto_orient_type(
    auto_orient_along_path: bool,
    camera_or_poi_auto_orient: bool,
    three_d_layer: bool,
    characters_toward_camera: bool,
    three_d_per_char: bool,
) -> AutoOrientType:
    """Derive the AutoOrientType from binary ldta data bits.

    The auto-orient type is stored across multiple non-contiguous bits in
    the binary format rather than as a single value:

    - ALONG_PATH: auto_orient_along_path bit is set
    - CAMERA_OR_POINT_OF_INTEREST: camera_or_poi_auto_orient AND three_d_layer are set
    - CHARACTERS_TOWARD_CAMERA: characters_toward_camera AND three_d_per_char are set
    - NO_AUTO_ORIENT: none of the above conditions are met

    Args:
        auto_orient_along_path: The auto_orient_along_path bit from ldta.
        camera_or_poi_auto_orient: The camera_or_poi_auto_orient bit from ldta.
        three_d_layer: Whether the layer is a 3D layer.
        characters_toward_camera: The characters_toward_camera bit from ldta.
        three_d_per_char: The three_d_per_char bit from ldta.
    """
    if auto_orient_along_path:
        return AutoOrientType.ALONG_PATH
    elif camera_or_poi_auto_orient and three_d_layer:
        return AutoOrientType.CAMERA_OR_POINT_OF_INTEREST
    elif characters_toward_camera and three_d_per_char:
        return AutoOrientType.CHARACTERS_TOWARD_CAMERA
    else:
        return AutoOrientType.NO_AUTO_ORIENT


def map_fast_preview_type(
    adaptive: bool,
    wireframe: bool,
) -> FastPreviewType:
    """Derive the FastPreviewType from individual fips bit flags.

    Args:
        adaptive: Whether the adaptive resolution bit is set.
        wireframe: Whether the wireframe bit is set.
    """
    if wireframe:
        return FastPreviewType.FP_WIREFRAME
    if adaptive:
        return FastPreviewType.FP_ADAPTIVE_RESOLUTION
    return FastPreviewType.FP_OFF


def map_viewer_type_from_string(label: str) -> ViewerType:
    """Map a viewer panel type label string to a ViewerType enum.

    The `fitt` chunk stores the inner tab type as an ASCII string
    (e.g. `"AE Composition"`). This function converts that string
    to the corresponding [ViewerType][aep_parser.enums.ViewerType] value.

    Args:
        label: The panel type label from the `fitt` chunk.

    Returns:
        The matching [ViewerType][aep_parser.enums.ViewerType]

    Raises:
        ValueError: If the label is not recognized.
    """
    mapping = {
        "AE Composition": ViewerType.VIEWER_COMPOSITION,
        "AE Layer": ViewerType.VIEWER_LAYER,
        "AE Footage": ViewerType.VIEWER_FOOTAGE,
    }
    try:
        return mapping[label]
    except KeyError:
        raise ValueError(f"Unknown viewer type label: {label!r}") from None


def map_gpu_accel_type(uuid: str) -> GpuAccelType | None:
    """Map a gpuG UUID to a GpuAccelType enum value.

    The GPU acceleration type is stored in the `gpuG` LIST chunk as a
    UUID string.  Known UUIDs are mapped to their corresponding enum
    value; unknown UUIDs default to `None`.

    Args:
        uuid: The UUID string from the gpuG Utf8 chunk.
    """
    mapping = {
        "7ee0ab59-822d-44cc-ac10-16279d041016": GpuAccelType.CUDA,
        "f33089e2-1ede-47c1-8a9e-b232bb1cc1a4": GpuAccelType.SOFTWARE,
    }
    try:
        return mapping[uuid]
    except KeyError:
        return None


def map_output_audio(
    audio_enabled: bool,
    audio_auto: bool,
) -> OutputAudio:
    """Derive the Output Audio setting from two binary sources.


    Args:
        audio_enabled: Whether audio is enabled.
        audio_auto: Whether audio is set to auto.
    """
    if not audio_enabled:
        return OutputAudio.OFF
    if audio_auto:
        return OutputAudio.AUTO
    return OutputAudio.ON


def map_output_color_space(
    output_profile_id: bytes,
    output_color_space_working: bool,
    working_space: str,
) -> str | None:
    """Map the output color space profile UID to a human-readable name.

    The 16-byte UID is the **ICC Profile ID** per ISO 15076-1 §7.2.18,
    computed as `MD5(icc_data)` with bytes 44-47, 64-67 and 84-99
    zeroed.  For Adobe color management, these correspond to ICC profiles
    shipped in the `MPProfiles` / `Profiles` directories.  For OCIO
    color management, the UIDs cannot be resolved without the OCIO config
    and more reverse-engineering.

    When `output_color_space_working` is `True`, the project's
    working color space name is returned directly.  Otherwise, the
    16-byte `output_profile_id` is looked up in the known profiles
    table.

    The mapping can be regenerated from ICC files on disk using
    `scripts/generate_color_space_mapping.py`.

    Args:
        output_profile_id: 16-byte binary profile identifier from the
            output-module `ldat` chunk.
        output_color_space_working: Flag indicating "Working Color
            Space".
        working_space: The project's working color space name.

    Returns:
        The color space name, or `None` if the profile is unknown.
    """
    mapping = {
        "7388945281150aeb4d9daebdafdc1801": "ACES Academy Color Encoding Specification SMPTE ST 2065-1",
        "ae27d1e66d65c5a0a50fe0ec149a24fa": "ACEScct",
        "9cc3d6762423e9d771726cb97d57cf3c": "ACEScg ACES Working Space AMPAS S-2014-004",
        "33bc7f1c156fa0d72f8f717ae5886bd4": "Adobe RGB (1998)",
        "47ae2b5f4c143df9d07b5dc78036b5a8": "Apple RGB",
        "938c06018c4f6479b790f94d0ea06d4c": "ARRI LogC3 Wide Color Gamut - EI 1000",
        "aa9af0bd200c8a86913c33ddf738c62e": "ARRI LogC3 Wide Color Gamut - EI 1280",
        "59be335a0f73c5e731914a695401c55a": "ARRI LogC3 Wide Color Gamut - EI 160",
        "3ece351cc10b1ef03e483218e2320479": "ARRI LogC3 Wide Color Gamut - EI 1600",
        "d11af53b9b6f1fe7b4885136d6df20aa": "ARRI LogC3 Wide Color Gamut - EI 200",
        "c2c24e98f0fb7749b83fe6be3f76350f": "ARRI LogC3 Wide Color Gamut - EI 250",
        "4d33f01c9c7bd608607e9298167a9b1a": "ARRI LogC3 Wide Color Gamut - EI 320",
        "25eeff532eb90fc255f52b6904ab2ae6": "ARRI LogC3 Wide Color Gamut - EI 400",
        "c4725e797859bdc0d9ab85b2cc053d62": "ARRI LogC3 Wide Color Gamut - EI 500",
        "d3a7ae72a5138d40efe1bb6adab86093": "ARRI LogC3 Wide Color Gamut - EI 640",
        "8713df03272443efeccbbf31d4f27c9a": "ARRI LogC3 Wide Color Gamut - EI 800",
        "93e2bc23777dadd2cf79ba4a43bb3e54": "ARRI WCG Preview LUT for P3",
        "fdad601ee83a18fc31695cd30fc77300": "ARRI WCG Preview LUT for P3D65",
        "1e3e358b79d80c0e9e0ed9ee9798aab8": "ARRI WCG Preview LUT for Rec. 709",
        "0e1c561854047a350def4656d9b9a5e6": "ARRIFLEX D-20 Daylight Log (by Adobe)",
        "bd07ddb13a773d6e99f74464c2a772eb": "ARRIFLEX D-20 Tungsten Log (by Adobe)",
        "dc07289838e4b2e009ad0fc7eb2abca6": "Canon Cinema CLog2",
        "076df49f51179c7a5a47b7ac8068cfeb": "Canon Cinema CLog3",
        "c2336f7797ce89ca59b34d9912612bf0": "CIE RGB",
        "34983ce67a8eaee8e97fb8f1e0288f39": "ColorMatch RGB",
        "c8868462c9733762898033c72da6ca9a": "DCDM X'Y'Z' D55 Gamma 2.6",
        "9884af1a63b7a668783b4a3a3f512cd8": "DCDM X'Y'Z' D60 Gamma 2.6",
        "62b316d7759b124fcd54ce531a39ff15": "DCDM X'Y'Z' D65 Gamma 2.6",
        "5c3eee63d9f0826014ac10dcad8405df": "DCDM X'Y'Z' DCI Gamma 2.6",
        "529294e457025111dbcb23be10ab12e4": "e-sRGB",  # WCS (Windows Color System) CDMP profile
        "9354712897186aa658ceeeaed72307b4": "Fujifilm 3510 (RDI) Theater Preview (by Adobe)",
        "981d06aef4c24e8d72e058b3c249f13c": "Fujifilm 3513DI (RDI) Theater Preview (by Adobe)",
        "b7402b70f8741d065142ad6be47d98e8": "Fujifilm 3521XD (RDI) Theater Preview (by Adobe)",
        "2d145edb108e4c3047ab83c793e1763e": "Fujifilm ETERNA 250 Printing Density (by Adobe)",
        "c19633c1fa5af36d7c232d58e2506005": "Fujifilm ETERNA 250D Printing Density (by Adobe)",
        "80b34d6de8c96e2492f3b98c1b44a3e9": "Fujifilm ETERNA 400 Printing Density (by Adobe)",
        "5f44607df576ac584674aa867977e9bd": "Fujifilm ETERNA 500 Printing Density (by Adobe)",
        "3238f5552f1da4ad4f4adc7ffec6cd0b": "Fujifilm ETERNA Vivid 160 Printing Density (by Adobe)",
        "c6ccd79b103a0e02374b71afaa419f12": "Fujifilm F-125 Printing Density (by Adobe)",
        "5e211ba46903dd4daee167cbdbc70919": "Fujifilm F-64D Printing Density (by Adobe)",
        "2ea8863ba779d1ad4740151b06f3f5fe": "Fujifilm REALA 500D Printing Density (by Adobe)",
        "5b06d4a00674a6d474ea9188aa6d92da": "HDTV (Rec. 709) 16-235",
        "c772b2d26a8f2450ce0da7ac2c511f4c": "image P3",
        "7f21e95c9baf764144f46327451decd1": "Kodak 2383 Theater Preview 2 (by Adobe)",
        "dc8e4dbe97f26bdd68b97e06411e700a": "Kodak 2393 Theater Preview 2 (by Adobe)",
        "8ec28b10560468781d0d8a06f0e51225": "Kodak 2395 Theater Preview 2 (by Adobe)",
        "a110df392a11c5ebe297abaeadf31102": "Kodak 5205/7205 Printing Density (by Adobe)",
        "fb3aeb6b63ae7c984d0b09cec29205ce": "Kodak 5218/7218 Printing Density (by Adobe)",
        "0588de19a1812143833739b276eb1da0": "Kodak 5229/7229 Printing Density (by Adobe)",
        "c2128160a8f9f69caf58fa1b991e4bb9": "P3 D55 Gamma 2.6",
        "11bbc3f39ce8c6f324096febf61fbb02": "P3 D60 Gamma 2.6",
        "63e456571bbbf4b88a8f28177e99d874": "P3 D65 Gamma 2.4",
        "202aa572b78122dd34b1e924a9ee1958": "P3 D65 Gamma 2.6",
        "0e76ac3b39c308dd7f0079bf6be13a7f": "P3 D65 PQ",
        "0eb77e006495d7bc03d02525d434e663": "P3 D65 PQ W100",
        "3ad9414c85526c2cda52690acbe82c43": "P3 D65 PQ W203",
        "eb04d089288cf6037587aa6d20d00253": "P3 D65 PQ W300",
        "de0357bcafad87f0932d1a638b1c436a": "P3 DCI Gamma 2.6",
        "5aca9378653ea1c34fbffe7e007148f9": "P3 DCI PQ",
        "990f17aa4481c7bf72a4b3bcbb936210": "PAL/SECAM",
        "601cc5eb6381ab9530b409103181ddc1": "Panasonic V-Gamut V-Log",
        "45d9ca4d5e7dd5788f59eb594008077b": "Panavision Genesis Tungsten Log (by Adobe)",
        "c24ec791616e49618507e9f6063b258a": "ProPhoto RGB",
        "f3d1fd924a2e68660ff244e95701d50b": "Rec.2020 Gamma 2.4",
        "88c25eb0b14f35c23b3fd0a8bf94d06e": "Rec.2100 HLG Scene W100",
        "167d9bc7b20cfbcf2f81bf8b92f0996d": "Rec.2100 HLG Scene W63",
        "4e4dec9b2e85417a79180842b7b55e7a": "Rec.2100 HLG Scene W75",
        "f6dbd53c7b1932473ecea085e3de0850": "Rec.2100 HLG Scene W81",
        "a2a5746a2068eff346cbc94c9a5bc0d3": "Rec.2100 HLG W100",
        "b68af357594e7b08a9c59eb15413830a": "Rec.2100 HLG W1000",
        "713ddb8ff5dec5fdc37054fadecdfd59": "Rec.2100 HLG W203",
        "1ef409903e2e37ef11fee50c2fd14bda": "Rec.2100 HLG W300",
        "506f062e12412703215710a53aef4744": "Rec.2100 PQ",
        "9c03f52174df8e05c8826d58c01db469": "Rec.2100 PQ W100",
        "a733cc4fb89c2e73cfab85df5c3c5230": "Rec.2100 PQ W10000",
        "4941fbef2b43d4c69424bc16c7752e15": "Rec.2100 PQ W203",
        "3454262a2e7d89bdc8c0a79984c0cbeb": "Rec.2100 PQ W300",
        "14c327c9133486996e84b8958ee0f26f": "Rec.601 NTSC Gamma 2.4",
        "5d0b55209357a0304922e494f6dc9f01": "Rec.601 PAL Gamma 2.4",
        "601e997329e4901f2acc5b497ba315f3": "Rec.709 Gamma 2.4",
        "9ff4f1f9a6242f963009c6b63c9db766": "Rec.709 HLG Scene W100",
        "5ae80163dace4f6c414caf63c7c2b8a9": "Rec.709 HLG Scene W63",
        "11907e643536fd2583bed1420fbeae67": "Rec.709 HLG Scene W75",
        "49409304bcc720cb6e0735756e9591a3": "Rec.709 HLG Scene W81",
        "32b1caa55e1783a2292fcea3c3c05862": "Rec.709 PQ",
        "5c83bb9bcb425451185b1ea2c57bf26c": "Rec.709 PQ W100",
        "0578c0a72e2aa6f2c0165482e80338b1": "Rec.709 PQ W203",
        "b955718aa0ce3ffd434c5b7973e25101": "Rec.709 PQ W300",
        "ec95b579e8046deb33d90544c1418727": "Rec.709 V-Log",
        "5101a72caf5a68d2274665c937ce54a0": "ROMM-RGB",
        "165180e0fe59947c25acfe66a655b90c": "SDTV NTSC 16-235",
        "7a1db9a17e573446aced16927d193aa3": "SDTV PAL 16-235",
        "82fcfdf86e94104ca27b00b675bd00f8": "SMPTE-C",
        "f2ef80974c3de8d7b28e33601ccea547": "Sony S-Gamut3.Cine/S-Log3",
        "a49ab775ef8f7260aac9deef5759a819": "Sony S-Gamut3/S-Log3",
        "1d3fda2edb4a89ab60a23c5f7c7d81dd": "sRGB IEC61966-2.1",
        "408770eb2f392dc4da437ca75b63d018": "Universal Camera Film Printing Density",
        "483c65ee9357334b8c5b2bfba0cdda90": "Viper FilmStream Daylight Log (by Adobe)",
        "479c5332bef3da7df6f539b4eca88b1b": "Viper FilmStream Tungsten Log (by Adobe)",
        "317695890d09f64fe3486ac9b7449879": "Wide Gamut RGB",
        # WCS (Windows Color System) CDMP profiles - no ICC files on disk,
        # Adobe Color Engine generates ICC wrappers at runtime.
        "cdbb342d1814a8f7eb3763b3e7fb57c4": "* wscRGB",
        "d5d94ab6e28455295be53988bae5d16e": "* wsRGB",
    }
    if output_color_space_working:
        return working_space
    uid_hex = output_profile_id.hex()
    return mapping.get(uid_hex)
