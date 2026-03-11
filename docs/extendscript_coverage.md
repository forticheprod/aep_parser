# ExtendScript Coverage

Implementation progress of ExtendScript API attributes in aep_parser.

Each row shows the ratio of implemented attributes vs. the total defined in the
[After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/).
Only attributes are counted - methods are excluded.

- ✅ = all attributes implemented (100%)
- ❌ = class does not exist in aep_parser


## Summary

| Category | Implemented | Total | Progress |
|----------|------------|-------|----------|
| General | 24 | 46 | 52% |
| Items | 41 | 57 | 72% |
| Layers | 41 | 50 | 82% |
| Properties | 40 | 50 | 80% |
| Render Queue | 20 | 24 | 83% |
| Sources | 12 | 15 | 80% |
| Other | 26 | 43 | 60% |
| Text | 80 | 104 | 77% |
| **Total** | **284** | **389** | **73%** |


## General

| Class | Implemented | Total | Progress | Missing |
|-------|------------|-------|----------|---------|
| Application | 4 | 19 | 21% | `availableGPUAccelTypes`, `buildName`, `disableRendering`, `effects`, `exitAfterLaunchAndEval`, `exitCode`, `fonts`, `isoLanguage`, `isRenderEngine`, `isWatchFolder`, `memoryInUse`, `onError`, `preferences`, `saveProjectOnCrash`, `settings` |
| System | 0 | 4 | ❌ | `machineName`, `osName`, `osVersion`, `userName` |
| Project | 20 | 23 | 87% | `dirty`, `selection`, `toolType` |

Note:
    Most missing `Application` and `System` attributes reflect runtime state
    (memory usage, OS info, render engine mode) that is not stored in `.aep`
    files.


## Items

| Class | Implemented | Total | Progress | Missing |
|-------|------------|-------|----------|---------|
| Item | 6 | 9 | 67% | `dynamicLinkGUID`, `guides`, `selected` |
| AVItem | 10 | 15 | 67% | `hasAudio`, `hasVideo`, `isMediaReplacementCompatible`, `proxySource`, `useProxy` |
| CompItem | 21 | 29 | 72% | `activeCamera`, `counters`, `motionGraphicsTemplateControllerCount`, `motionGraphicsTemplateName`, `numLayers`, `renderer`, `renderers`, `selectedLayers`, `selectedProperties` |
| FolderItem | 2 | 2 | ✅ | |
| FootageItem | 2 | 2 | ✅ | |


## Layers

| Class | Implemented | Total | Progress | Missing |
|-------|------------|-------|----------|---------|
| Layer | 17 | 20 | 85% | `hasVideo`, `index`, `selectedProperties` |
| AVLayer | 23 | 28 | 82% | `audioActive`, `canSetCollapseTransformation`, `canSetTimeRemapEnabled`, `hasAudio`, `threeDPerChar` |
| CameraLayer | 0 | 0 | ✅ | |
| LightLayer | 1 | 2 | 50% | `lightSource` |
| TextLayer | 0 | 0 | ✅ | |
| ShapeLayer | 0 | 0 | ✅ | |
| ThreeDModelLayer | 0 | 0 | ❌ | |


## Properties

| Class | Implemented | Total | Progress | Missing |
|-------|------------|-------|----------|---------|
| PropertyBase | 12 | 14 | 86% | `canSetEnabled`, `propertyIndex` |
| PropertyGroup | 1 | 1 | ✅ | |
| Property | 20 | 28 | 71% | `alternateSource`, `canSetAlternateSource`, `canSetExpression`, `canVaryOverTime`, `essentialPropertySource`, `propertyIndex`, `selectedKeys`, `valueText` |
| MaskPropertyGroup | 7 | 7 | ✅ | |


## Render Queue

| Class | Implemented | Total | Progress | Missing |
|-------|------------|-------|----------|---------|
| RenderQueue | 2 | 5 | 40% | `canQueueInAME`, `queueNotify`, `rendering` |
| RenderQueueItem | 13 | 14 | 92% | `onStatusChanged` |
| OutputModule | 5 | 5 | ✅ | |


## Sources

| Class | Implemented | Total | Progress | Missing |
|-------|------------|-------|----------|---------|
| FootageSource | 9 | 12 | 75% | `displayFrameRate`, `nativeFrameRate`, `removePulldown` |
| FileSource | 2 | 2 | ✅ | |
| SolidSource | 1 | 1 | ✅ | |
| PlaceholderSource | 0 | 0 | ✅ | |


## Other

| Class | Implemented | Total | Progress | Missing |
|-------|------------|-------|----------|---------|
| Shape | 4 | 11 | 36% | `featherInterps`, `featherRadii`, `featherRelCornerAngles`, `featherRelSegLocs`, `featherSegLocs`, `featherTensions`, `featherTypes` |
| KeyframeEase | 2 | 2 | ✅ | |
| MarkerValue | 9 | 9 | ✅ | |
| ImportOptions | 0 | 6 | ❌ | `file`, `forceAlphabetical`, `importAs`, `rangeEnd`, `rangeStart`, `sequence` |
| Viewer | 4 | 5 | 80% | `maximized` |
| ViewOptions | 6 | 8 | 75% | `guidesLocked`, `guidesSnap` |
| View | 1 | 2 | 50% | `active` |


## Text

| Class | Implemented | Total | Progress | Missing |
|-------|------------|-------|----------|---------|
| TextDocument | 61 | 61 | ✅ | |
| FontObject | 19 | 20 | 95% | `otherFontsWithSameDict` |
| FontsObject | 0 | 9 | ❌ | `allFonts`, `favoriteFontFamilyList`, `fontsDuplicateByPostScriptName`, `fontServerRevision`, `fontsWithDefaultDesignAxes`, `freezeSyncSubstitutedFonts`, `missingOrSubstitutedFonts`, `mruFontFamilyList`, `substitutedFontReplacementMatchPolicy` |
| CharacterRange | 0 | 8 | ❌ | `characterEnd`, `characterStart`, `fillColor`, `isRangeValid`, `kerning`, `strokeColor`, `strokeOverFill`, `text` |
| ComposedLineRange | 0 | 3 | ❌ | `characterEnd`, `characterStart`, `isRangeValid` |
| ParagraphRange | 0 | 3 | ❌ | `characterEnd`, `characterStart`, `isRangeValid` |

Note:
    `FontsObject` is a runtime collection, not stored in `.aep` files.