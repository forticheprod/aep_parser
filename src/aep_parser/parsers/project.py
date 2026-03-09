from __future__ import annotations

import contextlib
import json
import os
import xml.etree.ElementTree as ET
from typing import Any, NamedTuple

from ..enums import (
    ColorManagementSystem,
    FeetFramesFilmType,
    FramesCountType,
    Label,
    LutInterpolationMethod,
    PropertyControlType,
    PropertyValueType,
    TimeDisplayType,
)
from ..kaitai import Aep
from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_list_type,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.layers.av_layer import AVLayer
from ..models.layers.layer import Layer
from ..models.project import Project
from ..models.properties.property import Property
from ..models.properties.property_group import PropertyGroup
from ..utils import deprecated
from .app import parse_app
from .item import parse_folder
from .mappings import (
    map_bits_per_channel,
    map_footage_timecode_display_start_type,
    map_gpu_accel_type,
)
from .property import parse_effect_param_defs
from .render_queue import parse_render_queue


@deprecated(
    "Use aep_parser.parse() instead, which returns an App object. "
    "Access the project via app.project."
)
def parse_project(aep_file_path: str | os.PathLike[str]) -> Project:
    """Parse an After Effects (.aep) project file.

    Warning: Deprecated
        Use [aep_parser.parse][] instead which returns an
        [App][aep_parser.models.app.App] instance.  Access the project
        via ``app.project``.

    Args:
        aep_file_path: path to the project file
    """
    file_path = os.fspath(aep_file_path)
    with Aep.from_file(file_path) as aep:
        project = _parse_project(aep, file_path)
        return parse_app(aep, project).project


def _parse_project(aep: Aep, file_path: str) -> Project:
    """Parse an After Effects (.aep) project file into a Project.

    Args:
        aep: The parsed Kaitai RIFX structure.
        file_path: Path to the ``.aep`` file (stored on the Project).
    """
    root_chunks = aep.data.chunks

    root_folder_chunk = find_by_list_type(chunks=root_chunks, list_type="Fold")
    head_chunk = find_by_type(chunks=root_chunks, chunk_type="head")
    nnhd_chunk = find_by_type(chunks=root_chunks, chunk_type="nnhd")
    acer_chunk = find_by_type(chunks=root_chunks, chunk_type="acer")
    adfr_chunk = find_by_type(chunks=root_chunks, chunk_type="adfr")
    dwga_chunk = find_by_type(chunks=root_chunks, chunk_type="dwga")
    gpug_chunk = find_by_list_type(chunks=root_chunks, list_type="gpuG")
    xmp_packet = ET.fromstring(aep.xmp_packet)

    color_profile = _get_color_profile_settings(root_chunks)

    project = Project(
        bits_per_channel=map_bits_per_channel(nnhd_chunk.bits_per_channel),
        revision=head_chunk.file_revision,
        color_management_system=ColorManagementSystem(
            int(color_profile["colorManagementSystem"])
        ),
        compensate_for_scene_referred_profiles=bool(
            acer_chunk.compensate_for_scene_referred_profiles
        ),
        effect_names=_get_effect_names(root_chunks),
        expression_engine=_get_expression_engine(root_chunks),  # CC 2019+
        feet_frames_film_type=FeetFramesFilmType.from_binary(
            nnhd_chunk.feet_frames_film_type
        ),
        lut_interpolation_method=LutInterpolationMethod(
            int(color_profile["lutInterpolationMethod"])
        ),
        ocio_configuration_file=str(color_profile["ocioConfigurationFile"]),
        file=file_path,
        footage_timecode_display_start_type=map_footage_timecode_display_start_type(
            nnhd_chunk.footage_timecode_display_start_type
        ),
        frame_rate=nnhd_chunk.frame_rate,
        frames_count_type=FramesCountType.from_binary(nnhd_chunk.frames_count_type),
        frames_use_feet_frames=nnhd_chunk.frames_use_feet_frames,
        linear_blending=any(c.chunk_type == "lnrb" for c in root_chunks),
        linearize_working_space=nnhd_chunk.linearize_working_space,
        working_gamma=dwga_chunk.working_gamma,
        working_space=_get_working_space(root_chunks),
        display_color_space=_get_display_color_space(root_chunks),
        gpu_accel_type=map_gpu_accel_type(
            str_contents(find_by_type(chunks=gpug_chunk.chunks, chunk_type="Utf8"))
        ),
        audio_sample_rate=adfr_chunk.audio_sample_rate,
        items={},
        render_queue=None,
        time_display_type=TimeDisplayType.from_binary(nnhd_chunk.time_display_type),
        transparency_grid_thumbnails=bool(nnhd_chunk.transparency_grid_thumbnails),
        xmp_packet=xmp_packet,
    )

    project._effect_param_defs = _parse_effect_definitions(root_chunks)

    root_folder = parse_folder(
        is_root=True,
        child_chunks=root_folder_chunk.chunks,
        project=project,
        item_id=0,
        item_name="root",
        label=Label(0),
        parent_folder=None,
        comment="",
    )
    project.items[0] = root_folder
    project.root_folder = root_folder

    _link_layers(project)

    project.render_queue = parse_render_queue(root_chunks, project)

    with contextlib.suppress(ChunkNotFoundError):
        fcid_chunk = find_by_type(chunks=root_chunks, chunk_type="fcid")
        project.active_item = project.items[fcid_chunk.active_item_id]

    return project


def _link_layers(project: Project) -> None:
    for composition in project.compositions:
        layers_by_id = {layer.id: layer for layer in composition.layers}
        for layer in composition.layers:
            if isinstance(layer, AVLayer) and layer._source_id != 0:
                source = project.items.get(layer._source_id)
                if source is not None:
                    layer.source = source
                    _clamp_layer_times(layer, source, composition)
                    if hasattr(source, "_used_in"):
                        source._used_in.add(composition)
            if layer._parent_id != 0:
                layer.parent = layers_by_id.get(layer._parent_id)
            _set_transform_defaults(layer)
            _set_layer_property_defaults(layer)


class _TransformSpec(NamedTuple):
    """Metadata for a standard transform property."""

    match_name: str
    name: str
    dimensions: int
    is_spatial: bool
    property_value_type: PropertyValueType


