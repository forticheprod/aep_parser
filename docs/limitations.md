# Known Limitations

This page documents limitations of aep_parser that arise from the nature of
parsing a binary file format rather than querying a running After Effects
instance.

## Property.value_at_time Accuracy

### Spatial Properties (~0.015 Maximum Error)

`Property.value_at_time()` for spatial properties (position, 2D/3D) has a
systematic ±0.015 deviation from After Effects' `valueAtTime()`. This is
**not** a bug in the parser - it is caused by After Effects' internal spatial
evaluation pipeline.

**Evidence:** even a perfectly straight, LINEAR-interpolated path from
`[0, 50, 0]` to `[100, 50, 0]` (where the mathematically correct value is
`20 × t`) shows a sinusoidal deviation pattern in After Effects' own output,
peaking at ±0.011. The same deviation appears regardless of whether the
keyframe interpolation type is LINEAR or BEZIER.

After Effects appears to process all spatial properties through an arc-length
reparameterisation pipeline (likely a polyline or spline approximation) that
does not degrade gracefully to exact linear interpolation for straight paths.

## Runtime-Only Attributes

Many ExtendScript attributes reflect the live state of After Effects and cannot
be derived from the `.aep` file alone:

| Attribute | Reason |
|-----------|--------|
| `Application.memoryInUse` | Runtime memory state |
| `Application.isRenderEngine` | Launch mode flag |
| `Application.isWatchFolder` | Launch mode flag |
| `Application.fonts` | Installed fonts on the system |
| `Project.dirty` | Unsaved changes flag |
| `Viewer.maximized` | Window state not persisted in `.aep` |

## Expressions

### Property.value When Expressions Are Enabled

When `Property.expression_enabled` is `True`, the `value` attribute contains
the **last static or keyframed value** stored in the binary file - not the
result of evaluating the expression. After Effects computes expression results
at runtime using its expression engine; aep_parser has no expression evaluator.

```python
prop = layer.transform.property(name="ADBE Position")
if prop.expression_enabled:
    # prop.value is the pre-expression value, not the expression result
    print(prop.expression)  # the expression string is available
```

### Property.expression_error

`Property.expression_error` is always an empty string. After Effects computes
expression errors at runtime when it evaluates the expression engine; this
information is not stored in the binary `.aep` file.

## Property Metadata

### Property.default_value

Default values are set **heuristically** by the parser in `defaults.py`, not
read from the binary format. They are used for `Property.is_modified` checks.
Some default values may be inaccurate for non-standard property types.

### Property.units_text

`Property.units_text` is not read from the binary format, it is based on a
collection of samples. For some properties, the value may be an empty string
even though After Effects displays a unit string in the UI.

### Property.canSetExpression

`Property.canSetExpression` is not implemented. This attribute indicates
whether an expression can be assigned to the property. Analysis of the binary
format shows that this value is not stored in the `.aep` file. It is determined
at runtime by After Effects based on context such as the layer type (camera,
light, etc.), whether the layer is 3D, whether position dimensions are
separated, and the light type.

### Property.canVaryOverTime

`Property.can_vary_over_time` is parsed from the binary `tdb4` chunk using a
combined rule: the `can_vary_over_time` flag (byte 11 bit 1) OR the `no_value`
flag (byte 57 bit 0), since NO_VALUE properties always report
`canVaryOverTime = true` in ExtendScript. This achieves 100% accuracy across
all 800 test files, with two match-name overrides for edge cases
(`ADBE Light Falloff Type`, `ADBE FreePin3 Outlines`).

## Output Module Templates

`OutputModule.templates` and `RenderQueueItem.templates` are always empty
lists. After Effects populates them at runtime with template names from the
application preferences, but they are not stored in the `.aep` file. The actual
render settings are available through `OutputModule.settings` and
`RenderQueueItem.settings`.

## Proxy Sources

`AVItem.proxySource` and `AVItem.useProxy` are not parsed. Proxy footage
information is stored in the binary format but not yet extracted.

## Essential Properties

The Essential Graphics panel attributes are not parsed:

- `Property.alternateSource`
- `Property.canSetAlternateSource`
- `Property.essentialPropertySource`
- `CompItem.motionGraphicsTemplateName`
- `CompItem.motionGraphicsTemplateControllerCount`

## Missing Classes

The following ExtendScript classes do not exist in aep_parser:

| Class | Reason |
|-------|--------|
| `System` | OS/machine info - not stored in `.aep` |
| `ImportOptions` | Import dialog settings - not stored in `.aep` |
| `FontsObject` | Runtime collection of installed fonts |
| `CharacterRange` | Text engine range object (AE 24.6+) |
| `ComposedLineRange` | Text engine range object (AE 24.6+) |
| `ParagraphRange` | Text engine range object (AE 24.6+) |
| `ItemCollection` | Use `project.items` (Python list) instead |
| `LayerCollection` | Use `comp.layers` (Python list) instead |
| `Settings` | Application settings - methods only, not stored in `.aep` |
| `Preferences` | Application preferences - methods only, not stored in `.aep` |

## File Paths

File paths in `.aep` files are stored as they were saved on the original
system. They may be platform-specific (Windows backslashes vs. Unix forward
slashes) and may not resolve on the current system. `FileSource.file` returns
the path as stored without modification. `FileSource.missing_footage_path`
provides the path that After Effects would display for missing footage.
