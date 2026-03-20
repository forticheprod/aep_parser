from __future__ import annotations

import typing

from .layer import Layer

if typing.TYPE_CHECKING:
    from aep_parser.enums import AutoOrientType, LightType

    from ...kaitai.aep import Aep  # type: ignore[attr-defined]
    from ..items.composition import CompItem
    from ..properties.property import Property
    from ..properties.property_group import PropertyGroup


class LightLayer(Layer):
    """
    The `LightLayer` object represents a light layer within a composition.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        comp = app.project.compositions[0]
        light = comp.light_layers[0]
        print(light.light_type)
        ```

    Info:
        `LightLayer` is a subclass of [Layer][] object. All methods and
        attributes of [Layer][] are available when working with `LightLayer`.

    See: https://ae-scripting.docsforadobe.dev/layer/lightlayer/
    """

    light_type: LightType
    """The type of light."""

    _light_source_id: int

    light_source: Layer | None
    """The layer used as a light source when `light_type` is
    `LightType.ENVIRONMENT`. Returns `None` if no source is assigned.

    Warning:
        Added in After Effects 24.3.
    """

    def __init__(
        self,
        *,
        _ldta: Aep.LdtaBody,
        name: str,
        comment: str,
        containing_comp: CompItem,
        properties: list[Property | PropertyGroup],
        auto_orient: AutoOrientType,
        layer_type: str,
        match_name: str,
        light_type: LightType,
        _light_source_id: int,
    ) -> None:
        super().__init__(
            _ldta=_ldta,
            name=name,
            comment=comment,
            containing_comp=containing_comp,
            properties=properties,
            auto_orient=auto_orient,
            layer_type=layer_type,
            match_name=match_name,
        )
        self.light_type = light_type
        self._light_source_id = _light_source_id
        self.light_source: Layer | None = None
