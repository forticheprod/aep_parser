/**
 * Generate Test Samples for aep_parser Model Testing
 * 
 * Creates ONE .aep file and corresponding .json export per test case.
 * 
 * Covers ALL attributes from export_project_json.jsx.
 * 
 * Usage:
 *   1. Open After Effects 2019+ (some samples need at least this version)
 *   2. Run this script: File > Scripts > Run Script File
 *   3. Select the 'models' folder in samples/
 *   4. Files will be saved to samples/models/<type>/<attribute>.aep and .json
 */

// Include export_project_json as library
var AEP_EXPORT_AS_LIBRARY = true;
#include "export_project_json.jsx"

(function() {
    "use strict";

    // Track which scene is being generated for error reporting
    var currentScene = "(init)";

    // =========================================================================
    // Utility Functions
    // =========================================================================

    function createProject(sceneName) {
        currentScene = sceneName || "(unknown)";
        if (app.project) {
            app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
        }
        return app.newProject();
    }

    /**
     * Export the current project to JSON using the export_project_json module.
     */
    function exportProjectJson(aepFilePath) {
        var jsonFilePath = aepFilePath.replace(/\.aep$/i, ".json");
        var jsonFile = new File(jsonFilePath);

        try {
            var projectData = AepExport.exportProject();
            var jsonString = JSON.stringify(projectData, null, 2);

            jsonFile.open("w");
            jsonFile.encoding = "UTF-8";
            jsonFile.write(jsonString);
            jsonFile.close();
        } catch (e) {
            $.writeln("Warning: Could not export JSON: " + e.toString());
        }
    }

    function saveProject(project, folderPath) {
        var filePath = folderPath + "/" + currentScene + ".aep";
        $.writeln("  saving: " + currentScene);
        var file = new File(filePath);
        project.save(file);
        // Export JSON
        exportProjectJson(filePath);
    }

    function ensureFolder(folderPath) {
        var folder = new Folder(folderPath);
        if (!folder.exists) {
            folder.create();
        }
        return folder;
    }

    // =========================================================================
    // Project Model Samples
    // Covers: PROJECT_ATTRS
    // Not covered (read-only): numItems, revision
    // CC 2024+ (undocumented): colorManagementSystem, lutInterpolationMethod,
    //   ocioConfigurationFile (wrapped in try-catch for older versions)
    // =========================================================================

    function generateProjectSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/project");
        var proj;

        // bitsPerChannel = 8
        proj = createProject("bitsPerChannel_8");
        proj.bitsPerChannel = 8;
        saveProject(proj, folder.fsName);

        // bitsPerChannel = 16
        proj = createProject("bitsPerChannel_16");
        // 16 bits is not supported in OCIO mode
        try {
            proj.colorManagementSystem = 0; // Adobe
        } catch (e) {}
        proj.bitsPerChannel = 16;
        saveProject(proj, folder.fsName);

        // bitsPerChannel = 32
        proj = createProject("bitsPerChannel_32");
        proj.bitsPerChannel = 32;
        saveProject(proj, folder.fsName);

        // compensateForSceneReferredProfiles (CC 2019+)
        proj = createProject("compensateForSceneReferredProfiles_true");
        proj.compensateForSceneReferredProfiles = true;
        saveProject(proj, folder.fsName);

        proj = createProject("compensateForSceneReferredProfiles_false");
        proj.compensateForSceneReferredProfiles = false;
        saveProject(proj, folder.fsName);

        // displayStartFrame
        proj = createProject("displayStartFrame_1");
        proj.displayStartFrame = 1;
        saveProject(proj, folder.fsName);

        // expressionEngine (CC 2019+)
        proj = createProject("expressionEngine_javascript");
        proj.expressionEngine = "javascript-1.0";
        saveProject(proj, folder.fsName);

        // feetFramesFilmType
        proj = createProject("feetFramesFilmType_MM35");
        proj.framesUseFeetFrames = true;
        proj.feetFramesFilmType = FeetFramesFilmType.MM35;
        saveProject(proj, folder.fsName);

        // footageTimecodeDisplayStartType
        proj = createProject("footageTimecodeDisplayStartType_source");
        proj.footageTimecodeDisplayStartType = FootageTimecodeDisplayStartType.FTCS_USE_SOURCE_MEDIA;
        saveProject(proj, folder.fsName);

        // framesCountType
        proj = createProject("framesCountType_start0");
        proj.framesCountType = FramesCountType.FC_START_0;
        saveProject(proj, folder.fsName);

        // framesUseFeetFrames
        proj = createProject("framesUseFeetFrames_true");
        proj.framesUseFeetFrames = true;
        saveProject(proj, folder.fsName);

        // linearBlending
        proj = createProject("linearBlending_true");
        proj.bitsPerChannel = 32;
        proj.linearBlending = true;
        saveProject(proj, folder.fsName);

        // linearizeWorkingSpace (CC 2019+)
        proj = createProject("linearizeWorkingSpace_true");
        proj.bitsPerChannel = 32;
        proj.linearizeWorkingSpace = true;
        saveProject(proj, folder.fsName);

        // timeDisplayType = FRAMES
        proj = createProject("timeDisplayType_frames");
        proj.timeDisplayType = TimeDisplayType.FRAMES;
        saveProject(proj, folder.fsName);

        // timeDisplayType = TIMECODE
        proj = createProject("timeDisplayType_timecode");
        proj.timeDisplayType = TimeDisplayType.TIMECODE;
        saveProject(proj, folder.fsName);

        // transparencyGridThumbnails
        proj = createProject("transparencyGridThumbnails_true");
        proj.transparencyGridThumbnails = true;
        saveProject(proj, folder.fsName);

        // workingGamma
        proj = createProject("workingGamma_2.4");
        proj.workingGamma = 2.4;
        saveProject(proj, folder.fsName);

        // workingSpace (CC 2019+)
        proj = createProject("workingSpace_sRGB");
        proj.workingSpace = "sRGB IEC61966-2.1";
        saveProject(proj, folder.fsName);

        // --- CC 2024+ Color Management Attributes ---
        // These are undocumented and only available in CC 2024+

        // colorManagementSystem = 0 (Adobe)
        proj = createProject("colorManagementSystem_adobe");
        proj.colorManagementSystem = 0;
        saveProject(proj, folder.fsName);

        // OCIO config path (relative to outputPath: samples/models)
        var ocioFile = new File(outputPath + "/../assets/config.ocio");

        // colorManagementSystem = 1 (OCIO) (CC 2024+)
        proj = createProject("colorManagementSystem_ocio");
        proj.colorManagementSystem = 1;
        proj.ocioConfigurationFile = ocioFile.fsName;
        saveProject(proj, folder.fsName);

        // lutInterpolationMethod = 0 (Trilinear)
        proj = createProject("lutInterpolationMethod_trilinear");
        proj.lutInterpolationMethod = 0;
        saveProject(proj, folder.fsName);

        // lutInterpolationMethod = 1 (Tetrahedral - requires GPU acceleration)
        proj = createProject("lutInterpolationMethod_tetrahedral");
        proj.lutInterpolationMethod = 1;
        saveProject(proj, folder.fsName);

        // ocioConfigurationFile (test with explicit custom path)
        proj = createProject("ocioConfigurationFile_custom");
        proj.colorManagementSystem = 1; // OCIO mode
        proj.ocioConfigurationFile = ocioFile.fsName;
        saveProject(proj, folder.fsName);

        // workingSpace with OCIO (uses OCIO color space names from config)
        proj = createProject("workingSpace_ocio_acescct");
        proj.colorManagementSystem = 1; // OCIO mode
        proj.ocioConfigurationFile = ocioFile.fsName;
        proj.workingSpace = "ACEScct";
        saveProject(proj, folder.fsName);

        $.writeln("Generated project samples in: " + folder.fsName);
    }

    // =========================================================================
    // Composition Model Samples
    // Covers: ITEM_ATTRS + AVITEM_ATTRS + COMPITEM_ATTRS
    // Read-only: id, typeName, numLayers, footageMissing, hasAudio, hasVideo,
    //   frameDuration, renderers, time (writable on comp)
    // =========================================================================

    function generateCompositionSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/composition");
        var proj, c;

        // --- ITEM_ATTRS ---

        // name (explicit rename after creation)
        proj = createProject("name_renamed");
        c = proj.items.addComp("OriginalName", 100, 100, 1, 1, 24);
        c.name = "RenamedComp";
        saveProject(proj, folder.fsName);

        // comment
        proj = createProject("comment");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.comment = "Test comment";
        saveProject(proj, folder.fsName);

        // label
        proj = createProject("label_5");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.label = 5;
        saveProject(proj, folder.fsName);

        // --- AVITEM_ATTRS ---

        // duration
        proj = createProject("duration_60");
        proj.items.addComp("TestComp", 100, 100, 1, 60, 24);
        saveProject(proj, folder.fsName);

        // frameRate
        proj = createProject("frameRate_30");
        proj.items.addComp("TestComp", 100, 100, 1, 1, 30);
        saveProject(proj, folder.fsName);

        proj = createProject("frameRate_23976");
        proj.items.addComp("TestComp", 100, 100, 1, 1, 23.976);
        saveProject(proj, folder.fsName);

        proj = createProject("frameRate_60");
        proj.items.addComp("TestComp", 100, 100, 1, 1, 60);
        saveProject(proj, folder.fsName);

        // height/width
        proj = createProject("size_1920x1080");
        proj.items.addComp("TestComp", 1920, 1080, 1, 1, 24);
        saveProject(proj, folder.fsName);

        proj = createProject("size_2048x872");
        proj.items.addComp("TestComp", 2048, 872, 1, 1, 24);
        saveProject(proj, folder.fsName);

        // pixelAspect
        proj = createProject("pixelAspect_0.75");
        proj.items.addComp("TestComp", 100, 100, 0.75, 1, 24);
        saveProject(proj, folder.fsName);

        proj = createProject("pixelAspect_2");
        proj.items.addComp("TestComp", 100, 100, 2.0, 1, 24);
        saveProject(proj, folder.fsName);

        // --- COMPITEM_ATTRS ---

        // bgColor
        proj = createProject("bgColor_red");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.bgColor = [1, 0, 0];
        saveProject(proj, folder.fsName);

        proj = createProject("bgColor_custom");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.bgColor = [0.2, 0.4, 0.6];
        saveProject(proj, folder.fsName);

        // displayStartFrame
        proj = createProject("displayStartFrame_100");
        c = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        c.displayStartFrame = 100;
        saveProject(proj, folder.fsName);

        // displayStartTime
        proj = createProject("displayStartTime_10");
        c = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        c.displayStartTime = 10;
        saveProject(proj, folder.fsName);

        // draft3d
        // Skipped: Does not seem to work as expected, value stays false
        // proj = createProject();
        // c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        // c.draft3d = true;
        // saveProject(proj, folder.fsName);

        // dropFrame
        proj = createProject("dropFrame_true");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 29.97);
        c.dropFrame = true;
        saveProject(proj, folder.fsName);

        proj = createProject("dropFrame_false");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 29.97);
        c.dropFrame = false;
        saveProject(proj, folder.fsName);

        // frameBlending
        proj = createProject("frameBlending_true");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.frameBlending = true;
        saveProject(proj, folder.fsName);

        // hideShyLayers
        proj = createProject("hideShyLayers_true");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.hideShyLayers = true;
        saveProject(proj, folder.fsName);

        // motionBlur
        proj = createProject("motionBlur_true");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.motionBlur = true;
        saveProject(proj, folder.fsName);

        // motionBlurAdaptiveSampleLimit
        proj = createProject("motionBlurAdaptiveSampleLimit_256");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.motionBlurAdaptiveSampleLimit = 256;
        saveProject(proj, folder.fsName);

        // motionBlurSamplesPerFrame
        proj = createProject("motionBlurSamplesPerFrame_32");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.motionBlurSamplesPerFrame = 32;
        saveProject(proj, folder.fsName);

        // preserveNestedFrameRate
        proj = createProject("preserveNestedFrameRate_true");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.preserveNestedFrameRate = true;
        saveProject(proj, folder.fsName);

        // preserveNestedResolution
        proj = createProject("preserveNestedResolution_true");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.preserveNestedResolution = true;
        saveProject(proj, folder.fsName);

        // resolutionFactor
        proj = createProject("resolutionFactor_half");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.resolutionFactor = [2, 2];
        saveProject(proj, folder.fsName);

        proj = createProject("resolutionFactor_quarter");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.resolutionFactor = [4, 4];
        saveProject(proj, folder.fsName);

        // shutterAngle
        proj = createProject("shutterAngle_180");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.shutterAngle = 180;
        saveProject(proj, folder.fsName);

        proj = createProject("shutterAngle_360");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.shutterAngle = 360;
        saveProject(proj, folder.fsName);

        // shutterPhase
        proj = createProject("shutterPhase_minus90");
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.shutterPhase = -90;
        saveProject(proj, folder.fsName);

        // workAreaStart
        proj = createProject("workAreaStart_5");
        c = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        c.workAreaStart = 5;
        saveProject(proj, folder.fsName);

        // workAreaDuration
        proj = createProject("workAreaDuration_10");
        c = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        c.workAreaDuration = 10;
        saveProject(proj, folder.fsName);

        // time
        proj = createProject("time_0");
        c = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        c.time = 0;
        saveProject(proj, folder.fsName);

        proj = createProject("time_5");
        c = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        c.time = 5;
        saveProject(proj, folder.fsName);

        proj = createProject("time_15");
        c = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        c.time = 15;
        saveProject(proj, folder.fsName);

        $.writeln("Generated composition samples in: " + folder.fsName);
    }

    // =========================================================================
    // Layer Model Samples
    // Covers: LAYER_ATTRS + AVLAYER_ATTRS + LIGHTLAYER_ATTRS
    // Read-only: index, hasVideo, id, isNameSet, nullLayer, time,
    //   audioActive, canSetCollapseTransformation, canSetTimeRemapEnabled,
    //   hasAudio, hasTrackMatte, height, isNameFromSource, isTrackMatte, width,
    //   frameBlending
    // =========================================================================

    function generateLayerSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/layer");
        var proj, comp, layer;

        // --- LAYER_ATTRS ---

        // name (explicit rename after creation)
        proj = createProject("name_renamed");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "OriginalName", 100, 100, 1);
        layer.name = "RenamedLayer";
        saveProject(proj, folder.fsName);

        // comment
        proj = createProject("comment");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.comment = "Test layer comment";
        saveProject(proj, folder.fsName);

        // enabled
        proj = createProject("enabled_false");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.enabled = false;
        saveProject(proj, folder.fsName);

        // inPoint = 5 (basic case)
        proj = createProject("inPoint_5");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.inPoint = 5;
        saveProject(proj, folder.fsName);

        // inPoint with startTime offset (tests relative time parsing)
        // startTime=10, inPoint=5 means inPoint is before startTime
        // Binary stores in_point_dividend as negative relative to startTime
        proj = createProject("inPoint_before_startTime");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 60, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.startTime = 10;
        layer.inPoint = 5;
        saveProject(proj, folder.fsName);

        // inPoint at 0 (layer visible from start)
        proj = createProject("inPoint_0");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.inPoint = 0;
        saveProject(proj, folder.fsName);

        // label
        proj = createProject("label_3");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.label = 3;
        saveProject(proj, folder.fsName);

        // locked
        proj = createProject("locked_true");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.locked = true;
        saveProject(proj, folder.fsName);

        // outPoint = 10 (basic case, within comp duration)
        proj = createProject("outPoint_10");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 60, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.outPoint = 10;
        saveProject(proj, folder.fsName);

        // outPoint at composition duration (tests clamping behavior)
        // Solid source has infinite duration, but outPoint clamps to comp duration
        proj = createProject("outPoint_at_duration");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        // Layer keeps default outPoint which equals comp duration
        saveProject(proj, folder.fsName);

        // outPoint with startTime offset
        // startTime=-5 means content starts 5 seconds before comp start
        proj = createProject("outPoint_with_negative_startTime");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.startTime = -5;
        layer.outPoint = 20;
        saveProject(proj, folder.fsName);

        // shy
        proj = createProject("shy_true");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.shy = true;
        saveProject(proj, folder.fsName);

        // solo
        proj = createProject("solo_true");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.solo = true;
        saveProject(proj, folder.fsName);

        // startTime
        proj = createProject("startTime_5");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 60, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.startTime = 5;
        saveProject(proj, folder.fsName);

        // stretch
        proj = createProject("stretch_200");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 60, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.stretch = 200;
        saveProject(proj, folder.fsName);

        proj = createProject("stretch_minus100");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 60, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.stretch = -100;
        saveProject(proj, folder.fsName);

        // --- TIMING EDGE CASES (precomp source clamping) ---
        // These test _clamp_layer_times() behaviour with precomp sources
        // that have a finite duration, activating the outPoint clamp.

        // outPoint clamped by precomp source duration
        // Precomp duration = 5s, main comp = 30s.
        // Layer outPoint defaults to main comp duration (30s) but AE clamps
        // it to start_time + source.duration = 0 + 5 = 5.
        proj = createProject("outPoint_clamp_precomp");
        comp = proj.items.addComp("MainComp", 100, 100, 1, 30, 24);
        var precomp = proj.items.addComp("Precomp5s", 100, 100, 1, 5, 24);
        layer = comp.layers.add(precomp);
        saveProject(proj, folder.fsName);

        // outPoint clamped with stretch on precomp
        // Precomp duration = 5s, stretch = 200%.
        // Effective duration = 5 * (200/100) = 10s. Layer outPoint should
        // clamp to start_time + 10 = 10.
        proj = createProject("outPoint_clamp_stretch_200");
        comp = proj.items.addComp("MainComp", 100, 100, 1, 30, 24);
        precomp = proj.items.addComp("Precomp5s", 100, 100, 1, 5, 24);
        layer = comp.layers.add(precomp);
        layer.stretch = 200;
        saveProject(proj, folder.fsName);

        // outPoint clamped with large stretch (400%)
        // Precomp duration = 5s, stretch = 400%.
        // Effective duration = 5 * 4 = 20s. OutPoint clamps to 20.
        proj = createProject("outPoint_clamp_stretch_400");
        comp = proj.items.addComp("MainComp", 100, 100, 1, 30, 24);
        precomp = proj.items.addComp("Precomp5s", 100, 100, 1, 5, 24);
        layer = comp.layers.add(precomp);
        layer.stretch = 400;
        saveProject(proj, folder.fsName);

        // collapseTransformation precomp: NO outPoint clamp
        // Precomp duration = 5s, but collapse_transformation = true means
        // AE treats it as unlimited duration.
        // Must explicitly set outPoint=30 after enabling the flag, because
        // the default outPoint when adding a precomp layer is source.duration.
        proj = createProject("outPoint_no_clamp_collapse");
        comp = proj.items.addComp("MainComp", 100, 100, 1, 30, 24);
        precomp = proj.items.addComp("Precomp5s", 100, 100, 1, 5, 24);
        layer = comp.layers.add(precomp);
        if (layer.canSetCollapseTransformation) {
            layer.collapseTransformation = true;
        }
        layer.outPoint = 30;
        saveProject(proj, folder.fsName);

        // timeRemapEnabled precomp: NO outPoint clamp
        // Precomp duration = 5s, but time_remap_enabled = true means
        // AE does not clamp outPoint.
        // Must explicitly set outPoint=30 after enabling time remap, because
        // the default outPoint when adding a precomp layer is source.duration.
        proj = createProject("outPoint_no_clamp_timeRemap");
        comp = proj.items.addComp("MainComp", 100, 100, 1, 30, 24);
        precomp = proj.items.addComp("Precomp5s", 100, 100, 1, 5, 24);
        layer = comp.layers.add(precomp);
        layer.timeRemapEnabled = true;
        layer.outPoint = 30;
        saveProject(proj, folder.fsName);

        // Negative stretch precomp: NO outPoint clamp
        // Precomp duration = 5s, stretch = -100%.
        // Negative stretch skips clamping entirely.
        proj = createProject("outPoint_no_clamp_negative_stretch");
        comp = proj.items.addComp("MainComp", 100, 100, 1, 30, 24);
        precomp = proj.items.addComp("Precomp5s", 100, 100, 1, 5, 24);
        layer = comp.layers.add(precomp);
        layer.stretch = -100;
        saveProject(proj, folder.fsName);

        // Precomp with startTime offset and outPoint clamp
        // Precomp duration = 5s, startTime = 3s.
        // OutPoint clamps to startTime + duration = 3 + 5 = 8.
        proj = createProject("outPoint_clamp_with_startTime");
        comp = proj.items.addComp("MainComp", 100, 100, 1, 30, 24);
        precomp = proj.items.addComp("Precomp5s", 100, 100, 1, 5, 24);
        layer = comp.layers.add(precomp);
        layer.startTime = 3;
        saveProject(proj, folder.fsName);

        // --- AVLAYER_ATTRS ---

        // adjustmentLayer
        proj = createProject("adjustmentLayer_true");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.adjustmentLayer = true;
        saveProject(proj, folder.fsName);

        // blendingMode
        proj = createProject("blendingMode_MULTIPLY");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.blendingMode = BlendingMode.MULTIPLY;
        saveProject(proj, folder.fsName);

        proj = createProject("blendingMode_SCREEN");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.blendingMode = BlendingMode.SCREEN;
        saveProject(proj, folder.fsName);

        proj = createProject("blendingMode_ADD");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.blendingMode = BlendingMode.ADD;
        saveProject(proj, folder.fsName);

        // collapseTransformation
        proj = createProject("collapseTransformation_true");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        var precomp = proj.items.addComp("Precomp", 100, 100, 1, 1, 24);
        layer = comp.layers.add(precomp);
        if (layer.canSetCollapseTransformation) {
            layer.collapseTransformation = true;
        }
        saveProject(proj, folder.fsName);

        // effectsActive
        proj = createProject("effectsActive_false");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.effectsActive = false;
        saveProject(proj, folder.fsName);

        // environmentLayer - requires ray-traced 3D renderer and footage layer
        // Skipped: Ray-traced 3D renderer is deprecated and has complex requirements
        // The layer must be video/still footage (not solid, shape, text, or null)
        // and the comp must use Cinema 4D or Classic 3D renderer in certain modes

        // frameBlendingType
        // Test NO_FRAME_BLEND: when frameBlending is disabled on the layer
        // This covers the regression where binary value 0 was incorrectly mapped
        proj = createProject("frameBlendingType_NO_FRAME_BLEND");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.frameBlending = true;  // Enable on comp to allow layer control
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        // Default: frameBlendingType is NO_FRAME_BLEND when layer frameBlending is off
        // layer.frameBlending is read-only and determined by frameBlendingType
        saveProject(proj, folder.fsName);

        proj = createProject("frameBlendingType_FRAME_MIX");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.frameBlending = true;
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.frameBlendingType = FrameBlendingType.FRAME_MIX;
        saveProject(proj, folder.fsName);

        proj = createProject("frameBlendingType_PIXEL_MOTION");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.frameBlending = true;
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.frameBlendingType = FrameBlendingType.PIXEL_MOTION;
        saveProject(proj, folder.fsName);

        // guideLayer
        proj = createProject("guideLayer_true");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.guideLayer = true;
        saveProject(proj, folder.fsName);

        // motionBlur
        proj = createProject("motionBlur_true");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.motionBlur = true;
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.motionBlur = true;
        saveProject(proj, folder.fsName);

        // preserveTransparency
        proj = createProject("preserveTransparency_true");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.preserveTransparency = true;
        saveProject(proj, folder.fsName);

        // quality
        proj = createProject("quality_BEST");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.quality = LayerQuality.BEST;
        saveProject(proj, folder.fsName);

        proj = createProject("quality_DRAFT");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.quality = LayerQuality.DRAFT;
        saveProject(proj, folder.fsName);

        proj = createProject("quality_WIREFRAME");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.quality = LayerQuality.WIREFRAME;
        saveProject(proj, folder.fsName);

        // samplingQuality
        proj = createProject("samplingQuality_BICUBIC");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.samplingQuality = LayerSamplingQuality.BICUBIC;
        saveProject(proj, folder.fsName);

        // threeDLayer
        proj = createProject("threeDLayer_true");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.threeDLayer = true;
        saveProject(proj, folder.fsName);

        // threeDPerChar
        // Skipped: threeDPerChar requires text animators to persist correctly
        // and the export does not include AVLayer properties for text layers
        // proj = createProject();
        // comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        // layer = comp.layers.addText("3D Per Char");
        // layer.threeDLayer = true;
        // layer.threeDPerChar = true;
        // saveProject(proj, folder.fsName);

        // timeRemapEnabled
        proj = createProject("timeRemapEnabled_true");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        precomp = proj.items.addComp("Precomp", 100, 100, 1, 5, 24);
        layer = comp.layers.add(precomp);
        layer.timeRemapEnabled = true;
        saveProject(proj, folder.fsName);

        // trackMatteType
        proj = createProject("trackMatteType_ALPHA");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        var matteLayer = comp.layers.addSolid([1, 1, 1], "MatteLayer", 100, 100, 1);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        try {
            if (typeof layer.setTrackMatte === "function") {
                layer.setTrackMatte(matteLayer, TrackMatteType.ALPHA);
            } else {
                layer.trackMatteType = TrackMatteType.ALPHA;
            }
        } catch(e) {}
        saveProject(proj, folder.fsName);

        proj = createProject("trackMatteType_LUMA");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        matteLayer = comp.layers.addSolid([1, 1, 1], "MatteLayer", 100, 100, 1);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        try {
            if (typeof layer.setTrackMatte === "function") {
                layer.setTrackMatte(matteLayer, TrackMatteType.LUMA);
            } else {
                layer.trackMatteType = TrackMatteType.LUMA;
            }
        } catch(e) {}
        saveProject(proj, folder.fsName);

        // --- Layer types ---

        // Null layer
        proj = createProject("type_null");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.layers.addNull();
        saveProject(proj, folder.fsName);

        // Text layer
        proj = createProject("type_text");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.layers.addText("TextLayer");
        saveProject(proj, folder.fsName);

        // Shape layer
        proj = createProject("type_shape");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.layers.addShape();
        saveProject(proj, folder.fsName);

        // Camera layer
        proj = createProject("type_camera");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.layers.addCamera("CameraLayer", [50, 50]);
        saveProject(proj, folder.fsName);

        // --- LIGHTLAYER_ATTRS ---

        // lightType
        proj = createProject("lightType_PARALLEL");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addLight("TestLight", [50, 50]);
        layer.lightType = LightType.PARALLEL;
        saveProject(proj, folder.fsName);

        proj = createProject("lightType_SPOT");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addLight("TestLight", [50, 50]);
        layer.lightType = LightType.SPOT;
        saveProject(proj, folder.fsName);

        proj = createProject("lightType_POINT");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addLight("TestLight", [50, 50]);
        layer.lightType = LightType.POINT;
        saveProject(proj, folder.fsName);

        proj = createProject("lightType_AMBIENT");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addLight("TestLight", [50, 50]);
        layer.lightType = LightType.AMBIENT;
        saveProject(proj, folder.fsName);

        // parent
        proj = createProject("parent");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        var parentNull = comp.layers.addNull();
        parentNull.name = "ParentNull";
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "ChildLayer", 100, 100, 1);
        layer.parent = parentNull;
        saveProject(proj, folder.fsName);

        // autoOrient
        proj = createProject("autoOrient_ALONG_PATH");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.autoOrient = AutoOrientType.ALONG_PATH;
        saveProject(proj, folder.fsName);

        proj = createProject("autoOrient_CAMERA");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.threeDLayer = true;
        layer.autoOrient = AutoOrientType.CAMERA_OR_POINT_OF_INTEREST;
        saveProject(proj, folder.fsName);

        // AutoOrientType.CHARACTERS_TOWARD_CAMERA (per-character 3D text layer only)
        proj = createProject("autoOrient_CHARACTERS");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addText("3D Text");
        layer.threeDLayer = true;
        layer.threeDPerChar = true;  // Required for CHARACTERS_TOWARD_CAMERA
        layer.autoOrient = AutoOrientType.CHARACTERS_TOWARD_CAMERA;
        saveProject(proj, folder.fsName);

        // time (comp.time affects layer.time)
        proj = createProject("time_30");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 60, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        comp.time = 30;
        saveProject(proj, folder.fsName);

        // --- audioEnabled (requires audio file) ---
        // Get assets folder path (samples/assets from samples/models)
        var modelsFolder = new Folder(outputPath);
        var samplesFolder = modelsFolder.parent;
        var wavFile = new File(samplesFolder.fsName + "/assets/wav.wav");

        // audioEnabled = true (default)
        proj = createProject("audioEnabled_true");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        var importOptions = new ImportOptions(wavFile);
        var audioFootage = proj.importFile(importOptions);
        layer = comp.layers.add(audioFootage);
        layer.audioEnabled = true;
        saveProject(proj, folder.fsName);

        // audioEnabled = false
        proj = createProject("audioEnabled_false");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        importOptions = new ImportOptions(wavFile);
        audioFootage = proj.importFile(importOptions);
        layer = comp.layers.add(audioFootage);
        layer.audioEnabled = false;
        saveProject(proj, folder.fsName);

        $.writeln("Generated layer samples in: " + folder.fsName);
    }

    // =========================================================================
    // Footage Model Samples
    // Covers: SOLID_SOURCE_ATTRS, FILE_SOURCE_ATTRS (via assets/mov_480.mov)
    // Read-only: hasAlpha, isStill, nativeFrameRate, displayFrameRate,
    //   missingFootagePath
    // =========================================================================

    // Helper to get assets folder path
    function getAssetsFolder(modelsPath) {
        // modelsPath is samples/models, assets is samples/assets
        var modelsFolder = new Folder(modelsPath);
        var samplesFolder = modelsFolder.parent;
        return samplesFolder.fsName + "/assets";
    }

    function generateFootageSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/footage");
        var proj, comp, item;

        // --- ITEM_ATTRS on FootageItem ---

        // name (rename placeholder)
        proj = createProject("name_renamed");
        item = proj.importPlaceholder("OriginalName", 100, 100, 24, 1);
        item.name = "RenamedFootage";
        saveProject(proj, folder.fsName);

        // --- SOLID_SOURCE_ATTRS ---

        // color - red
        proj = createProject("color_red");
        comp = proj.items.addComp("Container", 100, 100, 1, 1, 24);
        comp.layers.addSolid([1, 0, 0], "Solid", 100, 100, 1);
        saveProject(proj, folder.fsName);

        // color - green
        proj = createProject("color_green");
        comp = proj.items.addComp("Container", 100, 100, 1, 1, 24);
        comp.layers.addSolid([0, 1, 0], "Solid", 100, 100, 1);
        saveProject(proj, folder.fsName);

        // color - blue
        proj = createProject("color_blue");
        comp = proj.items.addComp("Container", 100, 100, 1, 1, 24);
        comp.layers.addSolid([0, 0, 1], "Solid", 100, 100, 1);
        saveProject(proj, folder.fsName);

        // color - gray
        proj = createProject("color_gray");
        comp = proj.items.addComp("Container", 100, 100, 1, 1, 24);
        comp.layers.addSolid([0.5, 0.5, 0.5], "Solid", 100, 100, 1);
        saveProject(proj, folder.fsName);

        // size - 1920x1080
        proj = createProject("size_1920x1080");
        comp = proj.items.addComp("Container", 1920, 1080, 1, 1, 24);
        comp.layers.addSolid([0.5, 0.5, 0.5], "Solid", 1920, 1080, 1);
        saveProject(proj, folder.fsName);

        // size - 3840x2160
        proj = createProject("size_3840x2160");
        comp = proj.items.addComp("Container", 3840, 2160, 1, 1, 24);
        comp.layers.addSolid([0.5, 0.5, 0.5], "Solid", 3840, 2160, 1);
        saveProject(proj, folder.fsName);

        // pixelAspect
        proj = createProject("pixelAspect_2");
        comp = proj.items.addComp("Container", 100, 100, 2, 1, 24);
        comp.layers.addSolid([0.5, 0.5, 0.5], "Solid", 100, 100, 2);
        saveProject(proj, folder.fsName);

        // --- PlaceholderSource ---

        // isStill = true
        proj = createProject("placeholder_still");
        proj.importPlaceholder("Placeholder", 1920, 1080, 24, 0);
        saveProject(proj, folder.fsName);

        // isStill = false
        proj = createProject("placeholder_movie");
        proj.importPlaceholder("Placeholder", 1920, 1080, 24, 10);
        saveProject(proj, folder.fsName);

        // Different frame rates
        proj = createProject("placeholder_30fps");
        proj.importPlaceholder("Placeholder", 1920, 1080, 30, 10);
        saveProject(proj, folder.fsName);

        proj = createProject("placeholder_60fps");
        proj.importPlaceholder("Placeholder", 1920, 1080, 60, 10);
        saveProject(proj, folder.fsName);

        // 23.976 fps footage (using mov_23_976.mov)
        proj = createProject("frameRate_23976");
        var assetsPath = getAssetsFolder(outputPath);
        var mov23976File = new File(assetsPath + "/mov_23_976.mov");
        var importOptions = new ImportOptions(mov23976File);
        var footage = proj.importFile(importOptions);
        saveProject(proj, folder.fsName);

        // Different dimensions
        proj = createProject("placeholder_720p");
        proj.importPlaceholder("Placeholder", 1280, 720, 24, 10);
        saveProject(proj, folder.fsName);

        proj = createProject("placeholder_4K");
        proj.importPlaceholder("Placeholder", 3840, 2160, 24, 10);
        saveProject(proj, folder.fsName);

        // --- FILE_SOURCE_ATTRS (using mov_480.mov) ---
        var movFile = new File(assetsPath + "/mov_480.mov");
        var alphaImageFile = new File(assetsPath + "/image_with_alpha.png");

        // alphaMode (requires footage with alpha channel)
        proj = createProject("alphaMode_STRAIGHT");
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.alphaMode = AlphaMode.STRAIGHT;
        saveProject(proj, folder.fsName);

        proj = createProject("alphaMode_PREMULTIPLIED");
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.alphaMode = AlphaMode.PREMULTIPLIED;
        saveProject(proj, folder.fsName);

        proj = createProject("alphaMode_IGNORE");
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.alphaMode = AlphaMode.IGNORE;
        saveProject(proj, folder.fsName);

        // conformFrameRate
        proj = createProject("conformFrameRate_30");
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.conformFrameRate = 30;
        saveProject(proj, folder.fsName);

        proj = createProject("conformFrameRate_24");
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.conformFrameRate = 24;
        saveProject(proj, folder.fsName);

        // fieldSeparationType
        proj = createProject("fieldSeparationType_OFF");
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.fieldSeparationType = FieldSeparationType.OFF;
        saveProject(proj, folder.fsName);

        proj = createProject("fieldSeparationType_UPPER");
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.fieldSeparationType = FieldSeparationType.UPPER_FIELD_FIRST;
        saveProject(proj, folder.fsName);

        proj = createProject("fieldSeparationType_LOWER");
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.fieldSeparationType = FieldSeparationType.LOWER_FIELD_FIRST;
        saveProject(proj, folder.fsName);

        // highQualityFieldSeparation
        proj = createProject("highQualityFieldSeparation_true");
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.fieldSeparationType = FieldSeparationType.UPPER_FIELD_FIRST;
        footage.mainSource.highQualityFieldSeparation = true;
        saveProject(proj, folder.fsName);

        // invertAlpha (requires footage with alpha channel)
        proj = createProject("invertAlpha_true");
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.invertAlpha = true;
        saveProject(proj, folder.fsName);

        // loop
        proj = createProject("loop_3");
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.loop = 3;
        saveProject(proj, folder.fsName);

        // premulColor (requires footage with alpha channel)
        proj = createProject("premulColor_red");
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.alphaMode = AlphaMode.PREMULTIPLIED;
        footage.mainSource.premulColor = [1, 0, 0];
        saveProject(proj, folder.fsName);

        proj = createProject("premulColor_black");
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.alphaMode = AlphaMode.PREMULTIPLIED;
        footage.mainSource.premulColor = [0, 0, 0];
        saveProject(proj, folder.fsName);

        // removePulldown
        proj = createProject("removePulldown_OFF");
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.removePulldown = PulldownPhase.OFF;
        saveProject(proj, folder.fsName);

        // --- Image Sequence ---
        // Tests the code path that parses frame numbers from filenames
        // Point to the first file of the sequence, AE will detect the rest
        var sequenceFile = new File(assetsPath + "/sequence_001.gif");
        proj = createProject("imageSequence_numbered");
        importOptions = new ImportOptions(sequenceFile);
        importOptions.sequence = true;
        footage = proj.importFile(importOptions);
        saveProject(proj, folder.fsName);

        $.writeln("Generated footage samples in: " + folder.fsName);
    }

    // =========================================================================
    // Folder Model Samples
    // Covers: FolderItem attributes (name, comment, label, parentFolder)
    // Read-only: id, typeName, numItems
    // =========================================================================

    function generateFolderSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/folder");
        var proj, f;

        // name (explicit rename)
        proj = createProject("name_renamed");
        f = proj.items.addFolder("OriginalName");
        f.name = "RenamedFolder";
        saveProject(proj, folder.fsName);

        // comment
        proj = createProject("comment");
        f = proj.items.addFolder("TestFolder");
        f.comment = "Folder comment";
        saveProject(proj, folder.fsName);

        // label
        proj = createProject("label_1");
        f = proj.items.addFolder("TestFolder");
        f.label = 1;
        saveProject(proj, folder.fsName);

        proj = createProject("label_5");
        f = proj.items.addFolder("TestFolder");
        f.label = 5;
        saveProject(proj, folder.fsName);

        proj = createProject("label_10");
        f = proj.items.addFolder("TestFolder");
        f.label = 10;
        saveProject(proj, folder.fsName);

        // parentFolder (nested)
        proj = createProject("parentFolder_nested");
        var root = proj.items.addFolder("RootFolder");
        var nested1 = proj.items.addFolder("Level1");
        nested1.parentFolder = root;
        var nested2 = proj.items.addFolder("Level2");
        nested2.parentFolder = nested1;
        var nested3 = proj.items.addFolder("Level3");
        nested3.parentFolder = nested2;
        saveProject(proj, folder.fsName);

        // with items (numItems)
        proj = createProject("numItems_3");
        var withItems = proj.items.addFolder("FolderWithItems");
        var c1 = proj.items.addComp("Comp1", 100, 100, 1, 1, 24);
        c1.parentFolder = withItems;
        var c2 = proj.items.addComp("Comp2", 100, 100, 1, 1, 24);
        c2.parentFolder = withItems;
        var ph = proj.importPlaceholder("Placeholder", 100, 100, 24, 1);
        ph.parentFolder = withItems;
        saveProject(proj, folder.fsName);

        // empty folder
        proj = createProject("empty");
        proj.items.addFolder("EmptyFolder");
        saveProject(proj, folder.fsName);

        $.writeln("Generated folder samples in: " + folder.fsName);
    }

    // =========================================================================
    // Marker Model Samples
    // Covers: MARKER_ATTRS (comment, chapter, url, frameTarget, cuePointName,
    //   duration, label, protectedRegion)
    // All attributes are writable
    // =========================================================================

    function generateMarkerSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/marker");
        var proj, comp, m, layer;

        // --- Comp markers ---

        // comment
        proj = createProject("comment");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.comment = "Test comment";
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName);

        // chapter
        proj = createProject("chapter");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.chapter = "Chapter 1";
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName);

        // url
        proj = createProject("url");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.url = "https://example.com";
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName);

        // frameTarget
        proj = createProject("frameTarget");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.url = "https://example.com";
        m.frameTarget = "_blank";
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName);

        // cuePointName
        proj = createProject("cuePointName");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.cuePointName = "cue_test";
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName);

        // duration
        proj = createProject("duration_5");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.duration = 5;
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName);

        // label
        proj = createProject("label_0");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.label = 0;
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName);

        proj = createProject("label_3");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.label = 3;
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName);

        proj = createProject("label_8");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.label = 8;
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName);

        // protectedRegion
        proj = createProject("protectedRegion_true");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.protectedRegion = true;
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName);

        // --- Layer markers ---

        // layer marker comment
        proj = createProject("layer_comment");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        m = new MarkerValue("LayerMarker");
        m.comment = "Layer marker comment";
        layer.marker.setValueAtTime(0, m);
        saveProject(proj, folder.fsName);

        // layer marker duration
        proj = createProject("layer_duration");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        m = new MarkerValue("LayerMarker");
        m.duration = 3;
        layer.marker.setValueAtTime(0, m);
        saveProject(proj, folder.fsName);

        // layer marker cuePointName
        proj = createProject("layer_cuePointName");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        m = new MarkerValue("LayerMarker");
        m.cuePointName = "layer_cue_1";
        layer.marker.setValueAtTime(0, m);
        saveProject(proj, folder.fsName);

        $.writeln("Generated marker samples in: " + folder.fsName);
    }

    // =========================================================================
    // Mask Model Samples
    // Covers: PropertyBase.is_mask
    // =========================================================================

    function generateMaskSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/property");
        var proj, comp, layer, maskGroup, mask, myShape;

        // is_mask = true (single mask)
        proj = createProject("is_mask_true");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        maskGroup = layer.property("ADBE Mask Parade");
        mask = maskGroup.addProperty("ADBE Mask Atom");
        myShape = new Shape();
        myShape.vertices = [[10, 10], [90, 10], [90, 90], [10, 90]];
        myShape.closed = true;
        mask.property("ADBE Mask Shape").setValue(myShape);
        saveProject(proj, folder.fsName);

        // is_mask with multiple masks
        proj = createProject("is_mask_multiple");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        maskGroup = layer.property("ADBE Mask Parade");
        mask = maskGroup.addProperty("ADBE Mask Atom");
        myShape = new Shape();
        myShape.vertices = [[10, 10], [50, 10], [50, 50], [10, 50]];
        myShape.closed = true;
        mask.property("ADBE Mask Shape").setValue(myShape);
        mask = maskGroup.addProperty("ADBE Mask Atom");
        myShape = new Shape();
        myShape.vertices = [[50, 50], [90, 50], [90, 90], [50, 90]];
        myShape.closed = true;
        mask.property("ADBE Mask Shape").setValue(myShape);
        saveProject(proj, folder.fsName);

        $.writeln("Generated mask samples in: " + folder.fsName);
    }

    // =========================================================================
    // Property Model Samples
    // Covers: Property, PropertyGroup, keyframes, expressions
    // =========================================================================

    function generatePropertySamples(outputPath) {
        var folder = ensureFolder(outputPath + "/property");
        var proj, comp, layer, prop;
        var easeIn, easeOut;

        // --- Keyframe interpolation types ---

        // LINEAR
        proj = createProject("keyframe_LINEAR");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 50]);
        prop.setValueAtTime(5, [100, 50]);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR);
        saveProject(proj, folder.fsName);

        // BEZIER
        proj = createProject("keyframe_BEZIER");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 50]);
        prop.setValueAtTime(5, [100, 50]);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        saveProject(proj, folder.fsName);

        // HOLD
        proj = createProject("keyframe_HOLD");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 100);
        prop.setValueAtTime(2, 0);
        prop.setValueAtTime(4, 100);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);
        saveProject(proj, folder.fsName);

        // --- Property types ---

        // 1D (Opacity)
        proj = createProject("property_1D_opacity");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(5, 100);
        saveProject(proj, folder.fsName);

        // 2D (Position, 2D layer)
        proj = createProject("property_2D_position");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 0]);
        prop.setValueAtTime(5, [100, 100]);
        saveProject(proj, folder.fsName);

        // 3D (Position, 3D layer)
        proj = createProject("property_3D_position");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.threeDLayer = true;
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 0, 0]);
        prop.setValueAtTime(5, [100, 100, 500]);
        saveProject(proj, folder.fsName);

        // Rotation
        proj = createProject("property_rotation");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Rotation");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(5, 360);
        saveProject(proj, folder.fsName);

        // Scale
        proj = createProject("property_scale");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Scale");
        prop.setValueAtTime(0, [100, 100]);
        prop.setValueAtTime(5, [200, 200]);
        saveProject(proj, folder.fsName);

        // --- Expressions ---

        // expression enabled
        proj = createProject("expression_enabled");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.expression = "wiggle(2, 50)";
        saveProject(proj, folder.fsName);

        // expression disabled
        proj = createProject("expression_disabled");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.expression = "50";
        prop.expressionEnabled = false;
        saveProject(proj, folder.fsName);

        // time-based expression
        proj = createProject("expression_time");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Rotation");
        prop.expression = "time * 36";
        saveProject(proj, folder.fsName);

        // --- Effects with different parameter types ---

        // Effect with 2D Point parameter (Lens Flare - Flare Center is 2D point)
        proj = createProject("effect_2dPoint");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        var effect = layer.property("Effects").addProperty("ADBE Lens Flare");
        // Flare Center is a 2D point control
        saveProject(proj, folder.fsName);

        // Effect with 3D Point parameter (3D Channel Extract - 3D Point parameter)
        // Using CC Particle World which has 3D position controls
        proj = createProject("effect_3dPoint");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.threeDLayer = true;
        // CC Sphere has 3D rotation which uses 3D controls
        effect = layer.property("Effects").addProperty("CC Sphere");
        saveProject(proj, folder.fsName);

        // Effect with nested property groups (Puppet/FreePin3)
        // Tests the tdgp property group parsing in effects (coverage gap)
        // Just applying the effect creates nested tdgp structure
        proj = createProject("effect_puppet");
        comp = proj.items.addComp("TestComp", 200, 200, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 200, 200, 1);
        // Puppet effect has nested property groups (tdgp chunks)
        effect = layer.property("Effects").addProperty("ADBE FreePin3");
        saveProject(proj, folder.fsName);

        // =================================================================
        // Keyframe interpolation & temporal ease scenarios
        // =================================================================

        // --- Bezier with symmetric ease (75% influence) on 1D ---
        proj = createProject("keyframe_bezier_ease_in_out_1D");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(5, 100);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        easeIn = new KeyframeEase(0, 75);
        easeOut = new KeyframeEase(0, 75);
        prop.setTemporalEaseAtKey(1, [easeIn], [easeOut]);
        prop.setTemporalEaseAtKey(2, [easeIn], [easeOut]);
        saveProject(proj, folder.fsName);

        // --- Bezier with asymmetric ease on 1D ---
        // Fast start (high out influence at KF1), slow end (high in influence at KF2)
        proj = createProject("keyframe_bezier_asymmetric_ease_1D");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(5, 100);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setTemporalEaseAtKey(1, [new KeyframeEase(0, 16.67)], [new KeyframeEase(0, 90)]);
        prop.setTemporalEaseAtKey(2, [new KeyframeEase(0, 90)], [new KeyframeEase(0, 16.67)]);
        saveProject(proj, folder.fsName);

        // --- Bezier with extreme ease (near 0% and 100% influence) on 1D ---
        proj = createProject("keyframe_bezier_extreme_ease_1D");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(5, 100);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setTemporalEaseAtKey(1, [new KeyframeEase(0, 0.1)], [new KeyframeEase(0, 99)]);
        prop.setTemporalEaseAtKey(2, [new KeyframeEase(0, 99)], [new KeyframeEase(0, 0.1)]);
        saveProject(proj, folder.fsName);

        // --- Multi-keyframe Bezier with varying ease per segment ---
        // 5 keyframes, each pair with different ease
        proj = createProject("keyframe_bezier_multi_ease_1D");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(2, 80);
        prop.setValueAtTime(4, 20);
        prop.setValueAtTime(7, 90);
        prop.setValueAtTime(9, 50);
        for (var ki = 1; ki <= 5; ki++) {
            prop.setInterpolationTypeAtKey(ki, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        }
        prop.setTemporalEaseAtKey(1, [new KeyframeEase(0, 33)], [new KeyframeEase(0, 33)]);
        prop.setTemporalEaseAtKey(2, [new KeyframeEase(0, 80)], [new KeyframeEase(0, 10)]);
        prop.setTemporalEaseAtKey(3, [new KeyframeEase(0, 10)], [new KeyframeEase(0, 80)]);
        prop.setTemporalEaseAtKey(4, [new KeyframeEase(0, 70)], [new KeyframeEase(0, 70)]);
        prop.setTemporalEaseAtKey(5, [new KeyframeEase(0, 16.67)], [new KeyframeEase(0, 16.67)]);
        saveProject(proj, folder.fsName);

        // --- Mixed interpolation: different in/out types per keyframe ---
        proj = createProject("keyframe_mixed_interpolation");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 100);
        prop.setValueAtTime(3, 0);
        prop.setValueAtTime(6, 100);
        prop.setValueAtTime(9, 50);
        // KF1: LINEAR out
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR);
        // KF2: BEZIER in, HOLD out
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.HOLD);
        // KF3: HOLD in, LINEAR out
        prop.setInterpolationTypeAtKey(3, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.LINEAR);
        // KF4: LINEAR in
        prop.setInterpolationTypeAtKey(4, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR);
        saveProject(proj, folder.fsName);

        // --- Single keyframe ---
        proj = createProject("keyframe_single");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(3, 75);
        saveProject(proj, folder.fsName);

        // --- 2D Position with Bezier temporal ease ---
        proj = createProject("keyframe_bezier_ease_2D_position");
        comp = proj.items.addComp("TestComp", 200, 200, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 0]);
        prop.setValueAtTime(5, [200, 200]);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setTemporalEaseAtKey(1, [new KeyframeEase(0, 70)], [new KeyframeEase(0, 70)]);
        prop.setTemporalEaseAtKey(2, [new KeyframeEase(0, 70)], [new KeyframeEase(0, 70)]);
        saveProject(proj, folder.fsName);

        // --- 2D Position with spatial Bezier tangents (curved arc) ---
        proj = createProject("keyframe_spatial_bezier_arc");
        comp = proj.items.addComp("TestComp", 200, 200, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 100]);
        prop.setValueAtTime(5, [200, 100]);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        // Arc path: outgoing tangent up, incoming tangent down
        prop.setSpatialTangentsAtKey(1, [0, 0, 0], [60, -80, 0]);
        prop.setSpatialTangentsAtKey(2, [-60, -80, 0], [0, 0, 0]);
        saveProject(proj, folder.fsName);

        // --- Multi-keyframe spatial Bezier (S-curve path) ---
        proj = createProject("keyframe_spatial_bezier_s_curve");
        comp = proj.items.addComp("TestComp", 300, 300, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [50, 250]);
        prop.setValueAtTime(3, [150, 50]);
        prop.setValueAtTime(6, [250, 250]);
        for (var si = 1; si <= 3; si++) {
            prop.setInterpolationTypeAtKey(si, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        }
        prop.setSpatialTangentsAtKey(1, [0, 0, 0], [40, -60, 0]);
        prop.setSpatialTangentsAtKey(2, [-40, -60, 0], [40, 60, 0]);
        prop.setSpatialTangentsAtKey(3, [-40, 60, 0], [0, 0, 0]);
        saveProject(proj, folder.fsName);

        // --- 3D Position with spatial Bezier tangents ---
        proj = createProject("keyframe_spatial_bezier_3D");
        comp = proj.items.addComp("TestComp", 200, 200, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.threeDLayer = true;
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 0, 0]);
        prop.setValueAtTime(5, [200, 200, -200]);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setSpatialTangentsAtKey(1, [0, 0, 0], [50, -50, -30]);
        prop.setSpatialTangentsAtKey(2, [-50, -50, 30], [0, 0, 0]);
        saveProject(proj, folder.fsName);

        // --- Spatial auto-bezier (AE auto-computes tangents) ---
        proj = createProject("keyframe_spatial_auto_bezier");
        comp = proj.items.addComp("TestComp", 300, 300, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [50, 250]);
        prop.setValueAtTime(3, [150, 50]);
        prop.setValueAtTime(6, [250, 250]);
        for (var ai = 1; ai <= 3; ai++) {
            prop.setInterpolationTypeAtKey(ai, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
            prop.setSpatialAutoBezierAtKey(ai, true);
        }
        saveProject(proj, folder.fsName);

        // --- Spatial continuous (continuous but manually set tangent) ---
        proj = createProject("keyframe_spatial_continuous");
        comp = proj.items.addComp("TestComp", 300, 300, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [50, 250]);
        prop.setValueAtTime(3, [150, 50]);
        prop.setValueAtTime(6, [250, 250]);
        for (var ci = 1; ci <= 3; ci++) {
            prop.setInterpolationTypeAtKey(ci, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
            prop.setSpatialContinuousAtKey(ci, true);
        }
        prop.setSpatialTangentsAtKey(2, [-40, -60, 0], [40, 60, 0]);
        saveProject(proj, folder.fsName);

        // --- Roving keyframes (middle KFs rove for constant-speed path) ---
        proj = createProject("keyframe_roving");
        comp = proj.items.addComp("TestComp", 300, 300, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [50, 150]);
        prop.setValueAtTime(3, [150, 50]);
        prop.setValueAtTime(6, [250, 150]);
        prop.setValueAtTime(9, [150, 250]);
        for (var ri = 1; ri <= 4; ri++) {
            prop.setInterpolationTypeAtKey(ri, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        }
        // Only middle keyframes can rove (first and last cannot)
        prop.setRovingAtKey(2, true);
        prop.setRovingAtKey(3, true);
        saveProject(proj, folder.fsName);

        // --- Temporal auto-bezier ---
        proj = createProject("keyframe_temporal_auto_bezier");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(3, 80);
        prop.setValueAtTime(6, 20);
        prop.setValueAtTime(9, 100);
        for (var ti = 1; ti <= 4; ti++) {
            prop.setInterpolationTypeAtKey(ti, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
            prop.setTemporalAutoBezierAtKey(ti, true);
        }
        saveProject(proj, folder.fsName);

        // --- Temporal continuous ---
        proj = createProject("keyframe_temporal_continuous");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(3, 80);
        prop.setValueAtTime(6, 20);
        prop.setValueAtTime(9, 100);
        for (var tci = 1; tci <= 4; tci++) {
            prop.setInterpolationTypeAtKey(tci, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
            prop.setTemporalContinuousAtKey(tci, true);
        }
        prop.setTemporalEaseAtKey(2, [new KeyframeEase(0, 60)], [new KeyframeEase(0, 60)]);
        saveProject(proj, folder.fsName);

        // --- HOLD on 2D position ---
        proj = createProject("keyframe_hold_2D_position");
        comp = proj.items.addComp("TestComp", 200, 200, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 0]);
        prop.setValueAtTime(3, [200, 0]);
        prop.setValueAtTime(6, [200, 200]);
        prop.setValueAtTime(9, [0, 200]);
        for (var hi = 1; hi <= 4; hi++) {
            prop.setInterpolationTypeAtKey(hi, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);
        }
        saveProject(proj, folder.fsName);

        // --- LINEAR on 2D position (multi-keyframe) ---
        proj = createProject("keyframe_linear_2D_position");
        comp = proj.items.addComp("TestComp", 200, 200, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 0]);
        prop.setValueAtTime(3, [200, 0]);
        prop.setValueAtTime(6, [200, 200]);
        prop.setValueAtTime(9, [0, 200]);
        for (var li = 1; li <= 4; li++) {
            prop.setInterpolationTypeAtKey(li, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR);
        }
        saveProject(proj, folder.fsName);

        // --- Bezier ease on Scale (non-spatial, per-dimension ease) ---
        // AE internally stores Scale as 3D [x, y, z] even for 2D layers
        proj = createProject("keyframe_bezier_ease_scale");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Scale");
        prop.setValueAtTime(0, [0, 0, 0]);
        prop.setValueAtTime(3, [120, 120, 120]);
        prop.setValueAtTime(6, [80, 80, 80]);
        prop.setValueAtTime(9, [100, 100, 100]);
        for (var sci = 1; sci <= 4; sci++) {
            prop.setInterpolationTypeAtKey(sci, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        }
        prop.setTemporalEaseAtKey(1,
            [new KeyframeEase(0, 33), new KeyframeEase(0, 33), new KeyframeEase(0, 33)],
            [new KeyframeEase(0, 75), new KeyframeEase(0, 75), new KeyframeEase(0, 75)]);
        prop.setTemporalEaseAtKey(2,
            [new KeyframeEase(0, 75), new KeyframeEase(0, 75), new KeyframeEase(0, 75)],
            [new KeyframeEase(0, 33), new KeyframeEase(0, 33), new KeyframeEase(0, 33)]);
        saveProject(proj, folder.fsName);

        // --- Bezier with non-zero speed (velocity at keyframe) ---
        proj = createProject("keyframe_bezier_nonzero_speed");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(3, 50);
        prop.setValueAtTime(6, 100);
        for (var spi = 1; spi <= 3; spi++) {
            prop.setInterpolationTypeAtKey(spi, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        }
        prop.setTemporalEaseAtKey(1, [new KeyframeEase(0, 33)], [new KeyframeEase(20, 33)]);
        prop.setTemporalEaseAtKey(2, [new KeyframeEase(15, 50)], [new KeyframeEase(15, 50)]);
        prop.setTemporalEaseAtKey(3, [new KeyframeEase(20, 33)], [new KeyframeEase(0, 33)]);
        saveProject(proj, folder.fsName);

        // --- Same value at all keyframes (flat line with ease) ---
        proj = createProject("keyframe_flat_value");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 50);
        prop.setValueAtTime(5, 50);
        prop.setValueAtTime(9, 50);
        for (var fi = 1; fi <= 3; fi++) {
            prop.setInterpolationTypeAtKey(fi, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        }
        saveProject(proj, folder.fsName);

        // --- Keyframes at comp boundaries (first and last frame) ---
        proj = createProject("keyframe_comp_boundaries");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 5, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(comp.duration - comp.frameDuration, 100);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setTemporalEaseAtKey(1, [new KeyframeEase(0, 50)], [new KeyframeEase(0, 50)]);
        prop.setTemporalEaseAtKey(2, [new KeyframeEase(0, 50)], [new KeyframeEase(0, 50)]);
        saveProject(proj, folder.fsName);

        // --- Keyframes only in middle (extrapolation before/after) ---
        proj = createProject("keyframe_extrapolation");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(2, 20);
        prop.setValueAtTime(7, 80);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setTemporalEaseAtKey(1, [new KeyframeEase(0, 50)], [new KeyframeEase(0, 50)]);
        prop.setTemporalEaseAtKey(2, [new KeyframeEase(0, 50)], [new KeyframeEase(0, 50)]);
        saveProject(proj, folder.fsName);

        // --- Bounce pattern (10 keyframes with progressive ease) ---
        proj = createProject("keyframe_bounce_pattern");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        var bounceValues = [0, 100, 20, 90, 30, 80, 40, 70, 45, 55];
        for (var bi = 0; bi < bounceValues.length; bi++) {
            prop.setValueAtTime(bi, bounceValues[bi]);
            prop.setInterpolationTypeAtKey(bi + 1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        }
        for (var bei = 1; bei <= bounceValues.length; bei++) {
            var inf = 16.67 + (bei * 7);
            prop.setTemporalEaseAtKey(bei,
                [new KeyframeEase(0, inf)],
                [new KeyframeEase(0, inf)]);
        }
        saveProject(proj, folder.fsName);

        // --- Color property with keyframes ---
        proj = createProject("keyframe_color");
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        var colorEffect = layer.property("Effects").addProperty("ADBE Color Control");
        prop = colorEffect.property(1);  // Color param (first and only property)
        prop.setValueAtTime(0, [1, 0, 0, 1]);    // Red
        prop.setValueAtTime(5, [0, 0, 1, 1]);    // Blue
        prop.setValueAtTime(9, [0, 1, 0, 1]);    // Green
        saveProject(proj, folder.fsName);

        // --- Separated dimensions (X/Y keyframed independently) ---
        proj = createProject("keyframe_separated_dimensions");
        comp = proj.items.addComp("TestComp", 200, 200, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("ADBE Transform Group").property("ADBE Position");
        prop.dimensionsSeparated = true;
        var xPos = layer.property("ADBE Transform Group").property("ADBE Position_0");
        var yPos = layer.property("ADBE Transform Group").property("ADBE Position_1");
        xPos.setValueAtTime(0, 0);
        xPos.setValueAtTime(5, 200);
        xPos.setValueAtTime(9, 100);
        yPos.setValueAtTime(0, 200);
        yPos.setValueAtTime(3, 0);
        yPos.setValueAtTime(9, 150);
        for (var xi = 1; xi <= 3; xi++) {
            xPos.setInterpolationTypeAtKey(xi, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        }
        xPos.setTemporalEaseAtKey(1, [new KeyframeEase(0, 70)], [new KeyframeEase(0, 70)]);
        xPos.setTemporalEaseAtKey(2, [new KeyframeEase(0, 33)], [new KeyframeEase(0, 33)]);
        for (var yi = 1; yi <= 3; yi++) {
            yPos.setInterpolationTypeAtKey(yi, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        }
        yPos.setTemporalEaseAtKey(1, [new KeyframeEase(0, 33)], [new KeyframeEase(0, 33)]);
        yPos.setTemporalEaseAtKey(2, [new KeyframeEase(0, 70)], [new KeyframeEase(0, 70)]);
        saveProject(proj, folder.fsName);

        $.writeln("Generated property samples in: " + folder.fsName);
    }

    // =========================================================================
    // Shape / Mask Path Samples
    // Covers: Shape.closed, vertices, inTangents, outTangents,
    //   featherSegLocs, featherRelSegLocs, featherRadii, featherTypes,
    //   featherInterps, featherTensions, featherRelCornerAngles
    // =========================================================================

    function generateShapeSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/property");
        var proj, comp, layer, maskGroup, mask, myShape, prop;

        // --- Mask shapes ---

        // Closed square mask (straight segments, no tangents)
        proj = createProject("shape_closed_square");
        comp = proj.items.addComp("TestComp", 400, 400, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 400, 400, 1);
        maskGroup = layer.property("ADBE Mask Parade");
        mask = maskGroup.addProperty("ADBE Mask Atom");
        myShape = new Shape();
        myShape.vertices = [[100, 100], [100, 300], [300, 300], [300, 100]];
        myShape.closed = true;
        mask.property("ADBE Mask Shape").setValue(myShape);
        saveProject(proj, folder.fsName);

        // Closed oval mask (curved bezier tangents)
        proj = createProject("shape_closed_oval");
        comp = proj.items.addComp("TestComp", 400, 400, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 400, 400, 1);
        maskGroup = layer.property("ADBE Mask Parade");
        mask = maskGroup.addProperty("ADBE Mask Atom");
        myShape = new Shape();
        myShape.vertices = [[200, 50], [100, 200], [200, 350], [300, 200]];
        myShape.inTangents = [[55.23, 0], [0, -55.23], [-55.23, 0], [0, 55.23]];
        myShape.outTangents = [[-55.23, 0], [0, 55.23], [55.23, 0], [0, -55.23]];
        myShape.closed = true;
        mask.property("ADBE Mask Shape").setValue(myShape);
        saveProject(proj, folder.fsName);

        // Open mask (not closed)
        proj = createProject("shape_open");
        comp = proj.items.addComp("TestComp", 400, 400, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 400, 400, 1);
        maskGroup = layer.property("ADBE Mask Parade");
        mask = maskGroup.addProperty("ADBE Mask Atom");
        myShape = new Shape();
        myShape.vertices = [[50, 200], [150, 50], [250, 350], [350, 200]];
        myShape.inTangents = [[0, 0], [-30, 40], [-30, -40], [0, 0]];
        myShape.outTangents = [[30, -40], [30, 40], [30, -40], [0, 0]];
        myShape.closed = false;
        mask.property("ADBE Mask Shape").setValue(myShape);
        saveProject(proj, folder.fsName);

        // Mask with variable-width feather points
        proj = createProject("shape_feather_points");
        comp = proj.items.addComp("TestComp", 400, 400, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 400, 400, 1);
        maskGroup = layer.property("ADBE Mask Parade");
        mask = maskGroup.addProperty("ADBE Mask Atom");
        myShape = new Shape();
        myShape.vertices = [[100, 100], [100, 300], [300, 300], [300, 100]];
        myShape.closed = true;
        myShape.featherSegLocs = [1, 2];
        myShape.featherRelSegLocs = [0.15, 0.5];
        myShape.featherRadii = [30, 100];
        mask.property("ADBE Mask Shape").setValue(myShape);
        saveProject(proj, folder.fsName);

        // Mask with feather points including inner feather and hold interpolation
        proj = createProject("shape_feather_inner_hold");
        comp = proj.items.addComp("TestComp", 400, 400, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 400, 400, 1);
        maskGroup = layer.property("ADBE Mask Parade");
        mask = maskGroup.addProperty("ADBE Mask Atom");
        myShape = new Shape();
        myShape.vertices = [[100, 100], [100, 300], [300, 300], [300, 100]];
        myShape.closed = true;
        myShape.featherSegLocs = [0, 1, 2, 3];
        myShape.featherRelSegLocs = [0.5, 0.5, 0.5, 0.5];
        myShape.featherRadii = [50, -30, 80, -20];
        myShape.featherTypes = [0, 1, 0, 1];
        myShape.featherInterps = [0, 0, 1, 1];
        myShape.featherTensions = [0, 0.5, 1.0, 0.25];
        mask.property("ADBE Mask Shape").setValue(myShape);
        saveProject(proj, folder.fsName);

        // Animated mask shape (two keyframes)
        proj = createProject("shape_animated");
        comp = proj.items.addComp("TestComp", 400, 400, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 400, 400, 1);
        maskGroup = layer.property("ADBE Mask Parade");
        mask = maskGroup.addProperty("ADBE Mask Atom");
        var shape1 = new Shape();
        shape1.vertices = [[100, 100], [100, 300], [300, 300], [300, 100]];
        shape1.closed = true;
        var shape2 = new Shape();
        shape2.vertices = [[150, 150], [150, 250], [250, 250], [250, 150]];
        shape2.closed = true;
        prop = mask.property("ADBE Mask Shape");
        prop.setValueAtTime(0, shape1);
        prop.setValueAtTime(5, shape2);
        saveProject(proj, folder.fsName);

        // Mask with many vertices (>255) to verify seg_loc field width
        proj = createProject("shape_many_points");
        comp = proj.items.addComp("TestComp", 4000, 4000, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 4000, 4000, 1);
        maskGroup = layer.property("ADBE Mask Parade");
        mask = maskGroup.addProperty("ADBE Mask Atom");
        myShape = new Shape();
        var verts = [];
        var numVerts = 300;
        var cx = 2000, cy = 2000, r = 1500;
        for (var i = 0; i < numVerts; i++) {
            var angle = (i / numVerts) * 2 * Math.PI;
            verts.push([cx + r * Math.cos(angle), cy + r * Math.sin(angle)]);
        }
        myShape.vertices = verts;
        myShape.closed = true;
        // Place feather points on segments beyond index 255
        myShape.featherSegLocs = [0, 128, 255, 256, 270, 299];
        myShape.featherRelSegLocs = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5];
        myShape.featherRadii = [10, 20, 30, 40, 50, 60];
        mask.property("ADBE Mask Shape").setValue(myShape);
        saveProject(proj, folder.fsName);

        // --- Shape layer path ---

        // Shape layer with a rectangle path
        proj = createProject("shape_layer_path");
        comp = proj.items.addComp("TestComp", 400, 400, 1, 10, 24);
        var shapeLayer = comp.layers.addShape();
        var contents = shapeLayer.property("ADBE Root Vectors Group");
        var shapeGroup = contents.addProperty("ADBE Vector Group");
        var vectors = shapeGroup.property("ADBE Vectors Group");
        var pathProp = vectors.addProperty("ADBE Vector Shape - Group");
        var path = pathProp.property("ADBE Vector Shape");
        myShape = new Shape();
        myShape.vertices = [[50, 50], [50, 350], [350, 350], [350, 50]];
        myShape.closed = true;
        path.setValue(myShape);
        saveProject(proj, folder.fsName);

        $.writeln("Generated shape samples in: " + folder.fsName);
    }

    // =========================================================================
    // RenderQueue Model Samples
    // Covers: RenderQueue, RenderQueueItem, OutputModule
    // Generates all render_queue *.aep samples
    // =========================================================================

    /**
     * Helper to create a basic project with a comp and render queue item.
     * @param {string} compName - The name for the composition
     * @param {number} [width=1920] - Composition width
     * @param {number} [height=1080] - Composition height
     * @param {number} [duration=30] - Duration in seconds
     * @param {number} [frameRate=24] - Frame rate
     * @returns {{proj: Project, comp: CompItem, rqItem: RenderQueueItem, om: OutputModule}}
     */
    function createRenderQueueProject(compName, width, height, duration, frameRate, sceneName) {
        var proj = createProject(sceneName || compName || "render_queue");
        var comp = proj.items.addComp(
            compName || "Comp 1",
            width || 1920,
            height || 1080,
            1,
            duration || 30,
            frameRate || 24
        );
        comp.bgColor = [0.2, 0.4, 0.6];  // Set a distinctive background color
        var rqItem = proj.renderQueue.items.add(comp);
        var om = rqItem.outputModule(1);
        return {proj: proj, comp: comp, rqItem: rqItem, om: om};
    }

    /**
     * Apply render settings template or custom settings.
     * @param {RenderQueueItem} rqItem - The render queue item
     * @param {string} [template] - Template name to apply (optional)
     * @param {Object} [settings] - Custom settings to apply after template
     */
    function applyRenderSettings(rqItem, template, settings) {
        if (template) {
            try {
                rqItem.applyTemplate(template);
            } catch (e) {
                $.writeln("  Warning: Could not apply template '" + template + "': " + e.toString());
            }
        }
        if (settings) {
            try {
                rqItem.setSettings(settings);
            } catch (e) {
                $.writeln("  Warning: Could not apply settings: " + e.toString());
            }
        }
    }

    /**
     * Apply output module template or custom settings.
     *
     * WARNING: There is a bug that causes OutputModule objects to be invalidated
     * after the output module settings are modified. This function retrieves
     * the OutputModule fresh after modification and returns it.
     *
     * @param {RenderQueueItem} rqItem - The render queue item containing the output module
     * @param {string} [template] - Template name to apply (optional)
     * @param {Object} [settings] - Custom settings to apply after template
     * @param {number} [omIndex=1] - Index of the output module (1-based, default 1)
     * @returns {OutputModule} - The fresh OutputModule reference after modification
     */
    function applyOutputModuleSettings(rqItem, template, settings, omIndex) {
        omIndex = omIndex || 1;
        var om = rqItem.outputModule(omIndex);
        if (template) {
            try {
                om.applyTemplate(template);
                // Re-fetch OutputModule after template application (bug workaround)
                om = rqItem.outputModule(omIndex);
            } catch (e) {
                $.writeln("  Warning: Could not apply OM template '" + template + "': " + e.toString());
            }
        }
        if (settings) {
            try {
                om.setSettings(settings);
                // Re-fetch OutputModule after settings modification (bug workaround)
                om = rqItem.outputModule(omIndex);
            } catch (e) {
                $.writeln("  Warning: Could not apply OM settings: " + e.toString());
            }
        }
        return om;
    }

    function generateRenderQueueSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/renderqueue");
        var p, downloadFolder;

        // Get user's Downloads folder for output paths
        try {
            downloadFolder = Folder.myDocuments.parent.fsName + "/Downloads";
        } catch (e) {
            downloadFolder = folder.fsName;
        }

        // -----------------------------------------------------------------
        // base.aep - Base render settings (Best quality, Full resolution)
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/Comp 1.mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // current_settings.aep - Use current comp settings
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Current Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // custom.aep - Custom render settings
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Color Depth samples
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Color Depth": 0});  // 8 bits
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Color Depth": 1});  // 16 bits
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Color Depth": 2});  // 32 bits
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Quality samples
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Quality": -1});  // Current
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Quality": 1});  // Draft
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Quality": 0});  // Wireframe
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Resolution samples
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Resolution": {x: 0, y: 0}});  // Current
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Resolution": {x: 2, y: 2}});  // Half
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Resolution": {x: 3, y: 3}});  // Third
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Resolution": {x: 4, y: 4}});  // Quarter
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Resolution": {x: 7, y: 3}});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Resolution": {x: 7, y: 4}});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Resolution": {x: 8, y: 3}});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Effects samples
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Effects": 0});  // All Off
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Effects": 1});  // All On
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Proxy Use samples
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Proxy Use": 2});  // Current Settings
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Proxy Use": 1});  // Use All Proxies
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Proxy Use": 3});  // Use Comp Proxies Only
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Solo Switches samples
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Solo Switches": 0});  // All Off
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Disk Cache sample
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Disk Cache": 2});  // Current Settings
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Motion Blur samples
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Motion Blur": 2});  // Current Settings
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Motion Blur": 0});  // Off for All Layers
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Frame Blending samples
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Frame Blending": 2});  // Current Settings
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Frame Blending": 0});  // Off for All Layers
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Field Render samples
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Field Render": 2});  // Lower Field First
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Field Render": 1});  // Upper Field First
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // Field render with pulldown options (Upper Field First with 3:2 pulldown)
        // Pulldown values: 1=WSSWW, 2=SSWWW, 3=SWWWS, 4=WWWSS, 5=WWSSW
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Field Render": 1, "3:2 Pulldown": 2});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Field Render": 1, "3:2 Pulldown": 3});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Field Render": 1, "3:2 Pulldown": 1});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Field Render": 1, "3:2 Pulldown": 5});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Field Render": 1, "3:2 Pulldown": 4});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Guide Layers samples
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Guide Layers": 2});  // Current Settings
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Time Span samples
        // -----------------------------------------------------------------
        // Length of Comp (Time Span = 0)
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Time Span": 0, "Frame Rate": 1, "Use this frame rate": 30});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {
            "Time Span Start": 0,
            "Time Span Duration": 30
        });
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // Custom time span: start=0, duration=24s 13f (24.541667s at 24fps)
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {
            "Time Span Start": 0,
            "Time Span Duration": 24 + 13/24  // 24s 13f
        });
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // Custom time span: start=1s 23f, duration=24s 13f
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {
            "Time Span Start": 1 + 23/24,  // 1s 23f
            "Time Span Duration": 24 + 13/24  // 24s 13f
        });
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Frame Rate samples
        // Note: "Frame Rate" is the boolean flag (0=comp rate, 1=custom rate)
        // "Use this frame rate" is the actual fps value when custom is enabled
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Frame Rate": 1, "Use this frame rate": 24});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Frame Rate": 1, "Use this frame rate": 30});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Frame Rate": 1, "Use this frame rate": 29.97});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Template-based samples (Draft, DV, Multi-Machine, Log)
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Draft Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "DV Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Multi-Machine Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "Multi-Machine Sequence");
        p.om.file = new File(downloadFolder + "/[compName]/[compName]_[#####].psd");
        saveProject(p.proj, folder.fsName);

        // Log settings samples
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        try {
            p.rqItem.logType = LogType.PLUS_SETTINGS;
        } catch (e) {}
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        try {
            p.rqItem.logType = LogType.PLUS_PER_FRAME_INFO;
        } catch (e) {}
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Skip Frames samples
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Time Span": 0, "Frame Rate": 1, "Use this frame rate": 30});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        p.rqItem.skipFrames = 0;
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Time Span": 0, "Frame Rate": 1, "Use this frame rate": 30});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        p.rqItem.skipFrames = 1;
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Time Span": 0, "Frame Rate": 1, "Use this frame rate": 30});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        p.rqItem.skipFrames = 2;
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings", {"Time Span": 0, "Frame Rate": 1, "Use this frame rate": 30});
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        p.rqItem.skipFrames = 3;
        saveProject(p.proj, folder.fsName);

        // -----------------------------------------------------------------
        // Output Module samples - Audio settings
        // -----------------------------------------------------------------
        var omFolder = ensureFolder(outputPath + "/output_module");

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "Lossless", {"Output Audio": false});
        p.om.file = new File(downloadFolder + "/[compName].avi");
        saveProject(p.proj, omFolder.fsName + "/audio_output_off.aep");

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "Lossless", {"Output Audio": true});
        p.om.file = new File(downloadFolder + "/[compName].avi");
        saveProject(p.proj, omFolder.fsName + "/audio_output_on.aep");

        // Audio bit depth samples
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "Lossless", {"Output Audio": true, "Audio Bit Depth": 1});  // 8-bit
        p.om.file = new File(downloadFolder + "/[compName].avi");
        saveProject(p.proj, omFolder.fsName + "/audio_8bit.aep");

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "Lossless", {"Output Audio": true, "Audio Bit Depth": 4});  // 32-bit
        p.om.file = new File(downloadFolder + "/[compName].avi");
        saveProject(p.proj, omFolder.fsName + "/audio_32bit.aep");

        // Audio channels sample
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "Lossless", {"Output Audio": true, "Audio Channels": 1});  // Mono
        p.om.file = new File(downloadFolder + "/[compName].avi");
        saveProject(p.proj, omFolder.fsName + "/audio_mono.aep");

        // Audio sample rate samples
        var sampleRates = [8000, 16000, 22050, 32000, 96000];
        for (var i = 0; i < sampleRates.length; i++) {
            p = createRenderQueueProject("Comp 1");
            applyRenderSettings(p.rqItem, "Best Settings");
            p.om = applyOutputModuleSettings(p.rqItem, "Lossless", {"Output Audio": true, "Sample Rate": sampleRates[i]});
            p.om.file = new File(downloadFolder + "/[compName].avi");
            saveProject(p.proj, omFolder.fsName + "/audio_" + sampleRates[i] + "hz.aep");
        }

        // -----------------------------------------------------------------
        // Output Module samples - Video settings
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "Lossless", {"Channels": 2});  // Alpha only
        p.om.file = new File(downloadFolder + "/[compName].avi");
        saveProject(p.proj, omFolder.fsName + "/channels_alpha.aep");

        // Color: Straight (Unmatted)
        // NOTE: The "Color" setting cannot be changed via setSettings() in ExtendScript.
        // AE silently ignores the setting. This sample will have Color=1 (Premultiplied).
        // To get Color=0, the sample must be manually created in After Effects UI.
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "TIFF Sequence with Alpha", {"Color": 0});  // Straight (Unmatted) - DOES NOT WORK
        p.om.file = new File(downloadFolder + "/[compName]/[compName]_[#####].tif");
        saveProject(p.proj, omFolder.fsName + "/color_straight_unmatted.aep");

        // Custom H.264 sample
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, omFolder.fsName + "/custom_h264.aep");

        // -----------------------------------------------------------------
        // Output Module samples - Crop settings
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "Lossless", {
            "Crop": true,
            "Crop Top": 10,
            "Crop Left": 10,
            "Crop Bottom": 10,
            "Crop Right": 10
        });
        p.om.file = new File(downloadFolder + "/[compName].avi");
        saveProject(p.proj, omFolder.fsName + "/crop_checked.aep");

        // Crop using Region of Interest
        p = createRenderQueueProject("Comp 1");
        p.comp.regionOfInterest = [100, 100, 800, 600];  // Set ROI
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "Lossless", {"Crop": true});
        p.om.file = new File(downloadFolder + "/[compName].avi");
        saveProject(p.proj, omFolder.fsName + "/crop_use_roi_checked.aep");

        // -----------------------------------------------------------------
        // Output Module samples - Resize settings
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "Lossless", {
            "Stretch": true,
            "Stretch Width": 1280,
            "Stretch Height": 720
        });
        p.om.file = new File(downloadFolder + "/[compName].avi");
        saveProject(p.proj, omFolder.fsName + "/resize_checked.aep");

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "Lossless", {
            "Stretch": true,
            "Stretch Width": 1280,
            "Stretch Height": 800  // Different aspect ratio
        });
        p.om.file = new File(downloadFolder + "/[compName].avi");
        saveProject(p.proj, omFolder.fsName + "/resize_lock_aspect_ratio_unchecked.aep");

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "Lossless", {
            "Stretch": true,
            "Stretch Width": 640,
            "Stretch Height": 480,
            "Stretch Quality": 0  // Low
        });
        p.om.file = new File(downloadFolder + "/[compName].avi");
        saveProject(p.proj, omFolder.fsName + "/resize_quality_low.aep");

        // -----------------------------------------------------------------
        // Output Module samples - Other settings
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        try { p.om.includeSourceXMP = true; } catch (e) {}
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, omFolder.fsName + "/include_source_xmp_data_on.aep");

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, omFolder.fsName + "/include_project_link_off.aep");

        // -----------------------------------------------------------------
        // Output path pattern samples
        // -----------------------------------------------------------------
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName]_[outputModuleName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName]/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName]_[width]x[height].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName]_[pixelAspect].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[compName]_[dateYear]-[dateMonth]-[dateDay]_[timeHours]-[timeMins]-[timeSecs].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[projectName]_[compName].mp4");
        saveProject(p.proj, folder.fsName);

        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File("[projectFolder]/[compName].mp4");
        saveProject(p.proj, folder.fsName);

        // All fields combined
        p = createRenderQueueProject("Comp 1");
        applyRenderSettings(p.rqItem, "Best Settings");
        p.om = applyOutputModuleSettings(p.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        p.om.file = new File(downloadFolder + "/[projectFolder]\__[projectName]__[compName]__[renderSettingsName]__[outputModuleName]__[width]__[height]__[frameRate]__[aspectRatio]__[startFrame]__[endFrame]__[durationFrames]__[#####]__[startTimecode]__[endTimecode]__[durationTimecode]__[channels]__[projectColorDepth]__[outputColorDepth]__[compressor]__[fieldOrder]__[pulldownPhase]__[dateYear]__[dateMonth]__[dateDay]__[timeHour]__[timeMins]__[timeSecs]__[timeZone].[fileExtension]");
        saveProject(p.proj, folder.fsName);

        $.writeln("Generated renderqueue samples in: " + folder.fsName);
    }

    // =========================================================================
    // Main Execution
    // =========================================================================

    function main() {
        // Resolve samples/models/ relative to this script's location
        // Script is at scripts/jsx/, so ../../samples/models/
        var scriptFile = new File($.fileName);
        var scriptDir = scriptFile.parent;
        var modelsFolder = new Folder(scriptDir.fsName + "/../../samples/models");
        if (!modelsFolder.exists) {
            alert("Could not find samples/models/ relative to script.\n" +
                  "Expected: " + modelsFolder.fsName);
            return;
        }

        var OUTPUT_FOLDER = modelsFolder.fsName;

        $.writeln("=== Starting Sample Generation ===");
        $.writeln("Output folder: " + OUTPUT_FOLDER);
        $.writeln("Creating ONE .aep file per test case for isolation.");
        $.writeln("");

        try {
            // $.writeln("--- Project samples ---");
            // generateProjectSamples(OUTPUT_FOLDER);

            // $.writeln("--- Composition samples ---");
            // generateCompositionSamples(OUTPUT_FOLDER);

            // $.writeln("--- Layer samples ---");
            // generateLayerSamples(OUTPUT_FOLDER);

            // $.writeln("--- Footage samples ---");
            // generateFootageSamples(OUTPUT_FOLDER);

            // $.writeln("--- Folder samples ---");
            // generateFolderSamples(OUTPUT_FOLDER);

            // $.writeln("--- Marker samples ---");
            // generateMarkerSamples(OUTPUT_FOLDER);

            // $.writeln("--- Mask samples ---");
            // generateMaskSamples(OUTPUT_FOLDER);

            // $.writeln("--- Property samples ---");
            // generatePropertySamples(OUTPUT_FOLDER);

            $.writeln("--- Shape samples ---");
            generateShapeSamples(OUTPUT_FOLDER);

            // $.writeln("--- RenderQueue samples ---");
            // generateRenderQueueSamples(OUTPUT_FOLDER);
        } catch(e) {
            $.writeln("Error in scene '" + currentScene + "': " + e.toString());
            alert("Error in scene '" + currentScene + "':\n" + e.toString());
            return;
        }

        $.writeln("");
        $.writeln("=== Sample Generation Complete ===");
        $.writeln("Each .aep file tests ONE attribute for isolation.");
        $.writeln("Corresponding .json files have been generated automatically.");

        alert("Sample generation complete!\n\n" +
              "Output: " + OUTPUT_FOLDER + "\n\n" +
              "Each .aep file tests ONE attribute.\n" +
              "Corresponding .json files have been generated.");
    }

    main();

})();