# Canonical order of transform properties as reported by ExtendScript.
# Spatial values (Anchor Point, Position, Position_0, Position_1) are
# computed from layer/comp dimensions; all others use a fixed default.
_TRANSFORM_SPECS: list[_TransformSpec] = [
    _TransformSpec("ADBE Anchor Point", "Anchor Point", 3, True, PropertyValueType.THREE_D_SPATIAL),
    _TransformSpec("ADBE Position", "Position", 3, True, PropertyValueType.THREE_D_SPATIAL),
    _TransformSpec("ADBE Position_0", "X Position", 1, False, PropertyValueType.ONE_D),
    _TransformSpec("ADBE Position_1", "Y Position", 1, False, PropertyValueType.ONE_D),
    _TransformSpec("ADBE Position_2", "Z Position", 1, False, PropertyValueType.ONE_D),
    _TransformSpec("ADBE Scale", "Scale", 3, False, PropertyValueType.THREE_D),
    _TransformSpec("ADBE Orientation", "Orientation", 3, True, PropertyValueType.THREE_D_SPATIAL),
    _TransformSpec("ADBE Rotate X", "X Rotation", 1, False, PropertyValueType.ONE_D),
    _TransformSpec("ADBE Rotate Y", "Y Rotation", 1, False, PropertyValueType.ONE_D),
    _TransformSpec("ADBE Rotate Z", "Rotation", 1, False, PropertyValueType.ONE_D),
    _TransformSpec("ADBE Opacity", "Opacity", 1, False, PropertyValueType.ONE_D),
    _TransformSpec("ADBE Envir Appear in Reflect", "Appears in Reflections", 1, False, PropertyValueType.ONE_D),
]

# Map of match_name → fixed default for standard transform properties.
# Position and Anchor Point defaults depend on layer/comp dimensions and
# are handled separately.
_TRANSFORM_FIXED_DEFAULTS: dict[str, Any] = {
    "ADBE Scale": [100.0, 100.0, 100.0],
    "ADBE Rotate X": 0.0,
    "ADBE Rotate Y": 0.0,
    "ADBE Rotate Z": 0.0,
    "ADBE Opacity": 100.0,
    "ADBE Orientation": [0.0, 0.0, 0.0],
    "ADBE Position_2": 0.0,
    "ADBE Envir Appear in Reflect": 1.0,
}


def _synthesize_property(
    spec: _TransformSpec,
    value: Any,
    default_value: Any,
) -> Property:
    """Create a `Property` for a transform entry absent from the binary.

    The property is built with neutral metadata (no keyframes, no expression,
    enabled) and the supplied *value* / *default_value*.

    Args:
        spec: Metadata describing the transform property.
        value: The current value to assign.
        default_value: The default value for `is_modified` comparison.
    """
    prop = Property(
        animated=False,
        color=False,
        dimensions_separated=False,
        dimensions=spec.dimensions,
        enabled=True,
        expression_enabled=False,
        expression="",
        integer=False,
        is_spatial=spec.is_spatial,
        keyframes=[],
        locked_ratio=False,
        match_name=spec.match_name,
        name=spec.name,
        no_value=False,
        property_control_type=PropertyControlType.UNKNOWN,
        property_depth=2,
        property_value_type=spec.property_value_type,
        value=value,
        vector=spec.dimensions > 1,
    )
    prop.default_value = default_value
    return prop


def _set_transform_defaults(layer: Layer) -> None:
    """Assign defaults and synthesize missing transform properties.

    After Effects always exposes twelve transform properties via ExtendScript
    regardless of whether the layer is 2-D or 3-D.  The binary format, however,
    only stores properties relevant to the current layer state.  This function:

    1. Sets ``default_value`` on every transform property already parsed from
       the binary so that `Property.is_modified` works correctly.
    2. Creates ``Property`` objects for any of the twelve canonical properties
       that are absent from the binary.
    3. Re-orders ``transform.properties`` to match the canonical ExtendScript
       order.

    Spatial defaults (Anchor Point, Position, and the X / Y separated followers)
    depend on layer dimensions and are computed here; all other defaults are
    fixed constants defined in ``_TRANSFORM_FIXED_DEFAULTS``.
    """
    transform = layer.transform
    if transform is None:
        return

    # Determine spatial center. For AVLayers with a linked source, width
    # and height come from the source; otherwise fall back to comp dims.
    if isinstance(layer, AVLayer):
        w = float(layer.width)
        h = float(layer.height)
    else:
        w = float(layer.containing_comp.width)
        h = float(layer.containing_comp.height)

    center_x = w / 2.0
    center_y = h / 2.0

    # Spatial defaults depend on layer dimensions.
    spatial_defaults: dict[str, Any] = {
        "ADBE Anchor Point": [center_x, center_y, 0.0],
        "ADBE Position": [center_x, center_y, 0.0],
        "ADBE Position_0": center_x,
        "ADBE Position_1": center_y,
    }

    # --- Phase 1: set default_value on properties parsed from binary --------
    existing: dict[str, Property] = {}
    for prop in transform.properties:
        if isinstance(prop, Property):
            existing[prop.match_name] = prop
            # Pad 2D Scale to 3D with Z=100 (ExtendScript always reports 3D)
            if (
                prop.match_name == "ADBE Scale"
                and isinstance(prop.value, list)
                and len(prop.value) == 2
            ):
                prop.value = prop.value + [100.0]
                prop.dimensions = 3
                prop.property_value_type = PropertyValueType.THREE_D
                for kf in prop.keyframes:
                    if isinstance(kf.value, list) and len(kf.value) == 2:
                        kf.value = kf.value + [100.0]
            if prop.default_value is not None:
                continue  # already set (e.g. by effect param defs)
            default = _TRANSFORM_FIXED_DEFAULTS.get(prop.match_name)
            if default is None:
                default = spatial_defaults.get(prop.match_name)
            if default is not None:
                # When the parser stores a vector property as a scalar
                # (e.g. Orientation parsed as 0.0 instead of [0,0,0]),
                # coerce the default to match the actual value type.
                if isinstance(default, list) and not isinstance(
                    prop.value, (list, tuple)
                ):
                    default = default[0] if default else 0.0
                prop.default_value = default

    # --- Phase 2: synthesize missing properties & reorder -------------------
    # Match names whose synthesized *value* is 0.0 (inactive separation
    # followers) while their *default* comes from spatial_defaults.
    _INACTIVE_FOLLOWER_VALUE: dict[str, float] = {
        "ADBE Position_0": 0.0,
        "ADBE Position_1": 0.0,
    }

    ordered: list[Property] = []
    for spec in _TRANSFORM_SPECS:
        if spec.match_name in existing:
            ordered.append(existing[spec.match_name])
        else:
            # Determine value and default for the synthesised property.
            default = _TRANSFORM_FIXED_DEFAULTS.get(spec.match_name)
            if default is None:
                default = spatial_defaults.get(spec.match_name)
            value: list[float] | float | None = _INACTIVE_FOLLOWER_VALUE.get(
                spec.match_name
            )
            if value is None:
                value = default
            if value is None:
                value = [0.0] * spec.dimensions if spec.dimensions > 1 else 0.0
            if default is None:
                default = value
            prop = _synthesize_property(spec, value, default)
            prop.parent_property = transform
            ordered.append(prop)

    transform.properties = ordered  # type: ignore[assignment]

    # --- Phase 3: context-dependent naming ----------------------------------
    # ExtendScript displays "ADBE Rotate Z" as "Rotation" on 2-D layers
    # and "Z Rotation" on 3-D layers.  Adjust the display name here.
    is_3d = isinstance(layer, AVLayer) and layer.three_d_layer
    if not is_3d:
        rotate_z = existing.get("ADBE Rotate Z")
        if rotate_z is None:
            # Must be a synthesized property — find it in ordered list
            for p in ordered:
                if p.match_name == "ADBE Rotate Z":
                    rotate_z = p
                    break
        if rotate_z is not None:
            rotate_z.name = "Rotation"

    # --- Phase 4: set min/max on transform properties -----------------------
    _apply_min_max_defaults(transform)


