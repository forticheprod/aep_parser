# Known Limitations

This page documents limitations of aep_parser that arise from the nature of
parsing a binary file format rather than querying a running After Effects
instance.

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

`Property.units_text` is parsed from the binary format for common property
types. For some properties, the value may be an empty string even though After
Effects displays a unit string in the UI.

### Property.canSetExpression / Property.canVaryOverTime

These attributes are not yet implemented. They indicate whether a property
supports expressions or keyframes, which is metadata stored in the binary
format but not yet extracted.

## Output Module Templates

`OutputModule.templates` and `RenderQueueItem.templates` contain only the
**names** of templates referenced by the render queue. Template definitions
(format settings, file paths, etc.) are stored in After Effects' application
preferences, not in the `.aep` file. The actual render settings are available
through `OutputModule.settings` and `RenderQueueItem.settings`.

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
| `ThreeDModelLayer` | 3D model layer (AE 25.0+) - has no additional attributes |
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

## Shape Feather Attributes

`Shape` (mask path) objects expose `vertices`, `inTangents`, `outTangents`, and
`closed`, but the 7 feather-related attributes (`featherInterps`,
`featherRadii`, `featherRelCornerAngles`, `featherRelSegLocs`,
`featherSegLocs`, `featherTensions`, `featherTypes`) are not parsed. Per-vertex
mask feathering data is stored in the binary format but not yet extracted.
