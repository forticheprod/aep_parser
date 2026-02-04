/**
 * Generate Test Samples for aep_parser Model Testing
 * 
 * Creates ONE .aep file per test case.
 * 
 * Covers ALL attributes from export_project_json.jsx.
 * 
 * Usage:
 *   1. Open After Effects 2019+ (some samples need at least this version)
 *   2. Run this script: File > Scripts > Run Script File
 *   3. Select the 'models' folder in samples/
 *   4. Projects will be saved to samples/models/<type>/<attribute>.aep
 */

(function() {
    "use strict";

    // =========================================================================
    // Utility Functions
    // =========================================================================

    function createProject() {
        if (app.project) {
            app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
        }
        return app.newProject();
    }

    function saveProject(project, filePath) {
        var file = new File(filePath);
        project.save(file);
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
        proj = createProject();
        proj.bitsPerChannel = 8;
        saveProject(proj, folder.fsName + "/bitsPerChannel_8.aep");

        // bitsPerChannel = 16
        proj = createProject();
        // 16 bits is not supported in OCIO mode
        try {
            proj.colorManagementSystem = 0; // Adobe
        } catch (e) {}
        proj.bitsPerChannel = 16;
        saveProject(proj, folder.fsName + "/bitsPerChannel_16.aep");

        // bitsPerChannel = 32
        proj = createProject();
        proj.bitsPerChannel = 32;
        saveProject(proj, folder.fsName + "/bitsPerChannel_32.aep");

        // compensateForSceneReferredProfiles (CC 2019+)
        proj = createProject();
        proj.compensateForSceneReferredProfiles = true;
        saveProject(proj, folder.fsName + "/compensateForSceneReferredProfiles_true.aep");

        // displayStartFrame
        proj = createProject();
        proj.displayStartFrame = 1;
        saveProject(proj, folder.fsName + "/displayStartFrame_1.aep");

        // expressionEngine (CC 2019+)
        proj = createProject();
        proj.expressionEngine = "javascript-1.0";
        saveProject(proj, folder.fsName + "/expressionEngine_javascript.aep");

        // feetFramesFilmType
        proj = createProject();
        proj.framesUseFeetFrames = true;
        proj.feetFramesFilmType = FeetFramesFilmType.MM35;
        saveProject(proj, folder.fsName + "/feetFramesFilmType_MM35.aep");

        // footageTimecodeDisplayStartType
        proj = createProject();
        proj.footageTimecodeDisplayStartType = FootageTimecodeDisplayStartType.FTCS_USE_SOURCE_MEDIA;
        saveProject(proj, folder.fsName + "/footageTimecodeDisplayStartType_source.aep");

        // framesCountType
        proj = createProject();
        proj.framesCountType = FramesCountType.FC_START_0;
        saveProject(proj, folder.fsName + "/framesCountType_start0.aep");

        // framesUseFeetFrames
        proj = createProject();
        proj.framesUseFeetFrames = true;
        saveProject(proj, folder.fsName + "/framesUseFeetFrames_true.aep");

        // gpuAccelType (CC 2015.3+)
        proj = createProject();
        proj.gpuAccelType = GpuAccelType.CUDA;
        saveProject(proj, folder.fsName + "/gpuAccelType_cuda.aep");

        // linearBlending
        proj = createProject();
        proj.bitsPerChannel = 32;
        proj.linearBlending = true;
        saveProject(proj, folder.fsName + "/linearBlending_true.aep");

        // linearizeWorkingSpace (CC 2019+)
        proj = createProject();
        proj.bitsPerChannel = 32;
        proj.linearizeWorkingSpace = true;
        saveProject(proj, folder.fsName + "/linearizeWorkingSpace_true.aep");

        // timeDisplayType = FRAMES
        proj = createProject();
        proj.timeDisplayType = TimeDisplayType.FRAMES;
        saveProject(proj, folder.fsName + "/timeDisplayType_frames.aep");

        // timeDisplayType = TIMECODE
        proj = createProject();
        proj.timeDisplayType = TimeDisplayType.TIMECODE;
        saveProject(proj, folder.fsName + "/timeDisplayType_timecode.aep");

        // transparencyGridThumbnails
        proj = createProject();
        proj.transparencyGridThumbnails = true;
        saveProject(proj, folder.fsName + "/transparencyGridThumbnails_true.aep");

        // workingGamma
        proj = createProject();
        proj.workingGamma = 2.4;
        saveProject(proj, folder.fsName + "/workingGamma_2.4.aep");

        // workingSpace (CC 2019+)
        proj = createProject();
        proj.workingSpace = "sRGB IEC61966-2.1";
        saveProject(proj, folder.fsName + "/workingSpace_sRGB.aep");

        // --- CC 2024+ Color Management Attributes ---
        // These are undocumented and only available in CC 2024+

        // colorManagementSystem = 0 (Adobe)
        proj = createProject();
        proj.colorManagementSystem = 0;
        saveProject(proj, folder.fsName + "/colorManagementSystem_adobe.aep");

        // colorManagementSystem = 1 (OCIO) (CC 2024+)
        proj = createProject();
        proj.colorManagementSystem = 1;
        saveProject(proj, folder.fsName + "/colorManagementSystem_ocio.aep");

        // lutInterpolationMethod = 0 (Trilinear)
        proj = createProject();
        proj.lutInterpolationMethod = 0;
        saveProject(proj, folder.fsName + "/lutInterpolationMethod_trilinear.aep");

        // lutInterpolationMethod = 1 (Tetrahedral - requires GPU acceleration)
        proj = createProject();
        proj.gpuAccelType = GpuAccelType.OPENCL; // Enable GPU for tetrahedral
        proj.lutInterpolationMethod = 1;
        saveProject(proj, folder.fsName + "/lutInterpolationMethod_tetrahedral.aep");

        // ocioConfigurationFile (requires OCIO mode)
        proj = createProject();
        proj.colorManagementSystem = 1; // OCIO mode
        var ocioConfigPath = outputPath + "/../assets/config.ocio";
        var ocioFile = new File(ocioConfigPath);
        proj.ocioConfigurationFile = ocioFile.fsName;
        saveProject(proj, folder.fsName + "/ocioConfigurationFile_custom.aep");

        // workingSpace with OCIO (uses OCIO color space names)
        proj = createProject();
        proj.colorManagementSystem = 1; // OCIO mode
        var ocioConfigPath = outputPath + "/../assets/config.ocio";
        var ocioFile = new File(ocioConfigPath);
        proj.ocioConfigurationFile = ocioFile.fsName;
        proj.workingSpace = "ACEScct";
        saveProject(proj, folder.fsName + "/workingSpace_ocio_acescct.aep");

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
        proj = createProject();
        c = proj.items.addComp("OriginalName", 100, 100, 1, 1, 24);
        c.name = "RenamedComp";
        saveProject(proj, folder.fsName + "/name_renamed.aep");

        // comment
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.comment = "Test comment";
        saveProject(proj, folder.fsName + "/comment.aep");

        // label
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.label = 5;
        saveProject(proj, folder.fsName + "/label_5.aep");

        // --- AVITEM_ATTRS ---

        // duration
        proj = createProject();
        proj.items.addComp("TestComp", 100, 100, 1, 60, 24);
        saveProject(proj, folder.fsName + "/duration_60.aep");

        // frameRate
        proj = createProject();
        proj.items.addComp("TestComp", 100, 100, 1, 1, 30);
        saveProject(proj, folder.fsName + "/frameRate_30.aep");

        proj = createProject();
        proj.items.addComp("TestComp", 100, 100, 1, 1, 23.976);
        saveProject(proj, folder.fsName + "/frameRate_23976.aep");

        proj = createProject();
        proj.items.addComp("TestComp", 100, 100, 1, 1, 60);
        saveProject(proj, folder.fsName + "/frameRate_60.aep");

        // height/width
        proj = createProject();
        proj.items.addComp("TestComp", 1920, 1080, 1, 1, 24);
        saveProject(proj, folder.fsName + "/size_1920x1080.aep");

        proj = createProject();
        proj.items.addComp("TestComp", 2048, 872, 1, 1, 24);
        saveProject(proj, folder.fsName + "/size_2048x872.aep");

        // pixelAspect
        proj = createProject();
        proj.items.addComp("TestComp", 100, 100, 0.75, 1, 24);
        saveProject(proj, folder.fsName + "/pixelAspect_0.75.aep");

        proj = createProject();
        proj.items.addComp("TestComp", 100, 100, 2.0, 1, 24);
        saveProject(proj, folder.fsName + "/pixelAspect_2.aep");

        // --- COMPITEM_ATTRS ---

        // bgColor
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.bgColor = [1, 0, 0];
        saveProject(proj, folder.fsName + "/bgColor_red.aep");

        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.bgColor = [0.2, 0.4, 0.6];
        saveProject(proj, folder.fsName + "/bgColor_custom.aep");

        // displayStartFrame
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        c.displayStartFrame = 100;
        saveProject(proj, folder.fsName + "/displayStartFrame_100.aep");

        // displayStartTime
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        c.displayStartTime = 10;
        saveProject(proj, folder.fsName + "/displayStartTime_10.aep");

        // draft3d
        // Skipped: Does not seem to work as expected, value stays false
        // proj = createProject();
        // c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        // c.draft3d = true;
        // saveProject(proj, folder.fsName + "/draft3d_true.aep");

        // dropFrame
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 29.97);
        c.dropFrame = true;
        saveProject(proj, folder.fsName + "/dropFrame_true.aep");

        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 29.97);
        c.dropFrame = false;
        saveProject(proj, folder.fsName + "/dropFrame_false.aep");

        // frameBlending
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.frameBlending = true;
        saveProject(proj, folder.fsName + "/frameBlending_true.aep");

        // hideShyLayers
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.hideShyLayers = true;
        saveProject(proj, folder.fsName + "/hideShyLayers_true.aep");

        // motionBlur
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.motionBlur = true;
        saveProject(proj, folder.fsName + "/motionBlur_true.aep");

        // motionBlurAdaptiveSampleLimit
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.motionBlurAdaptiveSampleLimit = 256;
        saveProject(proj, folder.fsName + "/motionBlurAdaptiveSampleLimit_256.aep");

        // motionBlurSamplesPerFrame
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.motionBlurSamplesPerFrame = 32;
        saveProject(proj, folder.fsName + "/motionBlurSamplesPerFrame_32.aep");

        // preserveNestedFrameRate
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.preserveNestedFrameRate = true;
        saveProject(proj, folder.fsName + "/preserveNestedFrameRate_true.aep");

        // preserveNestedResolution
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.preserveNestedResolution = true;
        saveProject(proj, folder.fsName + "/preserveNestedResolution_true.aep");

        // resolutionFactor
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.resolutionFactor = [2, 2];
        saveProject(proj, folder.fsName + "/resolutionFactor_half.aep");

        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.resolutionFactor = [4, 4];
        saveProject(proj, folder.fsName + "/resolutionFactor_quarter.aep");

        // shutterAngle
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.shutterAngle = 180;
        saveProject(proj, folder.fsName + "/shutterAngle_180.aep");

        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.shutterAngle = 360;
        saveProject(proj, folder.fsName + "/shutterAngle_360.aep");

        // shutterPhase
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 1, 24);
        c.shutterPhase = -90;
        saveProject(proj, folder.fsName + "/shutterPhase_minus90.aep");

        // workAreaStart
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        c.workAreaStart = 5;
        saveProject(proj, folder.fsName + "/workAreaStart_5.aep");

        // workAreaDuration
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        c.workAreaDuration = 10;
        saveProject(proj, folder.fsName + "/workAreaDuration_10.aep");

        // time
        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        c.time = 0;
        saveProject(proj, folder.fsName + "/time_0.aep");

        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        c.time = 5;
        saveProject(proj, folder.fsName + "/time_5.aep");

        proj = createProject();
        c = proj.items.addComp("TestComp", 100, 100, 1, 30, 24);
        c.time = 15;
        saveProject(proj, folder.fsName + "/time_15.aep");

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
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "OriginalName", 100, 100, 1);
        layer.name = "RenamedLayer";
        saveProject(proj, folder.fsName + "/name_renamed.aep");

        // comment
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.comment = "Test layer comment";
        saveProject(proj, folder.fsName + "/comment.aep");

        // enabled
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.enabled = false;
        saveProject(proj, folder.fsName + "/enabled_false.aep");

        // inPoint
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.inPoint = 5;
        saveProject(proj, folder.fsName + "/inPoint_5.aep");

        // label
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.label = 3;
        saveProject(proj, folder.fsName + "/label_3.aep");

        // locked
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.locked = true;
        saveProject(proj, folder.fsName + "/locked_true.aep");

        // outPoint
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 60, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.outPoint = 10;
        saveProject(proj, folder.fsName + "/outPoint_10.aep");

        // shy
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.shy = true;
        saveProject(proj, folder.fsName + "/shy_true.aep");

        // solo
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.solo = true;
        saveProject(proj, folder.fsName + "/solo_true.aep");

        // startTime
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 60, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.startTime = 5;
        saveProject(proj, folder.fsName + "/startTime_5.aep");

        // stretch
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 60, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.stretch = 200;
        saveProject(proj, folder.fsName + "/stretch_200.aep");

        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 60, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.stretch = -100;
        saveProject(proj, folder.fsName + "/stretch_minus100.aep");

        // --- AVLAYER_ATTRS ---

        // adjustmentLayer
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.adjustmentLayer = true;
        saveProject(proj, folder.fsName + "/adjustmentLayer_true.aep");

        // blendingMode
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.blendingMode = BlendingMode.MULTIPLY;
        saveProject(proj, folder.fsName + "/blendingMode_MULTIPLY.aep");

        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.blendingMode = BlendingMode.SCREEN;
        saveProject(proj, folder.fsName + "/blendingMode_SCREEN.aep");

        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.blendingMode = BlendingMode.ADD;
        saveProject(proj, folder.fsName + "/blendingMode_ADD.aep");

        // collapseTransformation
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        var precomp = proj.items.addComp("Precomp", 100, 100, 1, 1, 24);
        layer = comp.layers.add(precomp);
        if (layer.canSetCollapseTransformation) {
            layer.collapseTransformation = true;
        }
        saveProject(proj, folder.fsName + "/collapseTransformation_true.aep");

        // effectsActive
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.effectsActive = false;
        saveProject(proj, folder.fsName + "/effectsActive_false.aep");

        // environmentLayer - requires ray-traced 3D renderer and footage layer
        // Skipped: Ray-traced 3D renderer is deprecated and has complex requirements
        // The layer must be video/still footage (not solid, shape, text, or null)
        // and the comp must use Cinema 4D or Classic 3D renderer in certain modes

        // frameBlendingType
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.frameBlending = true;
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.frameBlendingType = FrameBlendingType.FRAME_MIX;
        saveProject(proj, folder.fsName + "/frameBlendingType_FRAME_MIX.aep");

        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.frameBlending = true;
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.frameBlendingType = FrameBlendingType.PIXEL_MOTION;
        saveProject(proj, folder.fsName + "/frameBlendingType_PIXEL_MOTION.aep");

        // guideLayer
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.guideLayer = true;
        saveProject(proj, folder.fsName + "/guideLayer_true.aep");

        // motionBlur
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.motionBlur = true;
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.motionBlur = true;
        saveProject(proj, folder.fsName + "/motionBlur_true.aep");

        // preserveTransparency
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.preserveTransparency = true;
        saveProject(proj, folder.fsName + "/preserveTransparency_true.aep");

        // quality
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.quality = LayerQuality.BEST;
        saveProject(proj, folder.fsName + "/quality_BEST.aep");

        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.quality = LayerQuality.DRAFT;
        saveProject(proj, folder.fsName + "/quality_DRAFT.aep");

        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.quality = LayerQuality.WIREFRAME;
        saveProject(proj, folder.fsName + "/quality_WIREFRAME.aep");

        // samplingQuality
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.samplingQuality = LayerSamplingQuality.BICUBIC;
        saveProject(proj, folder.fsName + "/samplingQuality_BICUBIC.aep");

        // threeDLayer
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.threeDLayer = true;
        saveProject(proj, folder.fsName + "/threeDLayer_true.aep");

        // threeDPerChar
        // Skipped: threeDPerChar requires text animators to persist correctly
        // and the export does not include AVLayer properties for text layers
        // proj = createProject();
        // comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        // layer = comp.layers.addText("3D Per Char");
        // layer.threeDLayer = true;
        // layer.threeDPerChar = true;
        // saveProject(proj, folder.fsName + "/threeDPerChar_true.aep");

        // timeRemapEnabled
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        precomp = proj.items.addComp("Precomp", 100, 100, 1, 5, 24);
        layer = comp.layers.add(precomp);
        layer.timeRemapEnabled = true;
        saveProject(proj, folder.fsName + "/timeRemapEnabled_true.aep");

        // trackMatteType
        proj = createProject();
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
        saveProject(proj, folder.fsName + "/trackMatteType_ALPHA.aep");

        proj = createProject();
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
        saveProject(proj, folder.fsName + "/trackMatteType_LUMA.aep");

        // --- Layer types ---

        // Null layer
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.layers.addNull();
        saveProject(proj, folder.fsName + "/type_null.aep");

        // Text layer
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.layers.addText("TextLayer");
        saveProject(proj, folder.fsName + "/type_text.aep");

        // Shape layer
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.layers.addShape();
        saveProject(proj, folder.fsName + "/type_shape.aep");

        // Camera layer
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        comp.layers.addCamera("CameraLayer", [50, 50]);
        saveProject(proj, folder.fsName + "/type_camera.aep");

        // --- LIGHTLAYER_ATTRS ---

        // lightType
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addLight("TestLight", [50, 50]);
        layer.lightType = LightType.PARALLEL;
        saveProject(proj, folder.fsName + "/lightType_PARALLEL.aep");

        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addLight("TestLight", [50, 50]);
        layer.lightType = LightType.SPOT;
        saveProject(proj, folder.fsName + "/lightType_SPOT.aep");

        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addLight("TestLight", [50, 50]);
        layer.lightType = LightType.POINT;
        saveProject(proj, folder.fsName + "/lightType_POINT.aep");

        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addLight("TestLight", [50, 50]);
        layer.lightType = LightType.AMBIENT;
        saveProject(proj, folder.fsName + "/lightType_AMBIENT.aep");

        // parent
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        var parentNull = comp.layers.addNull();
        parentNull.name = "ParentNull";
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "ChildLayer", 100, 100, 1);
        layer.parent = parentNull;
        saveProject(proj, folder.fsName + "/parent.aep");

        // autoOrient
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.autoOrient = AutoOrientType.ALONG_PATH;
        saveProject(proj, folder.fsName + "/autoOrient_ALONG_PATH.aep");

        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.threeDLayer = true;
        layer.autoOrient = AutoOrientType.CAMERA_OR_POINT_OF_INTEREST;
        saveProject(proj, folder.fsName + "/autoOrient_CAMERA.aep");

        // time (comp.time affects layer.time)
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 60, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        comp.time = 30;
        saveProject(proj, folder.fsName + "/time_30.aep");

        // --- audioEnabled (requires audio file) ---
        // Get assets folder path (samples/assets from samples/models)
        var modelsFolder = new Folder(outputPath);
        var samplesFolder = modelsFolder.parent;
        var wavFile = new File(samplesFolder.fsName + "/assets/wav.wav");

        // audioEnabled = true (default)
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        var importOptions = new ImportOptions(wavFile);
        var audioFootage = proj.importFile(importOptions);
        layer = comp.layers.add(audioFootage);
        layer.audioEnabled = true;
        saveProject(proj, folder.fsName + "/audioEnabled_true.aep");

        // audioEnabled = false
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        importOptions = new ImportOptions(wavFile);
        audioFootage = proj.importFile(importOptions);
        layer = comp.layers.add(audioFootage);
        layer.audioEnabled = false;
        saveProject(proj, folder.fsName + "/audioEnabled_false.aep");

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
        proj = createProject();
        item = proj.importPlaceholder("OriginalName", 100, 100, 24, 1);
        item.name = "RenamedFootage";
        saveProject(proj, folder.fsName + "/name_renamed.aep");

        // --- SOLID_SOURCE_ATTRS ---

        // color - red
        proj = createProject();
        comp = proj.items.addComp("Container", 100, 100, 1, 1, 24);
        comp.layers.addSolid([1, 0, 0], "Solid", 100, 100, 1);
        saveProject(proj, folder.fsName + "/color_red.aep");

        // color - green
        proj = createProject();
        comp = proj.items.addComp("Container", 100, 100, 1, 1, 24);
        comp.layers.addSolid([0, 1, 0], "Solid", 100, 100, 1);
        saveProject(proj, folder.fsName + "/color_green.aep");

        // color - blue
        proj = createProject();
        comp = proj.items.addComp("Container", 100, 100, 1, 1, 24);
        comp.layers.addSolid([0, 0, 1], "Solid", 100, 100, 1);
        saveProject(proj, folder.fsName + "/color_blue.aep");

        // color - gray
        proj = createProject();
        comp = proj.items.addComp("Container", 100, 100, 1, 1, 24);
        comp.layers.addSolid([0.5, 0.5, 0.5], "Solid", 100, 100, 1);
        saveProject(proj, folder.fsName + "/color_gray.aep");

        // size - 1920x1080
        proj = createProject();
        comp = proj.items.addComp("Container", 1920, 1080, 1, 1, 24);
        comp.layers.addSolid([0.5, 0.5, 0.5], "Solid", 1920, 1080, 1);
        saveProject(proj, folder.fsName + "/size_1920x1080.aep");

        // size - 3840x2160
        proj = createProject();
        comp = proj.items.addComp("Container", 3840, 2160, 1, 1, 24);
        comp.layers.addSolid([0.5, 0.5, 0.5], "Solid", 3840, 2160, 1);
        saveProject(proj, folder.fsName + "/size_3840x2160.aep");

        // pixelAspect
        proj = createProject();
        comp = proj.items.addComp("Container", 100, 100, 2, 1, 24);
        comp.layers.addSolid([0.5, 0.5, 0.5], "Solid", 100, 100, 2);
        saveProject(proj, folder.fsName + "/pixelAspect_2.aep");

        // --- PlaceholderSource ---

        // isStill = true
        proj = createProject();
        proj.importPlaceholder("Placeholder", 1920, 1080, 24, 0);
        saveProject(proj, folder.fsName + "/placeholder_still.aep");

        // isStill = false
        proj = createProject();
        proj.importPlaceholder("Placeholder", 1920, 1080, 24, 10);
        saveProject(proj, folder.fsName + "/placeholder_movie.aep");

        // Different frame rates
        proj = createProject();
        proj.importPlaceholder("Placeholder", 1920, 1080, 30, 10);
        saveProject(proj, folder.fsName + "/placeholder_30fps.aep");

        proj = createProject();
        proj.importPlaceholder("Placeholder", 1920, 1080, 60, 10);
        saveProject(proj, folder.fsName + "/placeholder_60fps.aep");

        // 23.976 fps footage (using mov_23_976.mov)
        proj = createProject();
        var assetsPath = getAssetsFolder(outputPath);
        var mov23976File = new File(assetsPath + "/mov_23_976.mov");
        var importOptions = new ImportOptions(mov23976File);
        var footage = proj.importFile(importOptions);
        saveProject(proj, folder.fsName + "/frameRate_23976.aep");

        // Different dimensions
        proj = createProject();
        proj.importPlaceholder("Placeholder", 1280, 720, 24, 10);
        saveProject(proj, folder.fsName + "/placeholder_720p.aep");

        proj = createProject();
        proj.importPlaceholder("Placeholder", 3840, 2160, 24, 10);
        saveProject(proj, folder.fsName + "/placeholder_4K.aep");

        // --- FILE_SOURCE_ATTRS (using mov_480.mov) ---
        var movFile = new File(assetsPath + "/mov_480.mov");
        var alphaImageFile = new File(assetsPath + "/image_with_alpha.png");

        // alphaMode (requires footage with alpha channel)
        proj = createProject();
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.alphaMode = AlphaMode.STRAIGHT;
        saveProject(proj, folder.fsName + "/alphaMode_STRAIGHT.aep");

        proj = createProject();
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.alphaMode = AlphaMode.PREMULTIPLIED;
        saveProject(proj, folder.fsName + "/alphaMode_PREMULTIPLIED.aep");

        proj = createProject();
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.alphaMode = AlphaMode.IGNORE;
        saveProject(proj, folder.fsName + "/alphaMode_IGNORE.aep");

        // conformFrameRate
        proj = createProject();
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.conformFrameRate = 30;
        saveProject(proj, folder.fsName + "/conformFrameRate_30.aep");

        proj = createProject();
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.conformFrameRate = 24;
        saveProject(proj, folder.fsName + "/conformFrameRate_24.aep");

        // fieldSeparationType
        proj = createProject();
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.fieldSeparationType = FieldSeparationType.OFF;
        saveProject(proj, folder.fsName + "/fieldSeparationType_OFF.aep");

        proj = createProject();
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.fieldSeparationType = FieldSeparationType.UPPER_FIELD_FIRST;
        saveProject(proj, folder.fsName + "/fieldSeparationType_UPPER.aep");

        proj = createProject();
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.fieldSeparationType = FieldSeparationType.LOWER_FIELD_FIRST;
        saveProject(proj, folder.fsName + "/fieldSeparationType_LOWER.aep");

        // highQualityFieldSeparation
        proj = createProject();
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.fieldSeparationType = FieldSeparationType.UPPER_FIELD_FIRST;
        footage.mainSource.highQualityFieldSeparation = true;
        saveProject(proj, folder.fsName + "/highQualityFieldSeparation_true.aep");

        // invertAlpha (requires footage with alpha channel)
        proj = createProject();
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.invertAlpha = true;
        saveProject(proj, folder.fsName + "/invertAlpha_true.aep");

        // loop
        proj = createProject();
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.loop = 3;
        saveProject(proj, folder.fsName + "/loop_3.aep");

        // premulColor (requires footage with alpha channel)
        proj = createProject();
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.alphaMode = AlphaMode.PREMULTIPLIED;
        footage.mainSource.premulColor = [1, 0, 0];
        saveProject(proj, folder.fsName + "/premulColor_red.aep");

        proj = createProject();
        importOptions = new ImportOptions(alphaImageFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.alphaMode = AlphaMode.PREMULTIPLIED;
        footage.mainSource.premulColor = [0, 0, 0];
        saveProject(proj, folder.fsName + "/premulColor_black.aep");

        // removePulldown
        proj = createProject();
        importOptions = new ImportOptions(movFile);
        footage = proj.importFile(importOptions);
        footage.mainSource.removePulldown = PulldownPhase.OFF;
        saveProject(proj, folder.fsName + "/removePulldown_OFF.aep");

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
        proj = createProject();
        f = proj.items.addFolder("OriginalName");
        f.name = "RenamedFolder";
        saveProject(proj, folder.fsName + "/name_renamed.aep");

        // comment
        proj = createProject();
        f = proj.items.addFolder("TestFolder");
        f.comment = "Folder comment";
        saveProject(proj, folder.fsName + "/comment.aep");

        // label
        proj = createProject();
        f = proj.items.addFolder("TestFolder");
        f.label = 1;
        saveProject(proj, folder.fsName + "/label_1.aep");

        proj = createProject();
        f = proj.items.addFolder("TestFolder");
        f.label = 5;
        saveProject(proj, folder.fsName + "/label_5.aep");

        proj = createProject();
        f = proj.items.addFolder("TestFolder");
        f.label = 10;
        saveProject(proj, folder.fsName + "/label_10.aep");

        // parentFolder (nested)
        proj = createProject();
        var root = proj.items.addFolder("RootFolder");
        var nested1 = proj.items.addFolder("Level1");
        nested1.parentFolder = root;
        var nested2 = proj.items.addFolder("Level2");
        nested2.parentFolder = nested1;
        var nested3 = proj.items.addFolder("Level3");
        nested3.parentFolder = nested2;
        saveProject(proj, folder.fsName + "/parentFolder_nested.aep");

        // with items (numItems)
        proj = createProject();
        var withItems = proj.items.addFolder("FolderWithItems");
        var c1 = proj.items.addComp("Comp1", 100, 100, 1, 1, 24);
        c1.parentFolder = withItems;
        var c2 = proj.items.addComp("Comp2", 100, 100, 1, 1, 24);
        c2.parentFolder = withItems;
        var ph = proj.importPlaceholder("Placeholder", 100, 100, 24, 1);
        ph.parentFolder = withItems;
        saveProject(proj, folder.fsName + "/numItems_3.aep");

        // empty folder
        proj = createProject();
        proj.items.addFolder("EmptyFolder");
        saveProject(proj, folder.fsName + "/empty.aep");

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
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.comment = "Test comment";
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName + "/comment.aep");

        // chapter
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.chapter = "Chapter 1";
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName + "/chapter.aep");

        // url
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.url = "https://example.com";
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName + "/url.aep");

        // frameTarget
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.url = "https://example.com";
        m.frameTarget = "_blank";
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName + "/frameTarget.aep");

        // cuePointName
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.cuePointName = "cue_test";
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName + "/cuePointName.aep");

        // duration
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.duration = 5;
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName + "/duration_5.aep");

        // label
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.label = 0;
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName + "/label_0.aep");

        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.label = 3;
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName + "/label_3.aep");

        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.label = 8;
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName + "/label_8.aep");

        // protectedRegion
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        m = new MarkerValue("TestMarker");
        m.protectedRegion = true;
        comp.markerProperty.setValueAtTime(0, m);
        saveProject(proj, folder.fsName + "/protectedRegion_true.aep");

        // --- Layer markers ---

        // layer marker comment
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        m = new MarkerValue("LayerMarker");
        m.comment = "Layer marker comment";
        layer.marker.setValueAtTime(0, m);
        saveProject(proj, folder.fsName + "/layer_comment.aep");

        // layer marker duration
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        m = new MarkerValue("LayerMarker");
        m.duration = 3;
        layer.marker.setValueAtTime(0, m);
        saveProject(proj, folder.fsName + "/layer_duration.aep");

        // layer marker cuePointName
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        m = new MarkerValue("LayerMarker");
        m.cuePointName = "layer_cue_1";
        layer.marker.setValueAtTime(0, m);
        saveProject(proj, folder.fsName + "/layer_cuePointName.aep");

        $.writeln("Generated marker samples in: " + folder.fsName);
    }

    // =========================================================================
    // Property Model Samples
    // Covers: Property, PropertyGroup, keyframes, expressions
    // =========================================================================

    function generatePropertySamples(outputPath) {
        var folder = ensureFolder(outputPath + "/property");
        var proj, comp, layer, prop;

        // --- Keyframe interpolation types ---

        // LINEAR
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 50]);
        prop.setValueAtTime(5, [100, 50]);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR);
        saveProject(proj, folder.fsName + "/keyframe_LINEAR.aep");

        // BEZIER
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 50]);
        prop.setValueAtTime(5, [100, 50]);
        prop.setInterpolationTypeAtKey(1, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
        saveProject(proj, folder.fsName + "/keyframe_BEZIER.aep");

        // HOLD
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 100);
        prop.setValueAtTime(2, 0);
        prop.setValueAtTime(4, 100);
        prop.setInterpolationTypeAtKey(2, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);
        saveProject(proj, folder.fsName + "/keyframe_HOLD.aep");

        // --- Property types ---

        // 1D (Opacity)
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(5, 100);
        saveProject(proj, folder.fsName + "/property_1D_opacity.aep");

        // 2D (Position, 2D layer)
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 0]);
        prop.setValueAtTime(5, [100, 100]);
        saveProject(proj, folder.fsName + "/property_2D_position.aep");

        // 3D (Position, 3D layer)
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        layer.threeDLayer = true;
        prop = layer.property("Position");
        prop.setValueAtTime(0, [0, 0, 0]);
        prop.setValueAtTime(5, [100, 100, 500]);
        saveProject(proj, folder.fsName + "/property_3D_position.aep");

        // Rotation
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Rotation");
        prop.setValueAtTime(0, 0);
        prop.setValueAtTime(5, 360);
        saveProject(proj, folder.fsName + "/property_rotation.aep");

        // Scale
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Scale");
        prop.setValueAtTime(0, [100, 100]);
        prop.setValueAtTime(5, [200, 200]);
        saveProject(proj, folder.fsName + "/property_scale.aep");

        // --- Expressions ---

        // expression enabled
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Position");
        prop.expression = "wiggle(2, 50)";
        saveProject(proj, folder.fsName + "/expression_enabled.aep");

        // expression disabled
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Opacity");
        prop.expression = "50";
        prop.expressionEnabled = false;
        saveProject(proj, folder.fsName + "/expression_disabled.aep");

        // time-based expression
        proj = createProject();
        comp = proj.items.addComp("TestComp", 100, 100, 1, 10, 24);
        layer = comp.layers.addSolid([0.5, 0.5, 0.5], "TestLayer", 100, 100, 1);
        prop = layer.property("Rotation");
        prop.expression = "time * 36";
        saveProject(proj, folder.fsName + "/expression_time.aep");

        $.writeln("Generated property samples in: " + folder.fsName);
    }

    // =========================================================================
    // Main Execution
    // =========================================================================

    function main() {
        var folder = Folder.selectDialog("Select the 'models' folder in samples/");
        if (!folder) {
            alert("No folder selected. Aborting.");
            return;
        }

        var OUTPUT_FOLDER = folder.fsName;

        $.writeln("=== Starting Sample Generation ===");
        $.writeln("Output folder: " + OUTPUT_FOLDER);
        $.writeln("Creating ONE .aep file per test case for isolation.");
        $.writeln("");

        try {
            $.writeln("--- Project samples ---");
            generateProjectSamples(OUTPUT_FOLDER);

            $.writeln("--- Composition samples ---");
            generateCompositionSamples(OUTPUT_FOLDER);

            $.writeln("--- Layer samples ---");
            generateLayerSamples(OUTPUT_FOLDER);

            $.writeln("--- Footage samples ---");
            generateFootageSamples(OUTPUT_FOLDER);

            $.writeln("--- Folder samples ---");
            generateFolderSamples(OUTPUT_FOLDER);

            $.writeln("--- Marker samples ---");
            generateMarkerSamples(OUTPUT_FOLDER);

            $.writeln("--- Property samples ---");
            generatePropertySamples(OUTPUT_FOLDER);
        } catch(e) {
            $.writeln("Error: " + e.toString());
            alert("Error generating samples:\n" + e.toString());
            return;
        }

        $.writeln("");
        $.writeln("=== Sample Generation Complete ===");
        $.writeln("Each .aep file tests ONE attribute for isolation.");
        $.writeln("");
        $.writeln("Next steps:");
        $.writeln("1. Run export_project_json.jsx on each .aep to create .json files or use batch_export_project_json.jsx.");

        alert("Sample generation complete!\n\n" +
              "Output: " + OUTPUT_FOLDER + "\n\n" +
              "Each .aep file tests ONE attribute.\n\n" +
              "Next: Run export_project_json.jsx on each file or use batch_export_project_json.jsx.");
    }

    main();

})();