# Hardcoded min/max values that ExtendScript reports for standard properties.
# The binary does not store these; they are implicit in the AE object model.
_PROPERTY_MIN_MAX: dict[str, tuple[float, float]] = {
    # Transform
    "ADBE Opacity": (0, 100),
    # Geometry Options
    "ADBE Bevel Direction": (1, 2),
    # Material Options
    "ADBE Reflection Coefficient": (0, 100),
    "ADBE Glossiness Coefficient": (0, 100),
    "ADBE Fresnel Coefficient": (0, 100),
    "ADBE Transparency Coefficient": (0, 100),
    "ADBE Transp Rolloff": (0, 100),
    "ADBE Index of Refraction": (1, 5),
}


def _apply_min_max_defaults(group: PropertyGroup) -> None:
    """Set ``min_value`` / ``max_value`` on properties with known bounds.

    ExtendScript exposes fixed min/max on certain standard properties that
    are not stored in the binary.  This function walks all children of
    *group* and applies ``_PROPERTY_MIN_MAX`` where applicable.

    Args:
        group: The property group whose children should be updated.
    """
    for child in group.properties:
        if isinstance(child, Property):
            bounds = _PROPERTY_MIN_MAX.get(child.match_name)
            if bounds is not None:
                if child.min_value is None:
                    child.min_value = bounds[0]
                if child.max_value is None:
                    child.max_value = bounds[1]
        elif isinstance(child, PropertyGroup):
            _apply_min_max_defaults(child)


def _derive_layer_styles_enabled(layer: Layer) -> None:
    """Derive `enabled` for the Layer Styles group and Blend Options.

    ExtendScript reports the Layer Styles group as ``enabled=False`` when
    no individual style (Drop Shadow, Inner Glow, etc.) is enabled.
    Blend Options mirrors the Layer Styles group's enabled state.
    The binary stores ``enabled=True`` for both regardless.

    Args:
        layer: The layer to fix up.
    """
    for group in layer.properties:
        if not isinstance(group, PropertyGroup):
            continue
        if group.match_name != "ADBE Layer Styles":
            continue
        any_style_enabled = False
        for child in group.properties:
            if not isinstance(child, PropertyGroup):
                continue
            # Blend Options follows the parent; skip it for the check
            if child.match_name == "ADBE Blend Options Group":
                continue
            if child.enabled:
                any_style_enabled = True
                break
        group.enabled = any_style_enabled
        # Blend Options mirrors the Layer Styles group enabled state
        for child in group.properties:
            if (
                isinstance(child, PropertyGroup)
                and child.match_name == "ADBE Blend Options Group"
            ):
                child.enabled = any_style_enabled
                break
        break


def _set_layer_property_defaults(layer: Layer) -> None:
    """Apply min/max and other property defaults to all layer groups.

    Walks all top-level property groups on the layer (excluding Transform,
    which is handled by ``_set_transform_defaults``).  Also synthesizes
    missing sub-properties in standard groups (Material Options, Geometry
    Options, etc.) and missing top-level groups that ExtendScript always
    exposes.

    Args:
        layer: The layer whose properties should be updated.
    """
    # --- Synthesize missing top-level groups --------------------------------
    _synthesize_missing_top_level_groups(layer)

    # --- Synthesize missing sub-properties & apply min/max ------------------
    for group in layer.properties:
        if isinstance(group, PropertyGroup):
            if group.match_name == "ADBE Transform Group":
                continue  # already handled by _set_transform_defaults
            _synthesize_group_children(group)
            _apply_min_max_defaults(group)

    # --- Derive Layer Styles enabled from children -------------------------
    # ExtendScript reports the Layer Styles group and Blend Options as
    # enabled=False when no individual style is enabled, even though the
    # binary stores enabled=True at the group level.
    _derive_layer_styles_enabled(layer)


# ---------------------------------------------------------------------------
# Property synthesis specs
# ---------------------------------------------------------------------------

class _PropSpec(NamedTuple):
    """Metadata for a synthesized property."""

    match_name: str
    name: str
    value: Any
    pvt: PropertyValueType
    dimensions: int = 1
    is_spatial: bool = False
    color: bool = False
    min_value: float | None = None
    max_value: float | None = None


# Color min/max bounds used by Layer Styles and Material Shadow Color.
_COLOR_MIN: float = -3921568.62745098
_COLOR_MAX: float = 3921568.62745098

