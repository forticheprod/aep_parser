from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO


@dataclass
class OutputModuleTemplate:
    """An output module template definition.

    Attributes:
        name: The template name (e.g., "Lossless", "H.264").
        base_path: The default output base path.
        file_pattern: The file name pattern (e.g., "[compName].[fileextension]").
    """

    name: str
    base_path: str = ""
    file_pattern: str = ""


@dataclass
class OutputFileInfo:
    """Output file format information.

    Attributes:
        id: The output file info ID number.
        format_code: The 4-character format code (e.g., ".AVI", "png!").
        raw_data: The raw hex/binary data string.
    """

    id: int
    format_code: str
    raw_data: str


@dataclass
class ExporterParam:
    """A single exporter parameter from the output options XML.

    Attributes:
        identifier: The parameter identifier (e.g., "ADBEAudioCodec").
        param_type: The parameter type code.
        value: The parameter value (string, int, bool, etc.).
    """

    identifier: str
    param_type: int
    value: str


@dataclass
class OutputFileOptions:
    """Output file options with exporter parameters.

    Contains embedded XML exporter settings for a specific format.

    Attributes:
        id: The output file options ID number.
        format_code: The 4-character format code.
        video_output: Whether video output is enabled.
        output_audio: Whether audio output is enabled.
        params: Dictionary of exporter parameters by identifier.
        raw_data: The raw hex/binary data string.
    """

    id: int
    format_code: str
    video_output: bool = False
    output_audio: bool = False
    params: dict[str, ExporterParam] = field(default_factory=dict)
    raw_data: str = ""


@dataclass
class OutputModulePreferences:
    """Output module preference indices.

    Attributes:
        default_om_index: Index of the default output module.
        prerender_om_index: Index for pre-render output.
        proxy_movie_om_index: Index for proxy movie output.
        save_preview_om_index: Index for save current preview output.
        still_frame_om_index: Index for still frame output.
    """

    default_om_index: int = 0
    prerender_om_index: int = 0
    proxy_movie_om_index: int = 0
    save_preview_om_index: int = 0
    still_frame_om_index: int = 0


@dataclass
class Settings:
    """Parsed After Effects output preferences.

    Contains output module templates and file format information
    from the prefs_indep_output.txt file.

    Attributes:
        version: The preferences file version string.
        output_module_templates: List of available output module templates.
        output_file_info: Dictionary mapping ID to output file format info.
        output_file_options: Dictionary mapping ID to output file options.
        output_module_prefs: Output module preference indices.
    """

    version: str = ""
    output_module_templates: list[OutputModuleTemplate] = field(default_factory=list)
    output_file_info: dict[int, OutputFileInfo] = field(default_factory=dict)
    output_file_options: dict[int, OutputFileOptions] = field(default_factory=dict)
    output_module_prefs: OutputModulePreferences = field(
        default_factory=OutputModulePreferences
    )


