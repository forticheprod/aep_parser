# ExtendScript Coverage

Implementation progress of ExtendScript API attributes in aep_parser.

Each row lists the attributes from the
[After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/)
not yet implemented.
Only attributes are counted - methods are excluded.

- ✅ = all attributes implemented
- 🚧 = partially implemented
- ❌ = class does not exist in aep_parser


## General

| Class | Status | Missing |
|-------|--------|---------|
| Application | 🚧 | `availableGPUAccelTypes`, `buildName`, `disableRendering`, `effects`, `exitAfterLaunchAndEval`, `exitCode`, `fonts`, `isoLanguage`, `isRenderEngine`, `isWatchFolder`, `memoryInUse`, `onError`, `preferences`, `saveProjectOnCrash`, `settings` |
| System | ❌ | `machineName`, `osName`, `osVersion`, `userName` |
| Project | 🚧 | `dirty`, `selection`, `toolType` |

Note:
    Most missing `Application` and `System` attributes reflect runtime state
    (memory usage, OS info, render engine mode) that is not stored in `.aep`
    files.


## Items

| Class | Status | Missing |
|-------|--------|---------|
| Item | 🚧 | `dynamicLinkGUID`, `guides`, `selected` |
| AVItem | 🚧 | `hasAudio`, `isMediaReplacementCompatible`, `proxySource`, `useProxy` |
| CompItem | 🚧 | `motionGraphicsTemplateControllerCount`, `motionGraphicsTemplateName`, `renderer`, `renderers`, `selectedLayers`, `selectedProperties` |
| FolderItem | ✅ | |
| FootageItem | ✅ | |


## Layers

| Class | Status | Missing |
|-------|--------|---------|
| Layer | 🚧 | `selectedProperties` |
| AVLayer | 🚧 | `audioActive`, `hasAudio` |
| CameraLayer | ✅ | |
| LightLayer | ✅ | |
| TextLayer | ✅ | |
| ShapeLayer | ✅ | |
| ThreeDModelLayer | ✅ | |


## Properties

| Class | Status | Missing |
|-------|--------|---------|
| PropertyBase | ✅ | |
| PropertyGroup | ✅ | |
| Property | 🚧 | `alternateSource`, `canSetAlternateSource`, `canSetExpression`, `essentialPropertySource`, `selectedKeys`, `valueText` |
| MaskPropertyGroup | ✅ | |


## Render Queue

| Class | Status | Missing |
|-------|--------|---------|
| RenderQueue | 🚧 | `canQueueInAME`, `queueNotify`, `rendering` |
| RenderQueueItem | 🚧 | `onStatusChanged` |
| OutputModule | ✅ | |


## Sources

| Class | Status | Missing |
|-------|--------|---------|
| FootageSource | 🚧 | `displayFrameRate`, `nativeFrameRate`, `removePulldown` |
| FileSource | ✅ | |
| SolidSource | ✅ | |
| PlaceholderSource | ✅ | |


## Other

| Class | Status | Missing |
|-------|--------|---------|
| Shape | ✅ | |
| KeyframeEase | ✅ | |
| MarkerValue | ✅ | |
| ImportOptions | ❌ | `file`, `forceAlphabetical`, `importAs`, `rangeEnd`, `rangeStart`, `sequence` |
| Viewer | ✅ | |
| ViewOptions | ✅ | |
| View | ✅ | |


## Text

| Class | Status | Missing |
|-------|--------|---------|
| TextDocument | ✅ | |
| FontObject | 🚧 | `otherFontsWithSameDict` |
| FontsObject | ❌ | `allFonts`, `favoriteFontFamilyList`, `fontsDuplicateByPostScriptName`, `fontServerRevision`, `fontsWithDefaultDesignAxes`, `freezeSyncSubstitutedFonts`, `missingOrSubstitutedFonts`, `mruFontFamilyList`, `substitutedFontReplacementMatchPolicy` |
| CharacterRange | ❌ | `characterEnd`, `characterStart`, `fillColor`, `isRangeValid`, `kerning`, `strokeColor`, `strokeOverFill`, `text` |
| ComposedLineRange | ❌ | `characterEnd`, `characterStart`, `isRangeValid` |
| ParagraphRange | ❌ | `characterEnd`, `characterStart`, `isRangeValid` |

Note:
    `FontsObject` is a runtime collection, not stored in `.aep` files.