# Canonical children of "ADBE Material Options Group" as reported by
# ExtendScript.  Properties already parsed from binary are skipped.
_MATERIAL_SPECS: list[_PropSpec] = [
    _PropSpec("ADBE Casts Shadows", "Casts Shadows", 0.0, PropertyValueType.ONE_D),
    _PropSpec("ADBE Light Transmission", "Light Transmission", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE Accepts Shadows", "Accepts Shadows", 1.0, PropertyValueType.ONE_D),
    _PropSpec("ADBE Accepts Lights", "Accepts Lights", 1.0, PropertyValueType.ONE_D),
    _PropSpec("ADBE Shadow Color", "Shadow Color", [0.0, 0.0, 0.0, 1.0], PropertyValueType.COLOR, dimensions=4, is_spatial=True, color=True, min_value=_COLOR_MIN, max_value=_COLOR_MAX),
    _PropSpec("ADBE Appears in Reflections", "Appears in Reflections", 1.0, PropertyValueType.ONE_D),
    _PropSpec("ADBE Ambient Coefficient", "Ambient", 100.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE Diffuse Coefficient", "Diffuse", 50.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE Specular Coefficient", "Specular Intensity", 50.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE Shininess Coefficient", "Specular Shininess", 5.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE Metal Coefficient", "Metal", 100.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE Reflection Coefficient", "Reflection Intensity", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE Glossiness Coefficient", "Reflection Sharpness", 100.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE Fresnel Coefficient", "Reflection Rolloff", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE Transparency Coefficient", "Transparency", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE Transp Rolloff", "Transparency Rolloff", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE Index of Refraction", "Index of Refraction", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=5),
]

# Canonical children of "ADBE Extrsn Options Group".
_EXTRUSION_SPECS: list[_PropSpec] = [
    _PropSpec("ADBE Bevel Styles", "Bevel Style", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=4),
    _PropSpec("ADBE Bevel Direction", "Bevel Direction", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=2),
    _PropSpec("ADBE Bevel Depth", "Bevel Depth", 2.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE Hole Bevel Depth", "Hole Bevel Depth", 100.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE Extrsn Depth", "Extrusion Depth", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=10000),
]

# Canonical children of "ADBE Plane Options Group".
_PLANE_SPECS: list[_PropSpec] = [
    _PropSpec("ADBE Plane Curvature", "Curvature", 0.0, PropertyValueType.ONE_D, min_value=-100, max_value=100),
    _PropSpec("ADBE Plane Subdivision", "Segments", 4.0, PropertyValueType.ONE_D, min_value=2, max_value=256),
]

# Canonical children of "ADBE Audio Group".
_AUDIO_SPECS: list[_PropSpec] = [
    _PropSpec("ADBE Audio Levels", "Audio Levels", [0.0, 0.0], PropertyValueType.TWO_D, dimensions=2, min_value=-192, max_value=24),
]

# Canonical children of "ADBE Source Options Group".
_SOURCE_OPTIONS_SPECS: list[_PropSpec] = [
    _PropSpec("ADBE Layer Source Alternate", "Item Cache Entry", None, PropertyValueType.NO_VALUE),
]

# Mapping from group match_name to ordered list of child property specs.
_GROUP_CHILD_SPECS: dict[str, list[_PropSpec]] = {
    "ADBE Material Options Group": _MATERIAL_SPECS,
    "ADBE Extrsn Options Group": _EXTRUSION_SPECS,
    "ADBE Plane Options Group": _PLANE_SPECS,
    "ADBE Audio Group": _AUDIO_SPECS,
    "ADBE Source Options Group": _SOURCE_OPTIONS_SPECS,
}

# Canonical children for Layer Styles sub-groups.

_DROP_SHADOW_SPECS: list[_PropSpec] = [
    _PropSpec("dropShadow/mode2", "Blend Mode", 5.0, PropertyValueType.ONE_D, min_value=1, max_value=33),
    _PropSpec("dropShadow/color", "Color", [0.0, 0.0, 0.0, 1.0], PropertyValueType.COLOR, dimensions=4, is_spatial=True, color=True, min_value=_COLOR_MIN, max_value=_COLOR_MAX),
    _PropSpec("dropShadow/opacity", "Opacity", 75.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("dropShadow/useGlobalAngle", "Use Global Light", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=1),
    _PropSpec("dropShadow/localLightingAngle", "Angle", 120.0, PropertyValueType.ONE_D),
    _PropSpec("dropShadow/distance", "Distance", 5.0, PropertyValueType.ONE_D, min_value=0, max_value=30000),
    _PropSpec("dropShadow/chokeMatte", "Spread", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("dropShadow/blur", "Size", 5.0, PropertyValueType.ONE_D, min_value=0, max_value=250),
    _PropSpec("dropShadow/noise", "Noise", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("dropShadow/layerConceals", "Layer Knocks Out Drop Shadow", 1.0, PropertyValueType.ONE_D, min_value=0, max_value=1),
]

_INNER_SHADOW_SPECS: list[_PropSpec] = [
    _PropSpec("innerShadow/mode2", "Blend Mode", 5.0, PropertyValueType.ONE_D, min_value=1, max_value=33),
    _PropSpec("innerShadow/color", "Color", [0.0, 0.0, 0.0, 1.0], PropertyValueType.COLOR, dimensions=4, is_spatial=True, color=True, min_value=_COLOR_MIN, max_value=_COLOR_MAX),
    _PropSpec("innerShadow/opacity", "Opacity", 75.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("innerShadow/useGlobalAngle", "Use Global Light", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=1),
    _PropSpec("innerShadow/localLightingAngle", "Angle", 120.0, PropertyValueType.ONE_D),
    _PropSpec("innerShadow/distance", "Distance", 5.0, PropertyValueType.ONE_D, min_value=0, max_value=30000),
    _PropSpec("innerShadow/chokeMatte", "Choke", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("innerShadow/blur", "Size", 5.0, PropertyValueType.ONE_D, min_value=0, max_value=250),
    _PropSpec("innerShadow/noise", "Noise", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
]

_OUTER_GLOW_SPECS: list[_PropSpec] = [
    _PropSpec("outerGlow/mode2", "Blend Mode", 11.0, PropertyValueType.ONE_D, min_value=1, max_value=33),
    _PropSpec("outerGlow/opacity", "Opacity", 75.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("outerGlow/noise", "Noise", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("outerGlow/AEColorChoice", "Color Type", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=2),
    _PropSpec("outerGlow/color", "Color", [1.0, 1.0, 0.74509803921569, 1.0], PropertyValueType.COLOR, dimensions=4, is_spatial=True, color=True, min_value=_COLOR_MIN, max_value=_COLOR_MAX),
    _PropSpec("outerGlow/gradient", "Colors", None, PropertyValueType.NO_VALUE, is_spatial=True),
    _PropSpec("outerGlow/gradientSmoothness", "Gradient Smoothness", 100.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("outerGlow/glowTechnique", "Technique", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=2),
    _PropSpec("outerGlow/chokeMatte", "Spread", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("outerGlow/blur", "Size", 5.0, PropertyValueType.ONE_D, min_value=0, max_value=250),
    _PropSpec("outerGlow/inputRange", "Range", 50.0, PropertyValueType.ONE_D, min_value=1, max_value=100),
    _PropSpec("outerGlow/shadingNoise", "Jitter", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
]

_INNER_GLOW_SPECS: list[_PropSpec] = [
    _PropSpec("innerGlow/mode2", "Blend Mode", 11.0, PropertyValueType.ONE_D, min_value=1, max_value=33),
    _PropSpec("innerGlow/opacity", "Opacity", 75.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("innerGlow/noise", "Noise", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("innerGlow/AEColorChoice", "Color Type", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=2),
    _PropSpec("innerGlow/color", "Color", [1.0, 1.0, 0.74509803921569, 1.0], PropertyValueType.COLOR, dimensions=4, is_spatial=True, color=True, min_value=_COLOR_MIN, max_value=_COLOR_MAX),
    _PropSpec("innerGlow/gradient", "Colors", None, PropertyValueType.NO_VALUE, is_spatial=True),
    _PropSpec("innerGlow/gradientSmoothness", "Gradient Smoothness", 100.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("innerGlow/glowTechnique", "Technique", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=2),
    _PropSpec("innerGlow/innerGlowSource", "Source", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=2),
    _PropSpec("innerGlow/chokeMatte", "Choke", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("innerGlow/blur", "Size", 5.0, PropertyValueType.ONE_D, min_value=0, max_value=250),
    _PropSpec("innerGlow/inputRange", "Range", 50.0, PropertyValueType.ONE_D, min_value=1, max_value=100),
    _PropSpec("innerGlow/shadingNoise", "Jitter", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
]

_BEVEL_EMBOSS_SPECS: list[_PropSpec] = [
    _PropSpec("bevelEmboss/bevelStyle", "Style", 2.0, PropertyValueType.ONE_D, min_value=1, max_value=5),
    _PropSpec("bevelEmboss/bevelTechnique", "Technique", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=3),
    _PropSpec("bevelEmboss/strengthRatio", "Depth", 100.0, PropertyValueType.ONE_D, min_value=1, max_value=1000),
    _PropSpec("bevelEmboss/bevelDirection", "Direction", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=2),
    _PropSpec("bevelEmboss/blur", "Size", 5.0, PropertyValueType.ONE_D, min_value=0, max_value=250),
    _PropSpec("bevelEmboss/softness", "Soften", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=16),
    _PropSpec("bevelEmboss/useGlobalAngle", "Use Global Light", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=1),
    _PropSpec("bevelEmboss/localLightingAngle", "Angle", 120.0, PropertyValueType.ONE_D),
    _PropSpec("bevelEmboss/localLightingAltitude", "Altitude", 30.0, PropertyValueType.ONE_D),
    _PropSpec("bevelEmboss/highlightMode", "Highlight Mode", 11.0, PropertyValueType.ONE_D, min_value=1, max_value=33),
    _PropSpec("bevelEmboss/highlightColor", "Highlight Color", [1.0, 1.0, 1.0, 1.0], PropertyValueType.COLOR, dimensions=4, is_spatial=True, color=True, min_value=_COLOR_MIN, max_value=_COLOR_MAX),
    _PropSpec("bevelEmboss/highlightOpacity", "Highlight Opacity", 75.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("bevelEmboss/shadowMode", "Shadow Mode", 5.0, PropertyValueType.ONE_D, min_value=1, max_value=33),
    _PropSpec("bevelEmboss/shadowColor", "Shadow Color", [0.0, 0.0, 0.0, 1.0], PropertyValueType.COLOR, dimensions=4, is_spatial=True, color=True, min_value=_COLOR_MIN, max_value=_COLOR_MAX),
    _PropSpec("bevelEmboss/shadowOpacity", "Shadow Opacity", 75.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
]

_SATIN_SPECS: list[_PropSpec] = [
    _PropSpec("chromeFX/mode2", "Blend Mode", 5.0, PropertyValueType.ONE_D, min_value=1, max_value=33),
    _PropSpec("chromeFX/color", "Color", [0.0, 0.0, 0.0, 1.0], PropertyValueType.COLOR, dimensions=4, is_spatial=True, color=True, min_value=_COLOR_MIN, max_value=_COLOR_MAX),
    _PropSpec("chromeFX/opacity", "Opacity", 50.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("chromeFX/localLightingAngle", "Angle", 19.0, PropertyValueType.ONE_D),
    _PropSpec("chromeFX/distance", "Distance", 11.0, PropertyValueType.ONE_D, min_value=1, max_value=250),
    _PropSpec("chromeFX/blur", "Size", 14.0, PropertyValueType.ONE_D, min_value=0, max_value=250),
    _PropSpec("chromeFX/invert", "Invert", 1.0, PropertyValueType.ONE_D, min_value=0, max_value=1),
]

_COLOR_OVERLAY_SPECS: list[_PropSpec] = [
    _PropSpec("solidFill/mode2", "Blend Mode", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=33),
    _PropSpec("solidFill/color", "Color", [1.0, 0.0, 0.0, 1.0], PropertyValueType.COLOR, dimensions=4, is_spatial=True, color=True, min_value=_COLOR_MIN, max_value=_COLOR_MAX),
    _PropSpec("solidFill/opacity", "Opacity", 100.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
]

_GRADIENT_OVERLAY_SPECS: list[_PropSpec] = [
    _PropSpec("gradientFill/mode2", "Blend Mode", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=33),
    _PropSpec("gradientFill/opacity", "Opacity", 100.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("gradientFill/gradient", "Colors", None, PropertyValueType.NO_VALUE, is_spatial=True),
    _PropSpec("gradientFill/gradientSmoothness", "Gradient Smoothness", 100.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("gradientFill/angle", "Angle", 90.0, PropertyValueType.ONE_D),
    _PropSpec("gradientFill/type", "Style", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=5),
    _PropSpec("gradientFill/reverse", "Reverse", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=1),
    _PropSpec("gradientFill/align", "Align with Layer", 1.0, PropertyValueType.ONE_D, min_value=0, max_value=1),
    _PropSpec("gradientFill/scale", "Scale", 100.0, PropertyValueType.ONE_D, min_value=10, max_value=150),
    _PropSpec("gradientFill/offset", "Offset", [0.0, 0.0], PropertyValueType.TWO_D_SPATIAL, dimensions=2, is_spatial=True),
]

_PATTERN_OVERLAY_SPECS: list[_PropSpec] = [
    _PropSpec("patternFill/mode2", "Blend Mode", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=33),
    _PropSpec("patternFill/opacity", "Opacity", 100.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("patternFill/align", "Link with Layer", 1.0, PropertyValueType.ONE_D, min_value=0, max_value=1),
    _PropSpec("patternFill/scale", "Scale", 100.0, PropertyValueType.ONE_D, min_value=1, max_value=1000),
    _PropSpec("patternFill/phase", "Offset", [0.0, 0.0], PropertyValueType.TWO_D_SPATIAL, dimensions=2, is_spatial=True),
]

_STROKE_SPECS: list[_PropSpec] = [
    _PropSpec("frameFX/mode2", "Blend Mode", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=33),
    _PropSpec("frameFX/color", "Color", [1.0, 0.0, 0.0, 1.0], PropertyValueType.COLOR, dimensions=4, is_spatial=True, color=True, min_value=_COLOR_MIN, max_value=_COLOR_MAX),
    _PropSpec("frameFX/size", "Size", 3.0, PropertyValueType.ONE_D, min_value=1, max_value=250),
    _PropSpec("frameFX/opacity", "Opacity", 100.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("frameFX/style", "Position", 1.0, PropertyValueType.ONE_D, min_value=1, max_value=3),
]

# Blending Options has two direct properties and one sub-group.
_BLEND_OPTIONS_GLOBAL_SPECS: list[_PropSpec] = [
    _PropSpec("ADBE Global Angle2", "Global Light Angle", 120.0, PropertyValueType.ONE_D),
    _PropSpec("ADBE Global Altitude2", "Global Light Altitude", 30.0, PropertyValueType.ONE_D),
]

_ADV_BLEND_SPECS: list[_PropSpec] = [
    _PropSpec("ADBE Layer Fill Opacity2", "Fill Opacity", 100.0, PropertyValueType.ONE_D, min_value=0, max_value=100),
    _PropSpec("ADBE R Channel Blend", "Red", 1.0, PropertyValueType.ONE_D, min_value=0, max_value=1),
    _PropSpec("ADBE G Channel Blend", "Green", 1.0, PropertyValueType.ONE_D, min_value=0, max_value=1),
    _PropSpec("ADBE B Channel Blend", "Blue", 1.0, PropertyValueType.ONE_D, min_value=0, max_value=1),
    _PropSpec("ADBE Blend Interior", "Blend Interior Styles as Group", 0.0, PropertyValueType.ONE_D, min_value=0, max_value=1),
    _PropSpec("ADBE Blend Ranges", "Use Blend Ranges from Source", 1.0, PropertyValueType.ONE_D, min_value=0, max_value=1),
]

# Layer Styles sub-group specs (keyed by sub-group match name).
_LAYER_STYLE_CHILD_SPECS: dict[str, list[_PropSpec]] = {
    "dropShadow/enabled": _DROP_SHADOW_SPECS,
    "innerShadow/enabled": _INNER_SHADOW_SPECS,
    "outerGlow/enabled": _OUTER_GLOW_SPECS,
    "innerGlow/enabled": _INNER_GLOW_SPECS,
    "bevelEmboss/enabled": _BEVEL_EMBOSS_SPECS,
    "chromeFX/enabled": _SATIN_SPECS,
    "solidFill/enabled": _COLOR_OVERLAY_SPECS,
    "gradientFill/enabled": _GRADIENT_OVERLAY_SPECS,
    "patternFill/enabled": _PATTERN_OVERLAY_SPECS,
    "frameFX/enabled": _STROKE_SPECS,
}


def _make_property_from_spec(
    spec: _PropSpec,
    property_depth: int,
) -> Property:
    """Create a Property instance from a ``_PropSpec``."""
    no_value = spec.pvt == PropertyValueType.NO_VALUE
    prop = Property(
        animated=False,
        color=spec.color,
        dimensions_separated=False,
        dimensions=spec.dimensions,
        enabled=True,
        expression_enabled=False,
        expression="",
        integer=False,
        is_spatial=spec.is_spatial,
        keyframes=[],
        locked_ratio=False,
        match_name=spec.match_name,
        name=spec.name,
        no_value=no_value,
        property_control_type=PropertyControlType.UNKNOWN,
        property_depth=property_depth,
        property_value_type=spec.pvt,
        value=spec.value,
        vector=spec.dimensions > 1,
    )
    prop.default_value = spec.value
    if spec.min_value is not None:
        prop.min_value = spec.min_value
    if spec.max_value is not None:
        prop.max_value = spec.max_value
    return prop


def _synthesize_group_children(group: PropertyGroup) -> None:
    """Synthesize missing children in a standard property group.

    Checks if *group* has a known set of canonical children (Material Options,
    Geometry, Plane, Audio, or Layer Styles sub-groups) and creates any that
    are missing from the binary.  Existing properties are preserved in their
    canonical order.

    Args:
        group: The property group to fill out.
    """
    specs = _GROUP_CHILD_SPECS.get(group.match_name)
    if specs is not None:
        _fill_group(group, specs)
        return

    # Layer Styles top-level: fill Blending Options and each style sub-group.
    if group.match_name == "ADBE Layer Styles":
        for child in group.properties:
            if not isinstance(child, PropertyGroup):
                continue
            if child.match_name == "ADBE Blend Options Group":
                _fill_blend_options(child)
            else:
                child_specs = _LAYER_STYLE_CHILD_SPECS.get(child.match_name)
                if child_specs is not None:
                    _fill_group(child, child_specs)

    # Recurse into other groups that may contain known sub-groups.
    for child in group.properties:
        if isinstance(child, PropertyGroup):
            _synthesize_group_children(child)


def _fill_group(
    group: PropertyGroup,
    specs: list[_PropSpec],
) -> None:
    """Fill missing children of *group* using *specs* in canonical order."""
    existing: dict[str, Property | PropertyGroup] = {}
    for child in group.properties:
        existing[child.match_name] = child

    child_depth = group.property_depth + 1
    ordered: list[Property | PropertyGroup] = []
    for spec in specs:
        if spec.match_name in existing:
            ordered.append(existing[spec.match_name])
        else:
            prop = _make_property_from_spec(spec, child_depth)
            prop.parent_property = group
            ordered.append(prop)

    group.properties = ordered  # type: ignore[assignment]


def _fill_blend_options(group: PropertyGroup) -> None:
    """Fill Blending Options: 2 global-angle properties + Advanced Blending."""
    existing: dict[str, Property | PropertyGroup] = {}
    for child in group.properties:
        existing[child.match_name] = child

    child_depth = group.property_depth + 1
    ordered: list[Property | PropertyGroup] = []

    # Global Light Angle, Global Light Altitude
    for spec in _BLEND_OPTIONS_GLOBAL_SPECS:
        if spec.match_name in existing:
            ordered.append(existing[spec.match_name])
        else:
            prop = _make_property_from_spec(spec, child_depth)
            prop.parent_property = group
            ordered.append(prop)

    # Advanced Blending sub-group
    adv_mn = "ADBE Adv Blend Group"
    if adv_mn in existing:
        adv_group = existing[adv_mn]
        ordered.append(adv_group)
    else:
        adv_group = PropertyGroup(
            enabled=True,
            match_name=adv_mn,
            name="Advanced Blending",
            property_depth=child_depth,
            properties=[],
        )
        adv_group.parent_property = group
        ordered.append(adv_group)

    # Fill Advanced Blending children
    if isinstance(adv_group, PropertyGroup):
        _fill_group(adv_group, _ADV_BLEND_SPECS)

    group.properties = ordered  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Canonical order of top-level property groups on an AV layer.
# ---------------------------------------------------------------------------
_TOP_LEVEL_GROUP_ORDER: list[tuple[str, str]] = [
    ("ADBE Time Remapping", "Time Remap"),
    ("ADBE MTrackers", "Motion Trackers"),
    ("ADBE Mask Parade", "Masks"),
    ("ADBE Effect Parade", "Effects"),
    ("ADBE Transform Group", "Transform"),
    ("ADBE Layer Styles", "Layer Styles"),
    ("ADBE Plane Options Group", "Geometry Options"),
    ("ADBE Extrsn Options Group", "Geometry Options"),
    ("ADBE Material Options Group", "Material Options"),
    ("ADBE Audio Group", "Audio"),
    ("ADBE Data Group", "Data"),
    ("ADBE Layer Overrides", "Essential Properties"),
    ("ADBE Layer Sets", "Sets"),
    ("ADBE Source Options Group", "Replace Source"),
]


def _synthesize_missing_top_level_groups(layer: Layer) -> None:
    """Add missing top-level property groups expected by ExtendScript.

    ExtendScript always reports a fixed set of top-level property groups
    on every AV layer, even when most are empty.  The binary only stores
    groups that contain data.  This function synthesizes the missing empty
    groups and reorders all groups to match the canonical ExtendScript order.

    Args:
        layer: The layer whose property list should be filled out.
    """
    if not isinstance(layer, AVLayer):
        return

    existing: dict[str, Property | PropertyGroup] = {}
    for child in layer.properties:
        existing[child.match_name] = child

    ordered: list[Property | PropertyGroup] = []
    for match_name, name in _TOP_LEVEL_GROUP_ORDER:
        if match_name in existing:
            ordered.append(existing[match_name])
        else:
            group = PropertyGroup(
                enabled=True,
                match_name=match_name,
                name=name,
                property_depth=1,
                properties=[],
            )
            if match_name == "ADBE Layer Sets":
                group.elided = True
            group.parent_property = layer
            ordered.append(group)

    # Append any remaining properties not in the canonical list (e.g.
    # custom property groups) in their original order.
    canonical_mns = {mn for mn, _ in _TOP_LEVEL_GROUP_ORDER}
    for child in layer.properties:
        if child.match_name not in canonical_mns:
            ordered.append(child)

    # Ensure all top-level groups have the canonical depth of 1.
    for child in ordered:
        if isinstance(child, PropertyGroup) and child.match_name in canonical_mns:
            child.property_depth = 1

    layer.properties = ordered  # type: ignore[assignment]


def _clamp_layer_times(
    layer: Aep.Chunk,
    source: object,
    composition: object,
) -> None:
    """Clamp layer in/outPoint to source duration.

    After Effects clamps timing values when queried via ExtendScript:

    * ``outPoint`` is clamped to
      ``start_time + source.duration * abs(stretch / 100)`` for non-still
      footage layers where ``time_remap_enabled`` is ``False``.
    * ``inPoint`` is clamped to ``start_time`` when it falls before the
      layer's start time (positive stretch only).

    These clamps do **not** apply when ``time_remap_enabled`` is ``True``,
    since time-remapped layers have arbitrary time mapping.

    Note: ``collapse_transformation`` (continuously rasterise) does **not**
    prevent clamping — AE still clamps ``outPoint`` to the source duration.

    Args:
        layer: The layer whose timing may need clamping.
        source: The source item for the layer.
        composition: The parent composition (for frame rate).
    """
    if source is None:
        return

    # Skip still images (duration=0, no meaningful clamp)
    is_still = False
    if hasattr(source, "main_source"):
        is_still = source.main_source.is_still
    if is_still:
        return

    # Skip layers with time_remap_enabled (time remap has arbitrary mapping)
    # Note: collapse_transformation does NOT skip clamping — AE still clamps
    if getattr(layer, "time_remap_enabled", False):
        return

    source_duration = getattr(source, "duration", 0)
    if source_duration <= 0:
        return

    stretch = getattr(layer, "stretch", 100.0)

    # Skip negative stretch (reverse playback) - different clamp rules
    if stretch < 0:
        return

    frame_rate = getattr(composition, "frame_rate", 24.0)
    stretch_factor = abs(stretch / 100.0) if stretch != 0 else 1.0

    # Clamp inPoint: cannot be before start_time
    if layer.in_point < layer.start_time:
        layer.in_point = layer.start_time
        layer.frame_in_point = round(layer.start_time * frame_rate)

    # Clamp outPoint: cannot exceed start_time + source.duration * stretch
    max_out = layer.start_time + source_duration * stretch_factor
    if layer.out_point > max_out:
        layer.out_point = max_out
        layer.frame_out_point = round(max_out * frame_rate)


def _get_expression_engine(root_chunks: list[Aep.Chunk]) -> str:
    """
    Get the expression engine used in the project.

    Args:
        root_chunks (Aep.Chunk): list of root chunks of the project
    """
    try:
        expression_engine_chunk = find_by_list_type(
            chunks=root_chunks, list_type="ExEn"
        )
        utf8_chunk = find_by_type(
            chunks=expression_engine_chunk.chunks, chunk_type="Utf8"
        )
        return str_contents(utf8_chunk)
    except ChunkNotFoundError:
        return "extendscript"


def _parse_effect_definitions(
    root_chunks: list[Aep.Chunk],
) -> dict[str, dict[str, dict[str, Any]]]:
    """Parse project-level effect definitions from LIST:EfdG.

    EfdG contains parameter definitions for every effect type used in the
    project. Unlike layer-level sspc chunks, the EfdG definitions always
    include a parT chunk.

    Args:
        root_chunks: The root chunks of the AEP file.

    Returns:
        Dict mapping effect match names to their parameter definitions
        (effect_match_name -> param_match_name -> param_def dict).
    """
    try:
        efdg_chunk = find_by_list_type(chunks=root_chunks, list_type="EfdG")
    except ChunkNotFoundError:
        return {}

    effect_defs: dict[str, dict[str, dict[str, Any]]] = {}
    efdf_chunks = filter_by_list_type(chunks=efdg_chunk.chunks, list_type="EfDf")

    for efdf_chunk in efdf_chunks:
        efdf_child_chunks = efdf_chunk.chunks
        # First tdmn in EfDf contains the effect match name
        tdmn_chunk = find_by_type(chunks=efdf_child_chunks, chunk_type="tdmn")
        effect_match_name = str_contents(tdmn_chunk)

        # Parse param defs from the sspc chunk
        sspc_chunk = find_by_list_type(
            chunks=efdf_child_chunks, list_type="sspc"
        )
        param_defs = parse_effect_param_defs(sspc_chunk.chunks)
        effect_defs[effect_match_name] = param_defs

    return effect_defs


def _get_effect_names(root_chunks: list[Aep.Chunk]) -> list[str]:
    """
    Get the list of effect names used in the project.

    Args:
        root_chunks (Aep.Chunk): list of root chunks of the project
    """
    pefl_chunk = find_by_list_type(chunks=root_chunks, list_type="Pefl")
    pefl_child_chunks = pefl_chunk.chunks
    pjef_chunks = filter_by_type(chunks=pefl_child_chunks, chunk_type="pjef")
    return [str_contents(chunk) for chunk in pjef_chunks]


def _get_color_profile_settings(root_chunks: list[Aep.Chunk]) -> dict[str, int | str]:
    """
    Get color profile settings from the project.

    The settings are stored as JSON in a Utf8 chunk at the root level.

    Args:
        root_chunks: list of root chunks of the project

    Returns:
        Dict with colorManagementSystem, lutInterpolationMethod, and
        ocioConfigurationFile values.
    """
    defaults: dict[str, int | str] = {
        "colorManagementSystem": 0,  # Adobe
        "lutInterpolationMethod": 0,  # Trilinear
        "ocioConfigurationFile": "",
    }
    for chunk in filter_by_type(chunks=root_chunks, chunk_type="Utf8"):
        utf8_content = str_contents(chunk)
        if "lutInterpolationMethod" in utf8_content:
            cms_data = json.loads(utf8_content)
            # Merge with defaults so missing keys get default values
            return {**defaults, **cms_data}

    return defaults


def _get_working_space(root_chunks: list[Aep.Chunk]) -> str:
    """
    Get the working color space name from the project.

    The working space is stored in the first Utf8 chunk containing
    JSON with baseColorProfile.colorProfileName.

    Args:
        root_chunks: list of root chunks of the project

    Returns:
        The working space name (e.g., "sRGB IEC61966-2.1") or "None" if not set.
    """
    for chunk in filter_by_type(chunks=root_chunks, chunk_type="Utf8"):
        utf8_content = str_contents(chunk)
        if "baseColorProfile" in utf8_content:
            profile_data = json.loads(utf8_content)
            base_profile = profile_data.get("baseColorProfile", {})
            return str(base_profile.get("colorProfileName", "None"))
    return "None"


def _get_display_color_space(root_chunks: list[Aep.Chunk]) -> str:
    """
    Get the display color space name from the project.

    The display color space is stored in the second Utf8 chunk that
    follows the working space baseColorProfile chunk. When no display
    color space is set, the chunk contains ``{}``.

    Args:
        root_chunks: list of root chunks of the project

    Returns:
        The display color space name (e.g., "ACES/sRGB") or "None"
        if not set.
    """
    found_working_space = False
    for chunk in filter_by_type(chunks=root_chunks, chunk_type="Utf8"):
        utf8_content = str_contents(chunk)
        if not found_working_space:
            if "baseColorProfile" in utf8_content:
                found_working_space = True
            continue
        # This is the Utf8 chunk after the working space
        if "baseColorProfile" in utf8_content:
            profile_data = json.loads(utf8_content)
            base_profile = profile_data.get("baseColorProfile", {})
            return str(base_profile.get("colorProfileName", "None"))
        return "None"
    return "None"
