/**
 * Generate CONSOLIDATED Test Samples for py_aep Model Testing
 *
 * Creates FEWER .aep files, each containing MULTIPLE comps/items.
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

    function getAssetsFolder(modelsPath) {
        // modelsPath is samples/models, assets is samples/assets
        var modelsFolder = new Folder(modelsPath);
        var samplesFolder = modelsFolder.parent;
        return samplesFolder.fsName + "/assets";
    }

    // =========================================================================
    // Project Model Samples
    // Covers: PROJECT_ATTRS
    // Not covered (read-only): numItems, revision
    // CC 2024+ (undocumented): colorManagementSystem, lutInterpolationMethod,
    //   ocioConfigurationFile
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
        proj.colorManagementSystem = 0; // Adobe
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
    // Composition Model Samples (CONSOLIDATED)
    // Covers: ITEM_ATTRS + AVITEM_ATTRS + COMPITEM_ATTRS
    // Read-only: id, typeName, numLayers, footageMissing, hasAudio, hasVideo,
    //   frameDuration, renderers, time (writable on comp)
    // =========================================================================

    function generateCompositionSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/composition");
        var proj, c;

        // --- bgColor.aep ---
        proj = createProject("bgColor");
        c = proj.items.addComp("bgColor_red", 100, 100, 1, 1, 24);
        c.bgColor = [1, 0, 0];
        c = proj.items.addComp("bgColor_custom", 100, 100, 1, 1, 24);
        c.bgColor = [0.2, 0.4, 0.6];
        saveProject(proj, folder.fsName);

        // --- size.aep ---
        proj = createProject("size");
        proj.items.addComp("size_1920x1080", 1920, 1080, 1, 1, 24);
        proj.items.addComp("size_2048x872", 2048, 872, 1, 1, 24);
        saveProject(proj, folder.fsName);

        // --- frameRate.aep ---
        proj = createProject("frameRate");
        proj.items.addComp("frameRate_23976", 100, 100, 1, 1, 23.976);
        proj.items.addComp("frameRate_30", 100, 100, 1, 1, 30);
        proj.items.addComp("frameRate_60", 100, 100, 1, 1, 60);
        saveProject(proj, folder.fsName);

        // --- pixelAspect.aep ---
        proj = createProject("pixelAspect");
        proj.items.addComp("pixelAspect_0.75", 100, 100, 0.75, 1, 24);
        proj.items.addComp("pixelAspect_2", 100, 100, 2.0, 1, 24);
        saveProject(proj, folder.fsName);

        // --- displayStart.aep ---
        proj = createProject("displayStart");
        c = proj.items.addComp("displayStartFrame_100", 100, 100, 1, 10, 24);
        c.displayStartFrame = 100;
        c = proj.items.addComp("displayStartTime_10", 100, 100, 1, 30, 24);
        c.displayStartTime = 10;
        saveProject(proj, folder.fsName);

        // --- dropFrame.aep ---
        proj = createProject("dropFrame");
        c = proj.items.addComp("dropFrame_true", 100, 100, 1, 1, 29.97);
        c.dropFrame = true;
        c = proj.items.addComp("dropFrame_false", 100, 100, 1, 1, 29.97);
        c.dropFrame = false;
        saveProject(proj, folder.fsName);

        // --- shutterAngle.aep ---
        proj = createProject("shutterAngle");
        c = proj.items.addComp("shutterAngle_180", 100, 100, 1, 1, 24);
        c.shutterAngle = 180;
        c = proj.items.addComp("shutterAngle_360", 100, 100, 1, 1, 24);
        c.shutterAngle = 360;
        saveProject(proj, folder.fsName);

        // --- resolutionFactor.aep ---
        proj = createProject("resolutionFactor");
        c = proj.items.addComp("resolutionFactor_half", 100, 100, 1, 1, 24);
        c.resolutionFactor = [2, 2];
        c = proj.items.addComp("resolutionFactor_quarter", 100, 100, 1, 1, 24);
        c.resolutionFactor = [4, 4];
        saveProject(proj, folder.fsName);

        // --- time.aep ---
        proj = createProject("time");
        c = proj.items.addComp("time_0", 100, 100, 1, 30, 24);
        c.time = 0;
        c = proj.items.addComp("time_5", 100, 100, 1, 30, 24);
        c.time = 5;
        c = proj.items.addComp("time_15", 100, 100, 1, 30, 24);
        c.time = 15;
        saveProject(proj, folder.fsName);

        // --- workArea.aep ---
        proj = createProject("workArea");
        c = proj.items.addComp("workAreaStart_5", 100, 100, 1, 30, 24);
        c.workAreaStart = 5;
        c = proj.items.addComp("workAreaDuration_10", 100, 100, 1, 30, 24);
        c.workAreaDuration = 10;
        saveProject(proj, folder.fsName);

        // --- guides.aep ---
        proj = createProject("guides");
        proj.items.addComp("guides_none", 1920, 1080, 1, 1, 24);
        c = proj.items.addComp("guides_horizontal", 1920, 1080, 1, 1, 24);
        c.addGuide(0, 540);
        c = proj.items.addComp("guides_both", 1920, 1080, 1, 1, 24);
        c.addGuide(0, 270);   // horizontal at 270px
        c.addGuide(0, 810);   // horizontal at 810px
        c.addGuide(1, 960);   // vertical at 960px
        saveProject(proj, folder.fsName);

        // --- comp_flags.aep ---
        proj = createProject("comp_flags");
        c = proj.items.addComp("motionBlur_true", 100, 100, 1, 1, 24);
        c.motionBlur = true;
        c = proj.items.addComp("motionBlurAdaptiveSampleLimit_256", 100, 100, 1, 1, 24);
        c.motionBlurAdaptiveSampleLimit = 256;
        c = proj.items.addComp("motionBlurSamplesPerFrame_32", 100, 100, 1, 1, 24);
        c.motionBlurSamplesPerFrame = 32;
        c = proj.items.addComp("shutterPhase_minus90", 100, 100, 1, 1, 24);
        c.shutterPhase = -90;
        c = proj.items.addComp("frameBlending_true", 100, 100, 1, 1, 24);
        c.frameBlending = true;
        c = proj.items.addComp("hideShyLayers_true", 100, 100, 1, 1, 24);
        c.hideShyLayers = true;
        c = proj.items.addComp("preserveNestedFrameRate_true", 100, 100, 1, 1, 24);
        c.preserveNestedFrameRate = true;
        c = proj.items.addComp("preserveNestedResolution_true", 100, 100, 1, 1, 24);
        c.preserveNestedResolution = true;
        saveProject(proj, folder.fsName);

        // --- comp_misc.aep ---
        proj = createProject("comp_misc");
        c = proj.items.addComp("OriginalName", 100, 100, 1, 1, 24);
        c.name = "RenamedComp";
        c = proj.items.addComp("comment", 100, 100, 1, 1, 24);
        c.comment = "Test comment";
        c = proj.items.addComp("label_5", 100, 100, 1, 1, 24);
        c.label = 5;
        proj.items.addComp("duration_60", 100, 100, 1, 60, 24);
        saveProject(proj, folder.fsName);

        $.writeln("Generated composition samples in: " + folder.fsName);
    }

    // =========================================================================
    // Layer Model Samples
    // Covers: LAYER_ATTRS, AVLAYER_ATTRS, LIGHTLAYER_ATTRS, layer types,
    //   audioEnabled, timing edge cases (precomp outPoint clamping)
    // =========================================================================

    function generateLayerSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/layer");
        var proj, comp, c, layer, precomp, matteLayer, parentNull;

        // --- quality.aep ---
        proj = createProject("quality");
        c = proj.items.addComp("quality_BEST", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.quality = LayerQuality.BEST;
        c = proj.items.addComp("quality_DRAFT", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.quality = LayerQuality.DRAFT;
        c = proj.items.addComp("quality_WIREFRAME", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.quality = LayerQuality.WIREFRAME;
        saveProject(proj, folder.fsName);

        // --- blendingMode.aep ---
        proj = createProject("blendingMode");
        c = proj.items.addComp("blendingMode_MULTIPLY", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.blendingMode = BlendingMode.MULTIPLY;
        c = proj.items.addComp("blendingMode_SCREEN", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.blendingMode = BlendingMode.SCREEN;
        c = proj.items.addComp("blendingMode_ADD", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.blendingMode = BlendingMode.ADD;
        saveProject(proj, folder.fsName);

        // --- frameBlendingType.aep ---
        proj = createProject("frameBlendingType");
        c = proj.items.addComp("frameBlendingType_NO_FRAME_BLEND", 100, 100, 1, 10, 24);
        c.frameBlending = true;
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        c = proj.items.addComp("frameBlendingType_FRAME_MIX", 100, 100, 1, 10, 24);
        c.frameBlending = true;
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.frameBlendingType = FrameBlendingType.FRAME_MIX;
        c = proj.items.addComp("frameBlendingType_PIXEL_MOTION", 100, 100, 1, 10, 24);
        c.frameBlending = true;
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.frameBlendingType = FrameBlendingType.PIXEL_MOTION;
        saveProject(proj, folder.fsName);

        // --- lightType.aep ---
        proj = createProject("lightType");
        c = proj.items.addComp("lightType_PARALLEL", 100, 100, 1, 10, 24);
        layer = c.layers.addLight("TestLight", [50, 50]);
        layer.lightType = LightType.PARALLEL;
        c = proj.items.addComp("lightType_SPOT", 100, 100, 1, 10, 24);
        layer = c.layers.addLight("TestLight", [50, 50]);
        layer.lightType = LightType.SPOT;
        c = proj.items.addComp("lightType_POINT", 100, 100, 1, 10, 24);
        layer = c.layers.addLight("TestLight", [50, 50]);
        layer.lightType = LightType.POINT;
        c = proj.items.addComp("lightType_AMBIENT", 100, 100, 1, 10, 24);
        layer = c.layers.addLight("TestLight", [50, 50]);
        layer.lightType = LightType.AMBIENT;
        saveProject(proj, folder.fsName);

        // --- autoOrient.aep ---
        proj = createProject("autoOrient");
        c = proj.items.addComp("autoOrient_ALONG_PATH", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.autoOrient = AutoOrientType.ALONG_PATH;
        c = proj.items.addComp("autoOrient_CAMERA", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.threeDLayer = true;
        layer.autoOrient = AutoOrientType.CAMERA_OR_POINT_OF_INTEREST;
        c = proj.items.addComp("autoOrient_CHARACTERS", 100, 100, 1, 10, 24);
        layer = c.layers.addText("3D Text");
        layer.threeDLayer = true;
        layer.threeDPerChar = true;
        layer.autoOrient = AutoOrientType.CHARACTERS_TOWARD_CAMERA;
        saveProject(proj, folder.fsName);

        // --- trackMatteType.aep ---
        proj = createProject("trackMatteType");
        c = proj.items.addComp("trackMatteType_ALPHA", 100, 100, 1, 10, 24);
        matteLayer = c.layers.addSolid([1, 1, 1], "MatteLayer", 100, 100, 1);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        if (typeof layer.setTrackMatte === "function") {
            layer.setTrackMatte(matteLayer, TrackMatteType.ALPHA);
        } else {
            layer.trackMatteType = TrackMatteType.ALPHA;
        }
        c = proj.items.addComp("trackMatteType_LUMA", 100, 100, 1, 10, 24);
        matteLayer = c.layers.addSolid([1, 1, 1], "MatteLayer", 100, 100, 1);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        if (typeof layer.setTrackMatte === "function") {
            layer.setTrackMatte(matteLayer, TrackMatteType.LUMA);
        } else {
            layer.trackMatteType = TrackMatteType.LUMA;
        }
        saveProject(proj, folder.fsName);

        // --- type.aep ---
        proj = createProject("type");
        c = proj.items.addComp("type_null", 100, 100, 1, 10, 24);
        c.layers.addNull();
        c = proj.items.addComp("type_text", 100, 100, 1, 10, 24);
        c.layers.addText("TextLayer");
        c = proj.items.addComp("type_shape", 100, 100, 1, 10, 24);
        c.layers.addShape();
        c = proj.items.addComp("type_camera", 100, 100, 1, 10, 24);
        c.layers.addCamera("CameraLayer", [50, 50]);
        saveProject(proj, folder.fsName);

        // --- avlayer_flags.aep ---
        proj = createProject("avlayer_flags");
        c = proj.items.addComp("adjustmentLayer_true", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.adjustmentLayer = true;
        c = proj.items.addComp("collapseTransformation_true", 100, 100, 1, 10, 24);
        precomp = proj.items.addComp("Precomp_1s", 100, 100, 1, 1, 24);
        layer = c.layers.add(precomp);
        if (layer.canSetCollapseTransformation) {
            layer.collapseTransformation = true;
        }
        c = proj.items.addComp("effectsActive_false", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.effectsActive = false;
        c = proj.items.addComp("guideLayer_true", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.guideLayer = true;
        c = proj.items.addComp("motionBlur_true", 100, 100, 1, 10, 24);
        c.motionBlur = true;
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.motionBlur = true;
        c = proj.items.addComp("preserveTransparency_true", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.preserveTransparency = true;
        c = proj.items.addComp("samplingQuality_BICUBIC", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.samplingQuality = LayerSamplingQuality.BICUBIC;
        c = proj.items.addComp("threeDLayer_true", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.threeDLayer = true;
        c = proj.items.addComp("timeRemapEnabled_true", 100, 100, 1, 10, 24);
        precomp = proj.items.addComp("Precomp_5s", 100, 100, 1, 5, 24);
        layer = c.layers.add(precomp);
        layer.timeRemapEnabled = true;
        saveProject(proj, folder.fsName);

        // --- audioEnabled.aep ---
        proj = createProject("audioEnabled");
        var wavFile = new File(getAssetsFolder(outputPath) + "/wav.wav");
        var importOptions, audioFootage;
        c = proj.items.addComp("audioEnabled_true", 100, 100, 1, 10, 24);
        importOptions = new ImportOptions(wavFile);
        audioFootage = proj.importFile(importOptions);
        layer = c.layers.add(audioFootage);
        layer.audioEnabled = true;
        c = proj.items.addComp("audioEnabled_false", 100, 100, 1, 10, 24);
        layer = c.layers.add(audioFootage);
        layer.audioEnabled = false;
        saveProject(proj, folder.fsName);

        // --- inPoint.aep ---
        proj = createProject("inPoint");
        c = proj.items.addComp("inPoint_0", 100, 100, 1, 30, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.inPoint = 0;
        c = proj.items.addComp("inPoint_5", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.inPoint = 5;
        c = proj.items.addComp("inPoint_before_startTime", 100, 100, 1, 60, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.startTime = 10;
        layer.inPoint = 5;
        saveProject(proj, folder.fsName);

        // --- outPoint.aep ---
        proj = createProject("outPoint");
        c = proj.items.addComp("outPoint_10", 100, 100, 1, 60, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.outPoint = 10;
        c = proj.items.addComp("outPoint_at_duration", 100, 100, 1, 30, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        c = proj.items.addComp("outPoint_with_negative_startTime", 100, 100, 1, 30, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.startTime = -5;
        layer.outPoint = 20;
        saveProject(proj, folder.fsName);

        // --- outPoint_clamp.aep ---
        // All use a shared precomp with 5s duration
        proj = createProject("outPoint_clamp");
        precomp = proj.items.addComp("Precomp_5s", 100, 100, 1, 5, 24);
        c = proj.items.addComp("outPoint_clamp_precomp", 100, 100, 1, 30, 24);
        layer = c.layers.add(precomp);
        c = proj.items.addComp("outPoint_clamp_stretch_200", 100, 100, 1, 30, 24);
        layer = c.layers.add(precomp);
        layer.stretch = 200;
        c = proj.items.addComp("outPoint_clamp_stretch_400", 100, 100, 1, 30, 24);
        layer = c.layers.add(precomp);
        layer.stretch = 400;
        c = proj.items.addComp("outPoint_clamp_with_startTime", 100, 100, 1, 30, 24);
        layer = c.layers.add(precomp);
        layer.startTime = 3;
        saveProject(proj, folder.fsName);

        // --- outPoint_no_clamp.aep ---
        // All use a shared precomp with 5s duration
        proj = createProject("outPoint_no_clamp");
        precomp = proj.items.addComp("Precomp_5s", 100, 100, 1, 5, 24);
        c = proj.items.addComp("outPoint_no_clamp_collapse", 100, 100, 1, 30, 24);
        layer = c.layers.add(precomp);
        if (layer.canSetCollapseTransformation) {
            layer.collapseTransformation = true;
        }
        layer.outPoint = 30;
        c = proj.items.addComp("outPoint_no_clamp_timeRemap", 100, 100, 1, 30, 24);
        layer = c.layers.add(precomp);
        layer.timeRemapEnabled = true;
        layer.outPoint = 30;
        c = proj.items.addComp("outPoint_no_clamp_negative_stretch", 100, 100, 1, 30, 24);
        layer = c.layers.add(precomp);
        layer.stretch = -100;
        saveProject(proj, folder.fsName);

        // --- layer_switches.aep ---
        proj = createProject("layer_switches");
        c = proj.items.addComp("shy_true", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.shy = true;
        c = proj.items.addComp("solo_true", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.solo = true;
        c = proj.items.addComp("locked_true", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.locked = true;
        c = proj.items.addComp("enabled_false", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.enabled = false;
        saveProject(proj, folder.fsName);

        // --- layer_timing.aep ---
        proj = createProject("layer_timing");
        c = proj.items.addComp("startTime_5", 100, 100, 1, 60, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.startTime = 5;
        c = proj.items.addComp("stretch_200", 100, 100, 1, 60, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.stretch = 200;
        c = proj.items.addComp("stretch_minus100", 100, 100, 1, 60, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.stretch = -100;
        c = proj.items.addComp("time_30", 100, 100, 1, 60, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        c.time = 30;
        saveProject(proj, folder.fsName);

        // --- layer_misc.aep ---
        proj = createProject("layer_misc");
        c = proj.items.addComp("name_renamed", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "OriginalName", 100, 100, 1);
        layer.name = "RenamedLayer";
        c = proj.items.addComp("comment", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.comment = "Test layer comment";
        c = proj.items.addComp("label_3", 100, 100, 1, 10, 24);
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.label = 3;
        c = proj.items.addComp("parent", 100, 100, 1, 10, 24);
        parentNull = c.layers.addNull();
        parentNull.name = "ParentNull";
        layer = c.layers.addSolid([0.5, 0.5, 0.5], "ChildLayer", 100, 100, 1);
        layer.parent = parentNull;
        saveProject(proj, folder.fsName);

        $.writeln("Generated layer samples in: " + folder.fsName);
    }


    // =========================================================================
    // Footage Model Samples (CONSOLIDATED)
    // Covers: SolidSource, PlaceholderSource, FileSource attributes
    // 8 consolidated files from ~30 original scenes
    // =========================================================================

    function generateFootageSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/footage");
        var assetsPath = getAssetsFolder(outputPath);
        var movFile = new File(assetsPath + "/mov_480.mov");
        var alphaImageFile = new File(assetsPath + "/image_with_alpha.png");
        var proj, comp, importOptions, footage;

        // --- solid_colors.aep ---
        proj = createProject("solid_colors");
        comp = proj.items.addComp("solid_color_red", 100, 100, 1, 1, 24);
        comp.layers.addSolid([1, 0, 0], "Solid", 100, 100, 1);
        comp = proj.items.addComp("solid_color_green", 100, 100, 1, 1, 24);
        comp.layers.addSolid([0, 1, 0], "Solid", 100, 100, 1);
        comp = proj.items.addComp("solid_color_blue", 100, 100, 1, 1, 24);
        comp.layers.addSolid([0, 0, 1], "Solid", 100, 100, 1);
        comp = proj.items.addComp("solid_color_gray", 100, 100, 1, 1, 24);
        comp.layers.addSolid([0.5, 0.5, 0.5], "Solid", 100, 100, 1);
        saveProject(proj, folder.fsName);

        // --- solid_sizes.aep ---
        proj = createProject("solid_sizes");
        comp = proj.items.addComp("solid_size_1920x1080", 1920, 1080, 1, 1, 24);
        comp.layers.addSolid([0.5, 0.5, 0.5], "Solid", 1920, 1080, 1);
        comp = proj.items.addComp("solid_size_3840x2160", 3840, 2160, 1, 1, 24);
        comp.layers.addSolid([0.5, 0.5, 0.5], "Solid", 3840, 2160, 1);
        comp = proj.items.addComp("solid_pixelAspect_2", 100, 100, 2, 1, 24);
        comp.layers.addSolid([0.5, 0.5, 0.5], "Solid", 100, 100, 2);
        saveProject(proj, folder.fsName);

        // --- placeholder.aep ---
        proj = createProject("placeholder");
        proj.importPlaceholder("placeholder_still", 1920, 1080, 24, 0);
        proj.importPlaceholder("placeholder_movie", 1920, 1080, 24, 10);
        proj.importPlaceholder("placeholder_30fps", 1920, 1080, 30, 10);
        proj.importPlaceholder("placeholder_60fps", 1920, 1080, 60, 10);
        proj.importPlaceholder("placeholder_720p", 1280, 720, 24, 10);
        proj.importPlaceholder("placeholder_4K", 3840, 2160, 24, 10);
        saveProject(proj, folder.fsName);

        // --- alphaMode.aep ---
        proj = createProject("alphaMode");
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.name = "alphaMode_STRAIGHT";
        footage.mainSource.alphaMode = AlphaMode.STRAIGHT;
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.name = "alphaMode_PREMULTIPLIED";
        footage.mainSource.alphaMode = AlphaMode.PREMULTIPLIED;
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.name = "alphaMode_IGNORE";
        footage.mainSource.alphaMode = AlphaMode.IGNORE;
        saveProject(proj, folder.fsName);

        // --- conformFrameRate.aep ---
        proj = createProject("conformFrameRate");
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.name = "conformFrameRate_30";
        footage.mainSource.conformFrameRate = 30;
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.name = "conformFrameRate_24";
        footage.mainSource.conformFrameRate = 24;
        saveProject(proj, folder.fsName);

        // --- fieldSeparationType.aep ---
        proj = createProject("fieldSeparationType");
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.name = "fieldSeparationType_OFF";
        footage.mainSource.fieldSeparationType = FieldSeparationType.OFF;
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.name = "fieldSeparationType_UPPER";
        footage.mainSource.fieldSeparationType = FieldSeparationType.UPPER_FIELD_FIRST;
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.name = "fieldSeparationType_LOWER";
        footage.mainSource.fieldSeparationType = FieldSeparationType.LOWER_FIELD_FIRST;
        saveProject(proj, folder.fsName);

        // --- premulColor.aep ---
        proj = createProject("premulColor");
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.name = "premulColor_red";
        footage.mainSource.alphaMode = AlphaMode.PREMULTIPLIED;
        footage.mainSource.premulColor = [1, 0, 0];
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.name = "premulColor_black";
        footage.mainSource.alphaMode = AlphaMode.PREMULTIPLIED;
        footage.mainSource.premulColor = [0, 0, 0];
        saveProject(proj, folder.fsName);

        // --- footage_misc.aep ---
        proj = createProject("footage_misc");
        // name_renamed
        var item = proj.importPlaceholder("OriginalName", 100, 100, 24, 1);
        item.name = "RenamedFootage";
        // frameRate_23976
        var mov23976File = new File(assetsPath + "/mov_23_976.mov");
        importOptions = new ImportOptions(mov23976File);
        footage = proj.importFile(importOptions);
        footage.name = "frameRate_23976";
        // highQualityFieldSeparation_true
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.name = "highQualityFieldSeparation_true";
        footage.mainSource.fieldSeparationType = FieldSeparationType.UPPER_FIELD_FIRST;
        footage.mainSource.highQualityFieldSeparation = true;
        // invertAlpha_true
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.name = "invertAlpha_true";
        footage.mainSource.invertAlpha = true;
        // loop_3
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.name = "loop_3";
        footage.mainSource.loop = 3;
        // removePulldown_OFF
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.name = "removePulldown_OFF";
        footage.mainSource.removePulldown = PulldownPhase.OFF;
        // imageSequence_numbered
        var sequenceFile = new File(assetsPath + "/sequence_001.gif");
        importOptions = new ImportOptions(sequenceFile);
        importOptions.sequence = true;
        footage = proj.importFile(importOptions);
        footage.name = "imageSequence_numbered";
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

        // --- folder.aep ---
        proj = createProject("folder");

        // name_renamed
        f = proj.items.addFolder("OriginalName");
        f.name = "RenamedFolder";

        // comment
        f = proj.items.addFolder("comment");
        f.comment = "Folder comment";

        // label_1
        f = proj.items.addFolder("label_1");
        f.label = 1;

        // label_5
        f = proj.items.addFolder("label_5");
        f.label = 5;

        // label_10
        f = proj.items.addFolder("label_10");
        f.label = 10;

        // parentFolder_nested
        var root = proj.items.addFolder("RootFolder");
        var nested1 = proj.items.addFolder("Level1");
        nested1.parentFolder = root;
        var nested2 = proj.items.addFolder("Level2");
        nested2.parentFolder = nested1;
        var nested3 = proj.items.addFolder("Level3");
        nested3.parentFolder = nested2;

        // numItems_3
        var withItems = proj.items.addFolder("FolderWithItems");
        var c1 = proj.items.addComp("Comp1", 100, 100, 1, 1, 24);
        c1.parentFolder = withItems;
        var c2 = proj.items.addComp("Comp2", 100, 100, 1, 1, 24);
        c2.parentFolder = withItems;
        var ph = proj.importPlaceholder("Placeholder", 100, 100, 24, 1);
        ph.parentFolder = withItems;

        // empty
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

        // --- comp_marker.aep ---
        proj = createProject("comp_marker");

        // comment
        comp = proj.items.addComp("comment", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.comment = "Test comment";
        comp.markerProperty.setValueAtTime(0, m);

        // chapter
        comp = proj.items.addComp("chapter", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.chapter = "Chapter 1";
        comp.markerProperty.setValueAtTime(0, m);

        // url
        comp = proj.items.addComp("url", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.url = "https://example.com";
        comp.markerProperty.setValueAtTime(0, m);

        // frameTarget
        comp = proj.items.addComp("frameTarget", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.url = "https://example.com";
        m.frameTarget = "_blank";
        comp.markerProperty.setValueAtTime(0, m);

        // cuePointName
        comp = proj.items.addComp("cuePointName", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.cuePointName = "cue_test";
        comp.markerProperty.setValueAtTime(0, m);

        // duration_5
        comp = proj.items.addComp("duration_5", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.duration = 5;
        comp.markerProperty.setValueAtTime(0, m);

        // label_0
        comp = proj.items.addComp("label_0", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.label = 0;
        comp.markerProperty.setValueAtTime(0, m);

        // label_3
        comp = proj.items.addComp("label_3", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.label = 3;
        comp.markerProperty.setValueAtTime(0, m);

        // label_8
        comp = proj.items.addComp("label_8", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.label = 8;
        comp.markerProperty.setValueAtTime(0, m);

        // protectedRegion_true
        comp = proj.items.addComp("protectedRegion_true", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.protectedRegion = true;
        comp.markerProperty.setValueAtTime(0, m);

        saveProject(proj, folder.fsName);

        // --- layer_marker.aep ---
        proj = createProject("layer_marker");

        // layer_comment
        comp = proj.items.addComp("layer_comment", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        m = new MarkerValue("LayerMarker");
        m.comment = "Layer marker comment";
        layer.marker.setValueAtTime(0, m);

        // layer_duration
        comp = proj.items.addComp("layer_duration", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        m = new MarkerValue("LayerMarker");
        m.duration = 3;
        layer.marker.setValueAtTime(0, m);

        // layer_cuePointName
        comp = proj.items.addComp("layer_cuePointName", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        m = new MarkerValue("LayerMarker");
        m.cuePointName = "layer_cue_1";
        layer.marker.setValueAtTime(0, m);

        // layer_multiple_markers
        comp = proj.items.addComp("layer_multiple_markers", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        m = new MarkerValue("First");
        m.comment = "first marker";
        layer.marker.setValueAtTime(1, m);
        m = new MarkerValue("Second");
        m.comment = "second marker";
        m.duration = 2;
        layer.marker.setValueAtTime(4, m);
        m = new MarkerValue("Third");
        m.label = 5;
        layer.marker.setValueAtTime(7, m);

        // layer_marker_with_startTime
        comp = proj.items.addComp("layer_marker_with_startTime", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.startTime = 3;
        m = new MarkerValue("OffsetMarker");
        m.comment = "marker at comp time 5";
        layer.marker.setValueAtTime(5, m);

        saveProject(proj, folder.fsName);

        $.writeln("Generated marker samples in: " + folder.fsName);
    }

    // =========================================================================
    // Property, Mask & Shape Samples
    // Covers: Property, PropertyGroup, keyframes, expressions, effects,
    //   masks, shape paths, feather points
    // =========================================================================

    function generatePropertySamples(outputPath) {
        var folder = ensureFolder(outputPath + "/property");
        var proj, comp, layer, prop, maskGroup, mask, myShape;
        var easeIn, easeOut;

        // =================================================================
        // mask.aep - Mask-related samples
        // =================================================================
        proj = createProject("mask");

        // is_mask_true
        comp = proj.items.addComp("is_mask_true", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        maskGroup = layer.property("ADBE Mask Parade");
        mask = maskGroup.addProperty("ADBE Mask Atom");
        myShape = new Shape();
        myShape.vertices = [[10, 10], [90, 10], [90, 90], [10, 90]];
        myShape.closed = true;
        mask.property("ADBE Mask Shape").setValue(myShape);

        // is_mask_multiple
        comp = proj.items.addComp("is_mask_multiple", 100, 100, 1, 10, 24);
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

        // =================================================================
        // keyframe_interpolation.aep - Basic keyframe interpolation types
        // =================================================================
        proj = createProject("keyframe_interpolation");

        // keyframe_LINEAR
        comp = proj.items.addComp("keyframe_LINEAR", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 50]);
        prop.setValueAtTime(5, [100, 50]);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR);

        // keyframe_BEZIER
        comp = proj.items.addComp("keyframe_BEZIER", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 50]);
        prop.setValueAtTime(5, [100, 50]);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);

        // keyframe_HOLD
        comp = proj.items.addComp("keyframe_HOLD", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 100);
        prop.setValueAtTime(2, 0);
        prop.setValueAtTime(4, 100);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);

        saveProject(proj, folder.fsName);

        // =================================================================
        // property_types.aep - Property value types (1D, 2D, 3D, rotation, scale)
        // =================================================================
        proj = createProject("property_types");

        // property_1D_opacity
        comp = proj.items.addComp("property_1D_opacity", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(5, 100);

        // property_2D_position
        comp = proj.items.addComp("property_2D_position", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 0]);
        prop.setValueAtTime(5, [100, 100]);

        // property_3D_position
        comp = proj.items.addComp("property_3D_position", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.threeDLayer = true;
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 0, 0]);
        prop.setValueAtTime(5, [100, 100, 500]);

        // property_rotation
        comp = proj.items.addComp("property_rotation", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Rotation");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(5, 360);

        // property_scale
        comp = proj.items.addComp("property_scale", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Scale");
        prop.setValueAtTime(0, [100, 100]);
        prop.setValueAtTime(5, [200, 200]);

        saveProject(proj, folder.fsName);

        // =================================================================
        // expression.aep - Expression samples
        // =================================================================
        proj = createProject("expression");

        // expression_enabled
        comp = proj.items.addComp("expression_enabled", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.expression = "wiggle(2, 50)";

        // expression_disabled
        comp = proj.items.addComp("expression_disabled", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.expression = "50";
        prop.expressionEnabled = false;

        // expression_time
        comp = proj.items.addComp("expression_time", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Rotation");
        prop.expression = "time * 36";

        saveProject(proj, folder.fsName);

        // =================================================================
        // effects.aep - Effects with different parameter types
        // =================================================================
        proj = createProject("effects");

        // effect_2dPoint
        comp = proj.items.addComp("effect_2dPoint", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        var effect = layer.property("Effects").addProperty("ADBE Lens Flare");

        // effect_3dPoint
        comp = proj.items.addComp("effect_3dPoint", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.threeDLayer = true;
        effect = layer.property("Effects").addProperty("CC Sphere");

        // effect_puppet
        comp = proj.items.addComp("effect_puppet", 200, 200, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 200, 200, 1);
        effect = layer.property("Effects").addProperty("ADBE FreePin3");

        saveProject(proj, folder.fsName);

        // =================================================================
        // keyframe_1D.aep - 1D keyframe ease scenarios
        // =================================================================
        proj = createProject("keyframe_1D");

        // keyframe_bezier_ease_in_out_1D
        comp = proj.items.addComp("keyframe_bezier_ease_in_out_1D", 100, 100, 1, 10, 24);
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

        // keyframe_bezier_asymmetric_ease_1D
        comp = proj.items.addComp("keyframe_bezier_asymmetric_ease_1D", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(5, 100);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setTemporalEaseAtKey(1, [new KeyframeEase(0, 16.67)], [new KeyframeEase(0, 90)]);
        prop.setTemporalEaseAtKey(2, [new KeyframeEase(0, 90)], [new KeyframeEase(0, 16.67)]);

        // keyframe_bezier_extreme_ease_1D
        comp = proj.items.addComp("keyframe_bezier_extreme_ease_1D", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(5, 100);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setTemporalEaseAtKey(1, [new KeyframeEase(0, 0.1)], [new KeyframeEase(0, 99)]);
        prop.setTemporalEaseAtKey(2, [new KeyframeEase(0, 99)], [new KeyframeEase(0, 0.1)]);

        // keyframe_bezier_multi_ease_1D
        comp = proj.items.addComp("keyframe_bezier_multi_ease_1D", 100, 100, 1, 10, 24);
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

        // keyframe_mixed_interpolation
        comp = proj.items.addComp("keyframe_mixed_interpolation", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 100);
        prop.setValueAtTime(3, 0);
        prop.setValueAtTime(6, 100);
        prop.setValueAtTime(9, 50);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.HOLD);
        prop.setInterpolationTypeAtKey(3, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.LINEAR);
        prop.setInterpolationTypeAtKey(4, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR);

        // keyframe_single
        comp = proj.items.addComp("keyframe_single", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(3, 75);

        // keyframe_bezier_nonzero_speed
        comp = proj.items.addComp("keyframe_bezier_nonzero_speed", 100, 100, 1, 10, 24);
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

        // keyframe_flat_value
        comp = proj.items.addComp("keyframe_flat_value", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 50);
        prop.setValueAtTime(5, 50);
        prop.setValueAtTime(9, 50);
        for (var fi = 1; fi <= 3; fi++) {
            prop.setInterpolationTypeAtKey(fi, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        }

        // keyframe_comp_boundaries
        comp = proj.items.addComp("keyframe_comp_boundaries", 100, 100, 1, 5, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(comp.duration - comp.frameDuration, 100);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setTemporalEaseAtKey(1, [new KeyframeEase(0, 50)], [new KeyframeEase(0, 50)]);
        prop.setTemporalEaseAtKey(2, [new KeyframeEase(0, 50)], [new KeyframeEase(0, 50)]);

        // keyframe_extrapolation
        comp = proj.items.addComp("keyframe_extrapolation", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(2, 20);
        prop.setValueAtTime(7, 80);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setTemporalEaseAtKey(1, [new KeyframeEase(0, 50)], [new KeyframeEase(0, 50)]);
        prop.setTemporalEaseAtKey(2, [new KeyframeEase(0, 50)], [new KeyframeEase(0, 50)]);

        // keyframe_bounce_pattern
        comp = proj.items.addComp("keyframe_bounce_pattern", 100, 100, 1, 10, 24);
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

        // =================================================================
        // keyframe_spatial.aep - 2D/3D spatial keyframe scenarios
        // =================================================================
        proj = createProject("keyframe_spatial");

        // keyframe_bezier_ease_2D_position
        comp = proj.items.addComp("keyframe_bezier_ease_2D_position", 200, 200, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 0]);
        prop.setValueAtTime(5, [200, 200]);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setTemporalEaseAtKey(1, [new KeyframeEase(0, 70)], [new KeyframeEase(0, 70)]);
        prop.setTemporalEaseAtKey(2, [new KeyframeEase(0, 70)], [new KeyframeEase(0, 70)]);

        // keyframe_spatial_bezier_arc
        comp = proj.items.addComp("keyframe_spatial_bezier_arc", 200, 200, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 100]);
        prop.setValueAtTime(5, [200, 100]);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setSpatialTangentsAtKey(1, [0, 0, 0], [60, -80, 0]);
        prop.setSpatialTangentsAtKey(2, [-60, -80, 0], [0, 0, 0]);

        // keyframe_spatial_bezier_s_curve
        comp = proj.items.addComp("keyframe_spatial_bezier_s_curve", 300, 300, 1, 10, 24);
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

        // keyframe_spatial_bezier_3D
        comp = proj.items.addComp("keyframe_spatial_bezier_3D", 200, 200, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.threeDLayer = true;
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 0, 0]);
        prop.setValueAtTime(5, [200, 200, -200]);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setSpatialTangentsAtKey(1, [0, 0, 0], [50, -50, -30]);
        prop.setSpatialTangentsAtKey(2, [-50, -50, 30], [0, 0, 0]);

        // keyframe_spatial_auto_bezier
        comp = proj.items.addComp("keyframe_spatial_auto_bezier", 300, 300, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [50, 250]);
        prop.setValueAtTime(3, [150, 50]);
        prop.setValueAtTime(6, [250, 250]);
        for (var ai = 1; ai <= 3; ai++) {
            prop.setInterpolationTypeAtKey(ai, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
            prop.setSpatialAutoBezierAtKey(ai, true);
        }

        // keyframe_spatial_continuous
        comp = proj.items.addComp("keyframe_spatial_continuous", 300, 300, 1, 10, 24);
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

        // keyframe_hold_2D_position
        comp = proj.items.addComp("keyframe_hold_2D_position", 200, 200, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 0]);
        prop.setValueAtTime(3, [200, 0]);
        prop.setValueAtTime(6, [200, 200]);
        prop.setValueAtTime(9, [0, 200]);
        for (var hi = 1; hi <= 4; hi++) {
            prop.setInterpolationTypeAtKey(hi, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);
        }

        // keyframe_linear_2D_position
        comp = proj.items.addComp("keyframe_linear_2D_position", 200, 200, 1, 10, 24);
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

        // =================================================================
        // keyframe_misc.aep - Roving, temporal auto-bezier, scale, color, separated
        // =================================================================
        proj = createProject("keyframe_misc");

        // keyframe_roving
        comp = proj.items.addComp("keyframe_roving", 300, 300, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [50, 150]);
        prop.setValueAtTime(3, [150, 50]);
        prop.setValueAtTime(6, [250, 150]);
        prop.setValueAtTime(9, [150, 250]);
        for (var ri = 1; ri <= 4; ri++) {
            prop.setInterpolationTypeAtKey(ri, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        }
        prop.setRovingAtKey(2, true);
        prop.setRovingAtKey(3, true);

        // keyframe_temporal_auto_bezier
        comp = proj.items.addComp("keyframe_temporal_auto_bezier", 100, 100, 1, 10, 24);
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

        // keyframe_temporal_continuous
        comp = proj.items.addComp("keyframe_temporal_continuous", 100, 100, 1, 10, 24);
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

        // keyframe_bezier_ease_scale
        comp = proj.items.addComp("keyframe_bezier_ease_scale", 100, 100, 1, 10, 24);
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

        // keyframe_color
        comp = proj.items.addComp("keyframe_color", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        var colorEffect = layer.property("Effects").addProperty("ADBE Color Control");
        prop = colorEffect.property(1);
        prop.setValueAtTime(0, [1, 0, 0, 1]);
        prop.setValueAtTime(5, [0, 0, 1, 1]);
        prop.setValueAtTime(9, [0, 1, 0, 1]);

        // keyframe_separated_dimensions
        comp = proj.items.addComp("keyframe_separated_dimensions", 200, 200, 1, 10, 24);
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

        // =================================================================
        // shape_basic.aep - Basic mask shapes
        // =================================================================
        proj = createProject("shape_basic");

        // shape_closed_square
        comp = proj.items.addComp("shape_closed_square", 400, 400, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 400, 400, 1);
        maskGroup = layer.property("ADBE Mask Parade");
        mask = maskGroup.addProperty("ADBE Mask Atom");
        myShape = new Shape();
        myShape.vertices = [[100, 100], [100, 300], [300, 300], [300, 100]];
        myShape.closed = true;
        mask.property("ADBE Mask Shape").setValue(myShape);

        // shape_closed_oval
        comp = proj.items.addComp("shape_closed_oval", 400, 400, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 400, 400, 1);
        maskGroup = layer.property("ADBE Mask Parade");
        mask = maskGroup.addProperty("ADBE Mask Atom");
        myShape = new Shape();
        myShape.vertices = [[200, 50], [100, 200], [200, 350], [300, 200]];
        myShape.inTangents = [[55.23, 0], [0, -55.23], [-55.23, 0], [0, 55.23]];
        myShape.outTangents = [[-55.23, 0], [0, 55.23], [55.23, 0], [0, -55.23]];
        myShape.closed = true;
        mask.property("ADBE Mask Shape").setValue(myShape);

        // shape_open
        comp = proj.items.addComp("shape_open", 400, 400, 1, 10, 24);
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

        // =================================================================
        // shape_feather.aep - Mask shapes with feather points
        // =================================================================
        proj = createProject("shape_feather");

        // shape_feather_points
        comp = proj.items.addComp("shape_feather_points", 400, 400, 1, 10, 24);
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

        // shape_feather_inner_hold
        comp = proj.items.addComp("shape_feather_inner_hold", 400, 400, 1, 10, 24);
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

        // =================================================================
        // shape_misc.aep - Animated shapes, many-point shapes, shape layer paths
        // =================================================================
        proj = createProject("shape_misc");

        // shape_animated
        comp = proj.items.addComp("shape_animated", 400, 400, 1, 10, 24);
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

        // shape_many_points
        comp = proj.items.addComp("shape_many_points", 4000, 4000, 1, 10, 24);
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
        myShape.featherSegLocs = [0, 128, 255, 256, 270, 299];
        myShape.featherRelSegLocs = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5];
        myShape.featherRadii = [10, 20, 30, 40, 50, 60];
        mask.property("ADBE Mask Shape").setValue(myShape);

        // shape_layer_path
        comp = proj.items.addComp("shape_layer_path", 400, 400, 1, 10, 24);
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

        $.writeln("Generated property/mask/shape samples in: " + folder.fsName);
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
            rqItem.applyTemplate(template);
        }
        if (settings) {
            rqItem.setSettings(settings);
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
            om.applyTemplate(template);
            // Re-fetch OutputModule after template application (bug workaround)
            om = rqItem.outputModule(omIndex);
        }
        if (settings) {
            om.setSettings(settings);
            // Re-fetch OutputModule after settings modification (bug workaround)
            om = rqItem.outputModule(omIndex);
        }
        return om;
    }

    function addRenderQueueComp(proj, compName, width, height, duration, frameRate) {
        var comp = proj.items.addComp(compName, width || 1920, height || 1080, 1, duration || 30, frameRate || 24);
        comp.bgColor = [0.2, 0.4, 0.6];
        var rqItem = proj.renderQueue.items.add(comp);
        var om = rqItem.outputModule(1);
        return {comp: comp, rqItem: rqItem, om: om};
    }

    function generateRenderQueueSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/renderqueue");
        var omFolder = ensureFolder(outputPath + "/output_module");
        var proj, q, downloadFolder;

        // Get user's Downloads folder for output paths
        try {
            downloadFolder = Folder.myDocuments.parent.fsName + "/Downloads";
        } catch (e) {
            downloadFolder = folder.fsName;
        }

        // =================================================================
        // render_settings.aep - Basic render setting variations (21 comps)
        // =================================================================
        proj = createProject("render_settings");

        q = addRenderQueueComp(proj, "base");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/Comp 1.mp4");

        q = addRenderQueueComp(proj, "current_settings");
        applyRenderSettings(q.rqItem, "Current Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "custom");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "color_depth_8");
        applyRenderSettings(q.rqItem, "Best Settings", {"Color Depth": 0});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "color_depth_16");
        applyRenderSettings(q.rqItem, "Best Settings", {"Color Depth": 1});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "color_depth_32");
        applyRenderSettings(q.rqItem, "Best Settings", {"Color Depth": 2});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "quality_current");
        applyRenderSettings(q.rqItem, "Best Settings", {"Quality": -1});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "quality_draft");
        applyRenderSettings(q.rqItem, "Best Settings", {"Quality": 1});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "quality_wireframe");
        applyRenderSettings(q.rqItem, "Best Settings", {"Quality": 0});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "effects_all_off");
        applyRenderSettings(q.rqItem, "Best Settings", {"Effects": 0});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "effects_all_on");
        applyRenderSettings(q.rqItem, "Best Settings", {"Effects": 1});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "proxy_use_current");
        applyRenderSettings(q.rqItem, "Best Settings", {"Proxy Use": 2});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "proxy_use_all_proxies");
        applyRenderSettings(q.rqItem, "Best Settings", {"Proxy Use": 1});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "proxy_use_comp_only");
        applyRenderSettings(q.rqItem, "Best Settings", {"Proxy Use": 3});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "solo_switches_off");
        applyRenderSettings(q.rqItem, "Best Settings", {"Solo Switches": 0});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "disk_cache_current");
        applyRenderSettings(q.rqItem, "Best Settings", {"Disk Cache": 2});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "motion_blur_current");
        applyRenderSettings(q.rqItem, "Best Settings", {"Motion Blur": 2});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "motion_blur_off");
        applyRenderSettings(q.rqItem, "Best Settings", {"Motion Blur": 0});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "frame_blending_current");
        applyRenderSettings(q.rqItem, "Best Settings", {"Frame Blending": 2});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "frame_blending_off");
        applyRenderSettings(q.rqItem, "Best Settings", {"Frame Blending": 0});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "guide_layers_current");
        applyRenderSettings(q.rqItem, "Best Settings", {"Guide Layers": 2});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        saveProject(proj, folder.fsName);

        // =================================================================
        // resolution.aep - Resolution variants (7 comps)
        // =================================================================
        proj = createProject("resolution");

        q = addRenderQueueComp(proj, "resolution_current");
        applyRenderSettings(q.rqItem, "Best Settings", {"Resolution": {x: 0, y: 0}});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "resolution_half");
        applyRenderSettings(q.rqItem, "Best Settings", {"Resolution": {x: 2, y: 2}});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "resolution_third");
        applyRenderSettings(q.rqItem, "Best Settings", {"Resolution": {x: 3, y: 3}});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "resolution_quarter");
        applyRenderSettings(q.rqItem, "Best Settings", {"Resolution": {x: 4, y: 4}});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "resolution_custom_7x3");
        applyRenderSettings(q.rqItem, "Best Settings", {"Resolution": {x: 7, y: 3}});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "resolution_custom_7x4");
        applyRenderSettings(q.rqItem, "Best Settings", {"Resolution": {x: 7, y: 4}});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "resolution_custom_8x3");
        applyRenderSettings(q.rqItem, "Best Settings", {"Resolution": {x: 8, y: 3}});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        saveProject(proj, folder.fsName);

        // =================================================================
        // field_render.aep - Field render + pulldown (7 comps)
        // Pulldown values: 1=WSSWW, 2=SSWWW, 3=SWWWS, 4=WWWSS, 5=WWSSW
        // =================================================================
        proj = createProject("field_render");

        q = addRenderQueueComp(proj, "field_render_lower");
        applyRenderSettings(q.rqItem, "Best Settings", {"Field Render": 2});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "field_render_upper");
        applyRenderSettings(q.rqItem, "Best Settings", {"Field Render": 1});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "pulldown_SSWWW");
        applyRenderSettings(q.rqItem, "Best Settings", {"Field Render": 1, "3:2 Pulldown": 2});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "pulldown_SWWWS");
        applyRenderSettings(q.rqItem, "Best Settings", {"Field Render": 1, "3:2 Pulldown": 3});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "pulldown_WSSWW");
        applyRenderSettings(q.rqItem, "Best Settings", {"Field Render": 1, "3:2 Pulldown": 1});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "pulldown_WWSSW");
        applyRenderSettings(q.rqItem, "Best Settings", {"Field Render": 1, "3:2 Pulldown": 5});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "pulldown_WWWSS");
        applyRenderSettings(q.rqItem, "Best Settings", {"Field Render": 1, "3:2 Pulldown": 4});
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        saveProject(proj, folder.fsName);

        // =================================================================
        // time_span.aep - Time span and duration settings (4 comps)
        // =================================================================
        proj = createProject("time_span");

        q = addRenderQueueComp(proj, "time_span_length_of_comp");
        applyRenderSettings(q.rqItem, "Best Settings", {"Time Span": 0});
        q.rqItem.setSetting("Use this frame rate", 30);
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "time_span_full_duration");
        applyRenderSettings(q.rqItem, "Best Settings", {
            "Time Span Start": 0,
            "Time Span Duration": 30
        });
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "time_span_custom_24s13f");
        applyRenderSettings(q.rqItem, "Best Settings", {
            "Time Span Start": 0,
            "Time Span Duration": 24 + 13/24  // 24s 13f
        });
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "time_span_custom_start_1s23f");
        applyRenderSettings(q.rqItem, "Best Settings", {
            "Time Span Start": 1 + 23/24,  // 1s 23f
            "Time Span Duration": 24 + 13/24  // 24s 13f
        });
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        saveProject(proj, folder.fsName);

        // =================================================================
        // frame_rate.aep - Frame rate overrides (3 comps)
        // "Frame Rate" is the boolean flag (0=comp rate, 1=custom rate)
        // "Use this frame rate" is the actual fps value when custom is enabled
        // =================================================================
        proj = createProject("frame_rate");

        q = addRenderQueueComp(proj, "frame_rate_24");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.rqItem.setSetting("Use this frame rate", 24);
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "frame_rate_30");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.rqItem.setSetting("Use this frame rate", 30);
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "frame_rate_29_97");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.rqItem.setSetting("Use this frame rate", 29.97);
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        saveProject(proj, folder.fsName);

        // =================================================================
        // templates.aep - Template-based settings + log (5 comps)
        // =================================================================
        proj = createProject("templates");

        q = addRenderQueueComp(proj, "template_draft");
        applyRenderSettings(q.rqItem, "Draft Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "template_dv");
        applyRenderSettings(q.rqItem, "DV Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "template_multi_machine");
        applyRenderSettings(q.rqItem, "Multi-Machine Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Multi-Machine Sequence");
        q.om.file = new File(downloadFolder + "/[compName]/[compName]_[#####].psd");

        q = addRenderQueueComp(proj, "log_plus_settings");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.rqItem.logType = LogType.ERRORS_AND_PER_FRAME_INFO;
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "log_plus_per_frame_info");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.rqItem.logType = LogType.ERRORS_AND_PER_FRAME_INFO;
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        saveProject(proj, folder.fsName);

        // =================================================================
        // skip_frames.aep - Skip frame values (4 comps)
        // All use: Time Span: 0, Frame Rate: 1, Use this frame rate: 30
        // =================================================================
        proj = createProject("skip_frames");

        q = addRenderQueueComp(proj, "skip_frames_0");
        applyRenderSettings(q.rqItem, "Best Settings", {"Time Span": 0});
        q.rqItem.setSetting("Use this frame rate", 30);
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");
        q.rqItem.skipFrames = 0;

        q = addRenderQueueComp(proj, "skip_frames_1");
        applyRenderSettings(q.rqItem, "Best Settings", {"Time Span": 0});
        q.rqItem.setSetting("Use this frame rate", 30);
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");
        q.rqItem.skipFrames = 1;

        q = addRenderQueueComp(proj, "skip_frames_2");
        applyRenderSettings(q.rqItem, "Best Settings", {"Time Span": 0});
        q.rqItem.setSetting("Use this frame rate", 30);
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");
        q.rqItem.skipFrames = 2;

        q = addRenderQueueComp(proj, "skip_frames_3");
        applyRenderSettings(q.rqItem, "Best Settings", {"Time Span": 0});
        q.rqItem.setSetting("Use this frame rate", 30);
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");
        q.rqItem.skipFrames = 3;

        saveProject(proj, folder.fsName);

        // =================================================================
        // output_paths.aep - Output path patterns (9 comps)
        // =================================================================
        proj = createProject("output_paths");

        q = addRenderQueueComp(proj, "output_path_compName");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "output_path_compName_omName");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName]_[outputModuleName].mp4");

        q = addRenderQueueComp(proj, "output_path_subfolder");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName]/[compName].mp4");

        q = addRenderQueueComp(proj, "output_path_widthxheight");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName]_[width]x[height].mp4");

        q = addRenderQueueComp(proj, "output_path_pixelAspect");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName]_[pixelAspect].mp4");

        q = addRenderQueueComp(proj, "output_path_datetime");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName]_[dateYear]-[dateMonth]-[dateDay]_[timeHours]-[timeMins]-[timeSecs].mp4");

        q = addRenderQueueComp(proj, "output_path_projectName_compName");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[projectName]_[compName].mp4");

        q = addRenderQueueComp(proj, "output_path_projectFolder");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File("[projectFolder]/[compName].mp4");

        q = addRenderQueueComp(proj, "output_path_all_fields");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[projectFolder]\__[projectName]__[compName]__[renderSettingsName]__[outputModuleName]__[width]__[height]__[frameRate]__[aspectRatio]__[startFrame]__[endFrame]__[durationFrames]__[#####]__[startTimecode]__[endTimecode]__[durationTimecode]__[channels]__[projectColorDepth]__[outputColorDepth]__[compressor]__[fieldOrder]__[pulldownPhase]__[dateYear]__[dateMonth]__[dateDay]__[timeHour]__[timeMins]__[timeSecs]__[timeZone].[fileExtension]");

        saveProject(proj, folder.fsName);

        // =================================================================
        // om_audio.aep - Audio-related OM settings (10 comps)
        // =================================================================
        proj = createProject("om_audio");

        q = addRenderQueueComp(proj, "audio_output_off");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {"Output Audio": "1"});
        q.om.file = new File(downloadFolder + "/[compName].avi");

        q = addRenderQueueComp(proj, "audio_output_on");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {"Output Audio": "2"});
        q.om.file = new File(downloadFolder + "/[compName].avi");

        q = addRenderQueueComp(proj, "audio_8bit");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {"Output Audio": "2", "Audio Bit Depth": 1});
        q.om.file = new File(downloadFolder + "/[compName].avi");

        q = addRenderQueueComp(proj, "audio_32bit");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {"Output Audio": "2", "Audio Bit Depth": 4});
        q.om.file = new File(downloadFolder + "/[compName].avi");

        q = addRenderQueueComp(proj, "audio_mono");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {"Output Audio": "2", "Audio Channels": 1});
        q.om.file = new File(downloadFolder + "/[compName].avi");

        q = addRenderQueueComp(proj, "audio_8000hz");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {"Output Audio": "2", "Audio Sample Rate": 8000});
        q.om.file = new File(downloadFolder + "/[compName].avi");

        q = addRenderQueueComp(proj, "audio_16000hz");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {"Output Audio": "2", "Audio Sample Rate": 16000});
        q.om.file = new File(downloadFolder + "/[compName].avi");

        q = addRenderQueueComp(proj, "audio_22050hz");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {"Output Audio": "2", "Audio Sample Rate": 22050});
        q.om.file = new File(downloadFolder + "/[compName].avi");

        q = addRenderQueueComp(proj, "audio_32000hz");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {"Output Audio": "2", "Audio Sample Rate": 32000});
        q.om.file = new File(downloadFolder + "/[compName].avi");

        q = addRenderQueueComp(proj, "audio_96000hz");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {"Output Audio": "2", "Audio Sample Rate": 96000});
        q.om.file = new File(downloadFolder + "/[compName].avi");

        saveProject(proj, omFolder.fsName);

        // =================================================================
        // om_video.aep - Video-related OM settings (3 comps)
        // =================================================================
        proj = createProject("om_video");

        // "Channels", "Color", and "Format" are read-only in ExtendScript's
        // setSettings/setSetting. Use output module templates to set them.
        // "Straight" is a custom template created in the AE UI.
        q = addRenderQueueComp(proj, "channels_alpha");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Alpha Only");
        q.om.file = new File(downloadFolder + "/[compName].avi");

        q = addRenderQueueComp(proj, "color_straight_unmatted");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Straight");
        q.om.file = new File(downloadFolder + "/[compName]/[compName]_[#####].tif");

        q = addRenderQueueComp(proj, "custom_h264");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        saveProject(proj, omFolder.fsName);

        // =================================================================
        // om_crop.aep - Crop settings (2 comps)
        // =================================================================
        proj = createProject("om_crop");

        q = addRenderQueueComp(proj, "crop_checked");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {
            "Crop": true,
            "Crop Top": 10,
            "Crop Left": 10,
            "Crop Bottom": 10,
            "Crop Right": 10
        });
        q.om.file = new File(downloadFolder + "/[compName].avi");

        q = addRenderQueueComp(proj, "crop_use_roi_checked");
        q.comp.regionOfInterest = [100, 100, 800, 600];
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {"Crop": true});
        q.om.file = new File(downloadFolder + "/[compName].avi");

        saveProject(proj, omFolder.fsName);

        // =================================================================
        // om_resize.aep - Resize settings (3 comps)
        // =================================================================
        proj = createProject("om_resize");

        q = addRenderQueueComp(proj, "resize_checked");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {
            "Resize": true,
            "Resize to": [1280, 720]
        });
        q.om.file = new File(downloadFolder + "/[compName].avi");

        q = addRenderQueueComp(proj, "resize_lock_aspect_ratio_unchecked");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {
            "Resize": true,
            "Resize to": [1280, 800]
        });
        q.om.file = new File(downloadFolder + "/[compName].avi");

        q = addRenderQueueComp(proj, "resize_quality_low");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "Lossless", {
            "Resize": true,
            "Resize to": [640, 480],
            "Resize Quality": 0
        });
        q.om.file = new File(downloadFolder + "/[compName].avi");

        saveProject(proj, omFolder.fsName);

        // =================================================================
        // om_misc.aep - Miscellaneous OM settings (2 comps)
        // =================================================================
        proj = createProject("om_misc");

        q = addRenderQueueComp(proj, "include_source_xmp_data_on");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.includeSourceXMP = true;
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        q = addRenderQueueComp(proj, "include_project_link_off");
        applyRenderSettings(q.rqItem, "Best Settings");
        q.om = applyOutputModuleSettings(q.rqItem, "H.264 - Match Render Settings - 15 Mbps");
        q.om.file = new File(downloadFolder + "/[compName].mp4");

        saveProject(proj, omFolder.fsName);

        $.writeln("Generated renderqueue samples in: " + folder.fsName);
        $.writeln("Generated output_module samples in: " + omFolder.fsName);
    }

    // =========================================================================
    // Selection Samples - NOT GENERATED
    // Selection state (otln chunks) is only written to .aep files when layers
    // or properties are interactively selected in the AE UI at save time.
    // Setting .selected = true via ExtendScript does NOT produce otln chunks
    // in the saved binary. These samples must be authored manually in AE.
    // See: samples/models/selection/ and samples/models/composition/selection_*
    // =========================================================================

    // =========================================================================
    // View Samples
    // Covers: ViewOptions (channels, exposure, fastPreview, zoom, toggles)
    // ViewOptions are per-viewer; only the active viewer's settings survive.
    // =========================================================================

    function generateViewSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/view");
        var proj, comp, opts;

        // -----------------------------------------------------------------
        // Channels (2 files: default + non-default)
        // -----------------------------------------------------------------
        proj = createProject("channels_rgb");
        comp = proj.items.addComp("Comp 1", 1920, 1080, 1, 10, 24);
        comp.openInViewer();
        opts = app.activeViewer.views[0].options;
        opts.channels = ChannelType.CHANNEL_RGB;
        saveProject(proj, folder.fsName);

        proj = createProject("channels_alpha");
        comp = proj.items.addComp("Comp 1", 1920, 1080, 1, 10, 24);
        comp.openInViewer();
        opts = app.activeViewer.views[0].options;
        opts.channels = ChannelType.CHANNEL_ALPHA;
        saveProject(proj, folder.fsName);

        // -----------------------------------------------------------------
        // Exposure (2 files: zero + negative)
        // -----------------------------------------------------------------
        proj = createProject("exposure_0.0");
        comp = proj.items.addComp("Comp 1", 1920, 1080, 1, 10, 24);
        comp.openInViewer();
        opts = app.activeViewer.views[0].options;
        opts.exposure = 0;
        saveProject(proj, folder.fsName);

        proj = createProject("exposure_-40.0");
        comp = proj.items.addComp("Comp 1", 1920, 1080, 1, 10, 24);
        comp.openInViewer();
        opts = app.activeViewer.views[0].options;
        opts.exposure = -40;
        saveProject(proj, folder.fsName);

        // -----------------------------------------------------------------
        // Fast Preview (2 files: off + wireframe)
        // -----------------------------------------------------------------
        proj = createProject("fast_preview_off");
        comp = proj.items.addComp("Comp 1", 1920, 1080, 1, 10, 24);
        comp.openInViewer();
        opts = app.activeViewer.views[0].options;
        opts.fastPreview = FastPreviewType.FP_OFF;
        saveProject(proj, folder.fsName);

        proj = createProject("fast_preview_wireframe");
        comp = proj.items.addComp("Comp 1", 1920, 1080, 1, 10, 24);
        comp.openInViewer();
        opts = app.activeViewer.views[0].options;
        opts.fastPreview = FastPreviewType.FP_WIREFRAME;
        saveProject(proj, folder.fsName);

        // -----------------------------------------------------------------
        // Zoom (2 files: 25% + 100%)
        // -----------------------------------------------------------------
        proj = createProject("zoom_25");
        comp = proj.items.addComp("Comp 1", 1920, 1080, 1, 10, 24);
        comp.openInViewer();
        opts = app.activeViewer.views[0].options;
        opts.zoom = 0.25;
        saveProject(proj, folder.fsName);

        proj = createProject("zoom_100");
        comp = proj.items.addComp("Comp 1", 1920, 1080, 1, 10, 24);
        comp.openInViewer();
        opts = app.activeViewer.views[0].options;
        opts.zoom = 1.0;
        saveProject(proj, folder.fsName);

        // -----------------------------------------------------------------
        // Boolean toggles - consolidated (2 files)
        // -----------------------------------------------------------------
        proj = createProject("view_toggles_on");
        comp = proj.items.addComp("Comp 1", 1920, 1080, 1, 10, 24);
        comp.openInViewer();
        opts = app.activeViewer.views[0].options;
        opts.checkerboards = true;
        opts.guidesLocked = true;
        opts.guidesSnap = true;
        opts.guidesVisibility = true;
        opts.rulers = true;
        saveProject(proj, folder.fsName);

        proj = createProject("view_toggles_off");
        comp = proj.items.addComp("Comp 1", 1920, 1080, 1, 10, 24);
        comp.openInViewer();
        opts = app.activeViewer.views[0].options;
        opts.checkerboards = false;
        opts.guidesLocked = false;
        opts.guidesSnap = false;
        opts.guidesVisibility = false;
        opts.rulers = false;
        saveProject(proj, folder.fsName);

        $.writeln("Generated view samples in: " + folder.fsName);
    }

    // =========================================================================
    // Essential Graphics Samples
    // Covers: motionGraphicsTemplateName, addToMotionGraphicsTemplate,
    //   addToMotionGraphicsTemplateAs, setMotionGraphicsControllerName,
    //   Expression Controls, Layer Overrides
    // =========================================================================

    function generateEssentialGraphicsSamples(outputPath) {
        var folder = ensureFolder(outputPath + "/essential_graphics");
        var proj, primary, main, layer, prop;

        /**
         * Create a standard EG setup: primary comp with a solid + Fill effect,
         * nested into a main comp. Comp names include a prefix for uniqueness.
         */
        function egSetup(prefix) {
            primary = proj.items.addComp(prefix, 1000, 1000, 1, 10, 24);
            layer = primary.layers.addSolid(
                [0.5, 0.5, 0.5], "Gray Solid 1", 1000, 1000, 1
            );
            layer.property("ADBE Effect Parade").addProperty("ADBE Fill");
            main = proj.items.addComp(prefix + "_main", 1000, 1000, 1, 10, 24);
            main.layers.add(primary);
        }

        // -----------------------------------------------------------------
        // eg_fill.aep: Fill effect EGP variants (4 comps)
        // -----------------------------------------------------------------
        proj = createProject("eg_fill");

        // fill_color_added: Fill > Color added to EGP
        egSetup("fill_color_added");
        prop = layer.property("ADBE Effect Parade")
                    .property("ADBE Fill")
                    .property("ADBE Fill-0002");
        prop.addToMotionGraphicsTemplate(primary);

        // fill_color_renamed: Fill > Color added then renamed
        egSetup("fill_color_renamed");
        prop = layer.property("ADBE Effect Parade")
                    .property("ADBE Fill")
                    .property("ADBE Fill-0002");
        prop.addToMotionGraphicsTemplateAs(primary, "BG color");

        // fill_and_opacity_added: Fill > Color and Fill > Opacity added
        egSetup("fill_and_opacity_added");
        var colorProp = layer.property("ADBE Effect Parade")
                             .property("ADBE Fill")
                             .property("ADBE Fill-0002");
        var opacityProp = layer.property("ADBE Effect Parade")
                               .property("ADBE Fill")
                               .property("ADBE Fill-0005");
        colorProp.addToMotionGraphicsTemplateAs(primary, "BG color");
        opacityProp.addToMotionGraphicsTemplate(primary);

        // fill_color_changed_on_comp: Fill > Color added, value overridden
        egSetup("fill_color_changed_on_comp");
        prop = layer.property("ADBE Effect Parade")
                    .property("ADBE Fill")
                    .property("ADBE Fill-0002");
        prop.addToMotionGraphicsTemplateAs(primary, "BG color");
        var mainLayer = main.layer(1);
        var epGroup = mainLayer.property("ADBE Layer Overrides");
        if (epGroup.numProperties > 0) {
            epGroup.property(1).setValue([1.0, 0.0, 0.0, 1.0]);
        }

        saveProject(proj, folder.fsName);

        // -----------------------------------------------------------------
        // eg_controllers.aep: Controller types + multiple (7 comps)
        // -----------------------------------------------------------------
        proj = createProject("eg_controllers");

        // checkbox_controller
        egSetup("checkbox_controller");
        layer.property("ADBE Effect Parade").addProperty("ADBE Checkbox Control");
        prop = layer.property("ADBE Effect Parade")
                    .property("ADBE Checkbox Control")
                    .property("ADBE Checkbox Control-0001");
        prop.addToMotionGraphicsTemplateAs(primary, "Toggle Visibility");

        // slider_controller
        egSetup("slider_controller");
        layer.property("ADBE Effect Parade").addProperty("ADBE Slider Control");
        prop = layer.property("ADBE Effect Parade")
                    .property("ADBE Slider Control")
                    .property("ADBE Slider Control-0001");
        prop.addToMotionGraphicsTemplateAs(primary, "Intensity");

        // color_controller
        egSetup("color_controller");
        layer.property("ADBE Effect Parade").addProperty("ADBE Color Control");
        prop = layer.property("ADBE Effect Parade")
                    .property("ADBE Color Control")
                    .property("ADBE Color Control-0001");
        prop.addToMotionGraphicsTemplateAs(primary, "Custom Color");

        // point_controller
        egSetup("point_controller");
        layer.property("ADBE Effect Parade").addProperty("ADBE Point Control");
        prop = layer.property("ADBE Effect Parade")
                    .property("ADBE Point Control")
                    .property("ADBE Point Control-0001");
        prop.addToMotionGraphicsTemplateAs(primary, "Center Point");

        // dropdown_controller
        egSetup("dropdown_controller");
        var effect = layer.property("ADBE Effect Parade")
                         .addProperty("ADBE Dropdown Control");
        effect.property(1).addToMotionGraphicsTemplateAs(primary, "Style");

        // text_source_text (text layer, not solid)
        primary = proj.items.addComp("text_source_text", 1000, 1000, 1, 10, 24);
        var textLayer = primary.layers.addText("Sample Text");
        var sourceText = textLayer.property("ADBE Text Properties")
                                  .property("ADBE Text Document");
        sourceText.addToMotionGraphicsTemplateAs(primary, "Title Text");
        main = proj.items.addComp("text_source_text_main", 1000, 1000, 1, 10, 24);
        main.layers.add(primary);

        // multiple_controllers: Fill Color + Opacity + Brightness
        egSetup("multiple_controllers");
        layer.property("ADBE Effect Parade")
             .addProperty("ADBE Brightness & Contrast 2");
        var fillColor = layer.property("ADBE Effect Parade")
                             .property("ADBE Fill")
                             .property("ADBE Fill-0002");
        var layerOpacity = layer.property("ADBE Transform Group")
                                .property("ADBE Opacity");
        var brightness = layer.property("ADBE Effect Parade")
                              .property("ADBE Brightness & Contrast 2")
                              .property("ADBE Brightness & Contrast 2-0001");
        fillColor.addToMotionGraphicsTemplateAs(primary, "Background Color");
        layerOpacity.addToMotionGraphicsTemplateAs(primary, "Layer Opacity");
        brightness.addToMotionGraphicsTemplateAs(primary, "Brightness");

        saveProject(proj, folder.fsName);

        // -----------------------------------------------------------------
        // eg_transform.aep: Transform property EGP variants (2 comps)
        // -----------------------------------------------------------------
        proj = createProject("eg_transform");

        // transform_opacity
        egSetup("transform_opacity");
        prop = layer.property("ADBE Transform Group")
                    .property("ADBE Opacity");
        prop.addToMotionGraphicsTemplate(primary);

        // transform_position
        egSetup("transform_position");
        prop = layer.property("ADBE Transform Group")
                    .property("ADBE Position");
        prop.addToMotionGraphicsTemplate(primary);

        saveProject(proj, folder.fsName);

        // -----------------------------------------------------------------
        // eg_misc.aep: Miscellaneous EGP scenarios (5 comps)
        // -----------------------------------------------------------------
        proj = createProject("eg_misc");

        // base: comp with Fill, no EGP
        egSetup("base");

        // custom_template_name
        egSetup("custom_template_name");
        primary.motionGraphicsTemplateName = "My Custom Template";
        prop = layer.property("ADBE Effect Parade")
                    .property("ADBE Fill")
                    .property("ADBE Fill-0002");
        prop.addToMotionGraphicsTemplate(primary);

        // no_essential_properties: template name set, no controllers
        egSetup("no_essential_properties");
        primary.motionGraphicsTemplateName = "Empty Template";

        // controller_renamed: Fill > Color added, then controller renamed
        egSetup("controller_renamed");
        prop = layer.property("ADBE Effect Parade")
                    .property("ADBE Fill")
                    .property("ADBE Fill-0002");
        prop.addToMotionGraphicsTemplate(primary);
        primary.setMotionGraphicsControllerName(1, "Renamed Color");

        // two_layers: EGP from two different layers
        primary = proj.items.addComp("two_layers", 1000, 1000, 1, 10, 24);
        var layer1 = primary.layers.addSolid(
            [0.5, 0.5, 0.5], "Solid 1", 1000, 1000, 1
        );
        var layer2 = primary.layers.addSolid(
            [0.3, 0.3, 0.3], "Solid 2", 1000, 1000, 1
        );
        layer1.property("ADBE Effect Parade").addProperty("ADBE Fill");
        layer2.property("ADBE Effect Parade").addProperty("ADBE Fill");
        var color1 = layer1.property("ADBE Effect Parade")
                           .property("ADBE Fill")
                           .property("ADBE Fill-0002");
        var color2 = layer2.property("ADBE Effect Parade")
                           .property("ADBE Fill")
                           .property("ADBE Fill-0002");
        color1.addToMotionGraphicsTemplateAs(primary, "Color Layer 1");
        color2.addToMotionGraphicsTemplateAs(primary, "Color Layer 2");
        main = proj.items.addComp("two_layers_main", 1000, 1000, 1, 10, 24);
        main.layers.add(primary);

        saveProject(proj, folder.fsName);

        $.writeln("Generated essential graphics samples in: " + folder.fsName);
    }

    // =========================================================================
    // Main Execution
    // =========================================================================

    function main() {
        var scriptFile = new File($.fileName);
        var scriptPath = scriptFile.parent.fsName;
        var outputPath = scriptPath + "/../../samples/models";
        ensureFolder(outputPath);

        $.writeln("=== Generating CONSOLIDATED Model Samples ===");

        generateProjectSamples(outputPath);
        $.writeln("Project samples done");

        generateCompositionSamples(outputPath);
        $.writeln("Composition samples done");

        generateLayerSamples(outputPath);
        $.writeln("Layer samples done");

        generateFootageSamples(outputPath);
        $.writeln("Footage samples done");

        generateFolderSamples(outputPath);
        $.writeln("Folder samples done");

        generateMarkerSamples(outputPath);
        $.writeln("Marker samples done");

        generatePropertySamples(outputPath);
        $.writeln("Property samples done");

        generateRenderQueueSamples(outputPath);
        $.writeln("Render queue samples done");

        // Selection samples skipped - must be authored manually in AE (see comment above)

        generateViewSamples(outputPath);
        $.writeln("View samples done");

        generateEssentialGraphicsSamples(outputPath);
        $.writeln("Essential graphics samples done");

        $.writeln("=== All consolidated model samples generated ===");
    }

    main();

})();