def parse_prefs_indep_output(path: str | Path) -> Settings:
    """Parse an After Effects prefs_indep_output preferences file.

    This file contains output module templates and settings used by the
    render queue. It's typically found in the After Effects preferences
    folder.

    Args:
        path: Path to the prefs_indep_output.txt file.

    Returns:
        A Settings object containing the parsed preferences.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is invalid.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return _parse_prefs_file(f)


def _parse_prefs_file(file: TextIO) -> Settings:
    """Parse the preferences file from a file object.

    Args:
        file: An open file object to read from.

    Returns:
        A Settings object containing the parsed preferences.
    """
    settings = Settings()
    current_section = ""

    # Temporary storage for multi-line values
    pending_key = ""
    pending_value = ""

    # Storage for template components by ID
    template_names: dict[int, str] = {}
    template_base_paths: dict[int, str] = {}
    template_file_patterns: dict[int, str] = {}

    for line in file:
        line = line.rstrip("\n\r")

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            # Check for version comment
            if line.startswith("# Text File Version"):
                settings.version = line.split("Version")[-1].strip()
            continue

        # Handle continuation lines (ending with \)
        if pending_key:
            pending_value += line.lstrip()
            if not line.endswith("\\"):
                # Process the complete value
                _process_key_value(
                    current_section,
                    pending_key,
                    pending_value,
                    settings,
                    template_names,
                    template_base_paths,
                    template_file_patterns,
                )
                pending_key = ""
                pending_value = ""
            else:
                # Remove trailing backslash for next iteration
                pending_value = pending_value[:-1]
            continue

        # Check for section header
        section_match = re.match(r'^\["([^"]+)"\]$', line)
        if section_match:
            current_section = section_match.group(1)
            continue

        # Check for key-value pair
        kv_match = re.match(r'^\s*"([^"]+)"\s*=\s*(.*)$', line)
        if kv_match:
            key = kv_match.group(1)
            value = kv_match.group(2)

            if value.endswith("\\"):
                # Multi-line value
                pending_key = key
                pending_value = value[:-1]
            else:
                _process_key_value(
                    current_section,
                    key,
                    value,
                    settings,
                    template_names,
                    template_base_paths,
                    template_file_patterns,
                )

    # Build output module templates from collected data
    all_ids = set(template_names.keys()) | set(template_base_paths.keys()) | set(
        template_file_patterns.keys()
    )
    for template_id in sorted(all_ids):
        name = template_names.get(template_id, "")
        if name:  # Only add templates with names
            settings.output_module_templates.append(
                OutputModuleTemplate(
                    name=name,
                    base_path=template_base_paths.get(template_id, ""),
                    file_pattern=template_file_patterns.get(template_id, ""),
                )
            )

    return settings


def _process_key_value(
    section: str,
    key: str,
    value: str,
    settings: Settings,
    template_names: dict[int, str],
    template_base_paths: dict[int, str],
    template_file_patterns: dict[int, str],
) -> None:
    """Process a key-value pair from the preferences file.

    Args:
        section: The current section name.
        key: The key name.
        value: The value string.
        settings: The Settings object to populate.
        template_names: Dictionary to collect template names by ID.
        template_base_paths: Dictionary to collect base paths by ID.
        template_file_patterns: Dictionary to collect file patterns by ID.
    """
    # Parse Output File Info entries
    if "Output File Info Preference Section" in section:
        match = re.match(r"Output File Info ID # (\d+)", key)
        if match:
            info_id = int(match.group(1))
            format_code = _extract_format_code(value)
            settings.output_file_info[info_id] = OutputFileInfo(
                id=info_id,
                format_code=format_code,
                raw_data=value,
            )

    # Parse Output File Options entries
    elif "Output File Options Preference Section" in section:
        match = re.match(r"Output File Options ID # (\d+)", key)
        if match:
            options_id = int(match.group(1))
            settings.output_file_options[options_id] = _parse_output_file_options(
                options_id, value
            )

    # Parse Output Module Preference indices
    elif "Output Module Preference Section" in section:
        if key == "Default OM Index":
            settings.output_module_prefs.default_om_index = int(_unquote(value))
        elif key == "Pre-render OM Index":
            settings.output_module_prefs.prerender_om_index = int(_unquote(value))
        elif key == "Proxy Movie OM Index":
            settings.output_module_prefs.proxy_movie_om_index = int(_unquote(value))
        elif key == "Save Current Preview OM Index":
            settings.output_module_prefs.save_preview_om_index = int(_unquote(value))
        elif key == "Still Frame OM Index":
            settings.output_module_prefs.still_frame_om_index = int(_unquote(value))

    # Parse Output Module Spec Strings
    elif "Output Module Spec Strings Section" in section:
        # Name entries: "Output Module Spec Strings Name 0" = "Lossless"
        name_match = re.match(r"Output Module Spec Strings Name (\d+)", key)
        if name_match:
            template_id = int(name_match.group(1))
            template_names[template_id] = _unquote(value)
            return

        # Base path entries: "Output Module Spec Strings Base Path 0" = ""
        base_match = re.match(r"Output Module Spec Strings Base Path (\d+)", key)
        if base_match:
            template_id = int(base_match.group(1))
            template_base_paths[template_id] = _unquote(value)
            return

        # File pattern entries: "Output Module Spec Strings File Pattern 0" = ""
        pattern_match = re.match(r"Output Module Spec Strings File Pattern (\d+)", key)
        if pattern_match:
            template_id = int(pattern_match.group(1))
            template_file_patterns[template_id] = _unquote(value)


def _parse_output_file_options(options_id: int, value: str) -> OutputFileOptions:
    """Parse output file options including embedded XML exporter parameters.

    The value contains hex-encoded data followed by embedded XML that describes
    exporter parameters for audio/video codecs and settings.

    Args:
        options_id: The options entry ID number.
        value: The raw value string containing hex data and embedded XML.

    Returns:
        An OutputFileOptions object with parsed parameters.
    """
    format_code = _extract_format_code(value)
    options = OutputFileOptions(
        id=options_id,
        format_code=format_code,
        raw_data=value,
    )

    # Decode the embedded XML if present
    xml_content = _decode_embedded_xml(value)
    if xml_content:
        options.params = _parse_exporter_params(xml_content)

        # Determine if video/audio based on parameters
        param_ids = set(options.params.keys())
        video_params = {
            "ADBEVideoCodec",
            "ADBEVideoWidth",
            "ADBEVideoHeight",
            "ADBEVideoFPS",
            "ADBEVideoFieldType",
            "ADBEVideoAspect",
        }
        audio_params = {
            "ADBEAudioCodec",
            "ADBEAudioRatePerSecond",
            "ADBEAudioNumChannels",
            "ADBEAudioSampleType",
        }
        options.video_output = bool(param_ids & video_params)
        options.output_audio = bool(param_ids & audio_params)

    return options


def _decode_embedded_xml(value: str) -> str:
    """Decode embedded XML from an output file options value.

    The XML is encoded with hex escapes in a specific format:
    - "22" = quote character (ASCII 0x22)
    - "0A" = newline (ASCII 0x0A)
    - "09" = tab (ASCII 0x09)
    - "" = empty string artifact from line continuation (should be removed)

    Args:
        value: The raw value string.

    Returns:
        The decoded XML string, or empty string if not found.
    """
    # Look for XML start marker
    xml_match = re.search(r'<\?xml', value)
    if not xml_match:
        return ""

    # Extract everything from <?xml to </PremiereData>
    xml_start = xml_match.start()
    xml_end_match = re.search(r'</PremiereData>', value[xml_start:])
    if not xml_end_match:
        return ""

    raw_xml = value[xml_start:xml_start + xml_end_match.end()]

    # First, remove empty string artifacts from line continuation
    # These appear as "" in the middle of the value
    decoded = raw_xml.replace('""', '')

    # Decode hex escapes - the format uses quoted hex values
    # "22" represents a quote character (ASCII 0x22)
    decoded = decoded.replace('"22"', '"')

    # "0A" represents newline (ASCII 0x0A)
    # "0A09" = newline + tab, "0A0909" = newline + 2 tabs, etc.
    def decode_newline_tabs(m: re.Match[str]) -> str:
        full = m.group(0)
        # Count 09 pairs after 0A
        # Format: "0A" or "0A09" or "0A0909" etc.
        tabs = (len(full) - 4) // 2  # -4 for quotes and "0A", /2 for each "09"
        return '\n' + '\t' * tabs

    decoded = re.sub(r'"0A(09)*"', decode_newline_tabs, decoded)

    return decoded


def _parse_exporter_params(xml_content: str) -> dict[str, ExporterParam]:
    """Parse exporter parameters from decoded XML.

    Args:
        xml_content: The decoded XML string.

    Returns:
        Dictionary mapping parameter identifiers to ExporterParam objects.
    """
    params: dict[str, ExporterParam] = {}

    # Use regex to extract ExporterParam elements
    # Pattern for: <ParamIdentifier>NAME</ParamIdentifier>
    # <ParamType>N</ParamType> <ParamValue>VALUE</ParamValue>
    param_pattern = re.compile(
        r'<ExporterParam[^>]*>.*?'
        r'<ParamIdentifier>([^<]+)</ParamIdentifier>.*?'
        r'<ParamType>(\d+)</ParamType>.*?'
        r'<ParamValue>([^<]*)</ParamValue>.*?'
        r'</ExporterParam>',
        re.DOTALL
    )

    for match in param_pattern.finditer(xml_content):
        identifier = match.group(1)
        param_type = int(match.group(2))
        value = match.group(3)

        # Skip numeric identifiers (these are container groups)
        if identifier.isdigit():
            continue

        params[identifier] = ExporterParam(
            identifier=identifier,
            param_type=param_type,
            value=value,
        )

    return params


def _extract_format_code(value: str) -> str:
    """Extract the 4-character format code from an Output File Info value.

    The format code appears after the initial hex data, often quoted.
    Examples: ".AVI", "oEXR", "8BPS", "png!"

    Args:
        value: The raw value string.

    Returns:
        The extracted format code, or empty string if not found.
    """
    # Look for common format codes in the value
    # They typically appear as "CODE" in the hex string
    format_patterns = [
        r'"\.AVI"',
        r'"oEXR"',
        r'"8BPS"',
        r'"png!"',
        r'"TIFF"',
        r'"wao_"',
        r'"MooV"',
        r'"AIFF"',
    ]

    for pattern in format_patterns:
        if re.search(pattern, value):
            match = re.search(pattern, value)
            if match:
                return match.group(0).strip('"')

    # Try to extract any 4-character code in quotes
    match = re.search(r'"([A-Za-z0-9_.!]{4})"', value)
    if match:
        return match.group(1)

    return ""


def _unquote(value: str) -> str:
    """Remove surrounding quotes from a value string.

    Args:
        value: The value string, possibly quoted.

    Returns:
        The unquoted string.
    """
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value
