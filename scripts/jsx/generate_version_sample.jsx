/**
 * Generate Version-Specific Complete Sample
 *
 * Creates a single comprehensive .aep project containing a little bit of
 * everything: every item type, every layer type, common effects, expressions,
 * keyframes (various interpolation types), masks, shapes, text, 3D, parenting,
 * track mattes, markers, adjustment layers, guide layers, render queue, etc.
 *
 * The resulting project is used to test parser compatibility across AE versions.
 *
 * This project should be saved in samples/versions/ae<YEAR>/complete.aep
 *
 * Usage:
 *   1. Open After Effects (any version you want to test)
 *   2. Run this script: File > Scripts > Run Script File
 *   3. Project will be saved automatically to samples/versions/ae<YEAR>/
 *
 * Next step after running:
 *   Run export_project_json.jsx on the saved project to create the reference JSON.
 */

(function() {
    "use strict";

    // =========================================================================
    // Utility
    // =========================================================================

    function getAEVersionYear() {
        var major = parseInt(app.version.split(".")[0], 10);
        var map = {
            15: 2018, 16: 2019, 17: 2020, 18: 2021,
            22: 2022, 23: 2023, 24: 2024, 25: 2025, 26: 2026
        };
        return map[major] || major;
    }

    // =========================================================================
    // Project & Folders
    // =========================================================================

    function setupProject() {
        if (app.project) {
            app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
        }
        var proj = app.newProject();

        // Project settings
        proj.bitsPerChannel = 16;
        proj.linearBlending = true;
        proj.timeDisplayType = TimeDisplayType.TIMECODE;
        proj.framesCountType = FramesCountType.FC_START_0;
        try {
            proj.expressionEngine = "javascript-1.0";
        } catch (e) {}

        return proj;
    }

    function createFolders(proj) {
        var root = proj.items.addFolder("Assets");
        var comps = proj.items.addFolder("Compositions");
        comps.parentFolder = root;
        var footage = proj.items.addFolder("Footage");
        footage.parentFolder = root;
        var solids = proj.items.addFolder("Solids");
        solids.parentFolder = root;

        // Nested folder
        var sub = proj.items.addFolder("Subfolder");
        sub.parentFolder = footage;
        sub.comment = "Nested folder for testing depth";

        return { root: root, comps: comps, footage: footage, solids: solids, sub: sub };
    }

    // =========================================================================
    // Footage Items
    // =========================================================================

    function createPlaceholders(proj, folders) {
        var still = proj.importPlaceholder("Still_Placeholder", 1920, 1080, 24, 0);
        still.parentFolder = folders.footage;

        var video = proj.importPlaceholder("Video_Placeholder", 1920, 1080, 24, 300);
        video.parentFolder = folders.footage;

        return { still: still, video: video };
    }

    function importFileFootage(proj, folders, assetsPath) {
        var result = { video: null, audio: null, sequence: null };

        var movFile = new File(assetsPath + "/mov_480.mov");
        if (movFile.exists) {
            result.video = proj.importFile(new ImportOptions(movFile));
            result.video.parentFolder = folders.footage;
            result.video.mainSource.alphaMode = AlphaMode.STRAIGHT;
            result.video.mainSource.conformFrameRate = 24;
            result.video.mainSource.loop = 2;
            $.writeln("  Imported: " + movFile.name);
        }

        var wavFile = new File(assetsPath + "/wav.wav");
        if (wavFile.exists) {
            result.audio = proj.importFile(new ImportOptions(wavFile));
            result.audio.parentFolder = folders.footage;
            $.writeln("  Imported: " + wavFile.name);
        }

        // Image sequence
        var seqFile = new File(assetsPath + "/sequence_001.gif");
        if (seqFile.exists) {
            var seqOpts = new ImportOptions(seqFile);
            if (seqOpts.canImportAs(ImportAsType.FOOTAGE)) {
                seqOpts.sequence = true;
                result.sequence = proj.importFile(seqOpts);
                result.sequence.parentFolder = folders.sub;
                $.writeln("  Imported: image sequence");
            }
        }

        return result;
    }

    // =========================================================================
    // Main Composition - layers of every type
    // =========================================================================

    function createMainComp(proj, folders, placeholders, footage) {
        var comp = proj.items.addComp("Main_Comp", 1920, 1080, 1.0, 30, 24);
        comp.parentFolder = folders.comps;
        comp.bgColor = [0.1, 0.15, 0.2];
        comp.motionBlur = true;
        comp.shutterAngle = 180;
        comp.shutterPhase = -90;
        comp.workAreaStart = 2;
        comp.workAreaDuration = 20;
        comp.displayStartFrame = 0;

        // Comp markers
        var m1 = new MarkerValue("Start");
        m1.duration = 2;
        comp.markerProperty.setValueAtTime(0, m1);

        var m2 = new MarkerValue("Middle");
        m2.chapter = "Ch1";
        comp.markerProperty.setValueAtTime(10, m2);

        var m3 = new MarkerValue("End");
        m3.label = 5;
        comp.markerProperty.setValueAtTime(25, m3);

        // --- Solid layers ---
        var redSolid = comp.layers.addSolid([1, 0, 0], "Solid_Red", 1920, 1080, 1.0);
        redSolid.label = 1;
        redSolid.blendingMode = BlendingMode.MULTIPLY;

        var blueSolid = comp.layers.addSolid([0, 0, 1], "Solid_Blue", 1920, 1080, 1.0);
        blueSolid.label = 9;
        blueSolid.blendingMode = BlendingMode.SCREEN;
        blueSolid.enabled = false;

        // Solid with shy + locked
        var graySolid = comp.layers.addSolid([0.5, 0.5, 0.5], "Solid_ShyLocked", 1920, 1080, 1.0);
        graySolid.shy = true;
        graySolid.locked = true;

        // --- Adjustment layer ---
        var adjLayer = comp.layers.addSolid([1, 1, 1], "Adjustment", 1920, 1080, 1.0);
        adjLayer.adjustmentLayer = true;
        adjLayer.label = 14;

        // --- Guide layer ---
        var guideLayer = comp.layers.addSolid([0, 1, 0], "Guide", 200, 200, 1.0);
        guideLayer.guideLayer = true;

        // --- Null layer ---
        var nullCtrl = comp.layers.addNull();
        nullCtrl.name = "Null_Controller";
        nullCtrl.threeDLayer = true;
        nullCtrl.comment = "Parent null for shapes";

        // --- Shape layers ---
        var rectShape = comp.layers.addShape();
        rectShape.name = "Shape_Rectangle";
        var rg = rectShape.property("Contents").addProperty("ADBE Vector Group");
        rg.property("Contents").addProperty("ADBE Vector Shape - Rect");
        var rectFill = rg.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        rectFill.property("Color").setValue([1, 0.5, 0]);
        rg.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
        rectShape.parent = nullCtrl;

        var ellipseShape = comp.layers.addShape();
        ellipseShape.name = "Shape_Ellipse";
        var eg = ellipseShape.property("Contents").addProperty("ADBE Vector Group");
        eg.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        var ellipseFill = eg.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        ellipseFill.property("Color").setValue([0, 0.8, 0.4]);
        ellipseShape.parent = nullCtrl;

        var starShape = comp.layers.addShape();
        starShape.name = "Shape_Star";
        var sg = starShape.property("Contents").addProperty("ADBE Vector Group");
        sg.property("Contents").addProperty("ADBE Vector Shape - Star");
        sg.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        sg.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
        // Repeater
        starShape.property("Contents").addProperty("ADBE Vector Filter - Repeater");

        // --- Text layers ---
        var textSimple = comp.layers.addText("Hello World");
        textSimple.name = "Text_Simple";

        var textStyled = comp.layers.addText("Styled Text");
        textStyled.name = "Text_Styled";
        var textProp = textStyled.property("Source Text");
        var textDoc = textProp.value;
        textDoc.fontSize = 72;
        textDoc.fillColor = [1, 1, 0];
        textDoc.strokeColor = [0, 0, 0];
        textDoc.strokeWidth = 2;
        textDoc.font = "Arial";
        textDoc.tracking = 50;
        textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
        textProp.setValue(textDoc);

        // --- Camera ---
        var camera = comp.layers.addCamera("Camera", [960, 540]);
        camera.property("Position").setValue([960, 540, -1500]);
        camera.property("Zoom").setValue(1200);

        // --- Lights ---
        var pointLight = comp.layers.addLight("Light_Point", [960, 540]);
        pointLight.lightType = LightType.POINT;
        pointLight.property("Intensity").setValue(80);

        var spotLight = comp.layers.addLight("Light_Spot", [400, 300]);
        spotLight.lightType = LightType.SPOT;
        spotLight.property("Cone Angle").setValue(60);

        var ambientLight = comp.layers.addLight("Light_Ambient", [960, 540]);
        ambientLight.lightType = LightType.AMBIENT;
        ambientLight.property("Intensity").setValue(30);

        // --- 3D solid ---
        var solid3d = comp.layers.addSolid([0.3, 0.6, 0.9], "Solid_3D", 400, 400, 1.0);
        solid3d.threeDLayer = true;
        solid3d.property("Position").setValue([960, 540, 200]);
        solid3d.property("X Rotation").setValue(30);
        solid3d.property("Y Rotation").setValue(45);
        solid3d.motionBlur = true;

        // --- Audio layer ---
        if (footage.audio) {
            var audioLayer = comp.layers.add(footage.audio);
            audioLayer.name = "Audio";
            audioLayer.audioEnabled = true;
        }

        // --- Video footage layer ---
        if (footage.video) {
            var vidLayer = comp.layers.add(footage.video);
            vidLayer.name = "Video_Footage";
            if (vidLayer.canSetTimeRemapEnabled) {
                vidLayer.timeRemapEnabled = true;
            }
        }

        // --- Placeholder layer ---
        var phLayer = comp.layers.add(placeholders.video);
        phLayer.name = "Placeholder_Layer";
        phLayer.startTime = 5;
        phLayer.stretch = 150;

        // --- Solo layer ---
        var soloSolid = comp.layers.addSolid([1, 1, 0], "Solid_Solo", 1920, 1080, 1.0);
        soloSolid.solo = true;

        return comp;
    }

    // =========================================================================
    // Track Mattes
    // =========================================================================

    function addTrackMattes(comp) {
        var matte = comp.layers.addSolid([1, 1, 1], "TrackMatte_Alpha", 1920, 1080, 1.0);
        var target = comp.layers.addSolid([1, 0.3, 0], "TrackMatte_Target", 1920, 1080, 1.0);
        if (typeof target.setTrackMatte === "function") {
            target.setTrackMatte(matte, TrackMatteType.ALPHA);
        } else {
            target.trackMatteType = TrackMatteType.ALPHA;
        }
    }

    // =========================================================================
    // Masks
    // =========================================================================

    function addMasks(comp) {
        var maskLayer = comp.layers.addSolid([0.8, 0.2, 0.8], "Masked_Layer", 1920, 1080, 1.0);

        // Rectangular mask
        var mask1 = maskLayer.property("Masks").addProperty("Mask");
        mask1.name = "Rect_Mask";
        var shape1 = new Shape();
        shape1.vertices = [[200, 200], [800, 200], [800, 600], [200, 600]];
        shape1.closed = true;
        mask1.property("Mask Path").setValue(shape1);
        mask1.property("Mask Feather").setValue([20, 20]);
        mask1.property("Mask Opacity").setValue(80);
        mask1.maskMode = MaskMode.ADD;

        // Elliptical mask (subtract)
        var mask2 = maskLayer.property("Masks").addProperty("Mask");
        mask2.name = "Ellipse_Mask";
        var shape2 = new Shape();
        shape2.vertices = [[500, 300], [700, 400], [500, 500], [300, 400]];
        shape2.inTangents = [[110, 0], [0, -55], [-110, 0], [0, 55]];
        shape2.outTangents = [[-110, 0], [0, 55], [110, 0], [0, -55]];
        shape2.closed = true;
        mask2.property("Mask Path").setValue(shape2);
        mask2.maskMode = MaskMode.SUBTRACT;
        mask2.property("Mask Expansion").setValue(10);
    }

    // =========================================================================
    // Keyframes (various interpolation types)
    // =========================================================================

    function addKeyframes(comp) {
        var kfLayer = comp.layers.addSolid([0.5, 0.5, 0.5], "Keyframe_Demo", 1920, 1080, 1.0);

        // Position - bezier with spatial tangents
        var pos = kfLayer.property("Position");
        pos.setValueAtTime(0, [100, 540]);
        pos.setValueAtTime(1, [960, 100]);
        pos.setValueAtTime(2, [1820, 540]);
        pos.setValueAtTime(3, [960, 980]);
        pos.setValueAtTime(4, [100, 540]);
        for (var i = 1; i <= pos.numKeys; i++) {
            pos.setInterpolationTypeAtKey(i, KeyframeInterpolationType.BEZIER);
            pos.setSpatialContinuousAtKey(i, true);
        }

        // Opacity - hold keyframes
        var opacity = kfLayer.property("Opacity");
        opacity.setValueAtTime(0, 100);
        opacity.setValueAtTime(1, 0);
        opacity.setValueAtTime(2, 100);
        opacity.setInterpolationTypeAtKey(2, KeyframeInterpolationType.HOLD);

        // Scale - linear
        var scale = kfLayer.property("Scale");
        scale.setValueAtTime(0, [50, 50]);
        scale.setValueAtTime(2, [150, 150]);
        scale.setValueAtTime(4, [100, 100]);
        for (var i = 1; i <= scale.numKeys; i++) {
            scale.setInterpolationTypeAtKey(i, KeyframeInterpolationType.LINEAR);
        }

        // Rotation - continuous bezier with easing
        var rot = kfLayer.property("Rotation");
        rot.setValueAtTime(0, 0);
        rot.setValueAtTime(2, 180);
        rot.setValueAtTime(4, 360);
        for (var i = 1; i <= rot.numKeys; i++) {
            rot.setTemporalContinuousAtKey(i, true);
            rot.setTemporalAutoBezierAtKey(i, true);
        }

        // Layer markers
        var lm1 = new MarkerValue("Hit");
        kfLayer.marker.setValueAtTime(1, lm1);
        var lm2 = new MarkerValue("Duration Marker");
        lm2.duration = 0.5;
        kfLayer.marker.setValueAtTime(3, lm2);
    }

    // =========================================================================
    // Expressions
    // =========================================================================

    function addExpressions(comp) {
        var exprLayer = comp.layers.addSolid([0.2, 0.8, 0.2], "Expression_Demo", 1920, 1080, 1.0);

        // Active expressions
        exprLayer.property("Position").expression = "wiggle(2, 50)";
        exprLayer.property("Opacity").expression = "Math.abs(Math.sin(time * 2)) * 100";
        exprLayer.property("Rotation").expression = "time * 36";

        // Disabled expression
        var scale = exprLayer.property("Scale");
        scale.expression = "[100 + Math.sin(time) * 20, 100 + Math.sin(time) * 20]";
        scale.expressionEnabled = false;
    }

    // =========================================================================
    // Effects
    // =========================================================================

    function addEffects(comp) {
        var fxLayer = comp.layers.addSolid([1, 0.5, 0], "Effect_Demo", 1920, 1080, 1.0);
        var effects = fxLayer.property("Effects");

        var effectList = [
            "ADBE Gaussian Blur 2",
            "ADBE Drop Shadow",
            "ADBE Fill",
            "ADBE Glo2",
            "ADBE HUE SATURATION",
            "ADBE Tint",
            "ADBE Exposure2"
        ];

        for (var i = 0; i < effectList.length; i++) {
            try {
                effects.addProperty(effectList[i]);
            } catch (e) {
                $.writeln("  SKIP effect: " + effectList[i] + " (" + e.message + ")");
            }
        }

        // Configure some effect params
        try {
            effects.property("Gaussian Blur").property("Blurriness").setValue(15);
            effects.property("Drop Shadow").property("Distance").setValue(25);
            effects.property("Drop Shadow").property("Softness").setValue(20);
            effects.property("Fill").property("Color").setValue([0, 1, 0.5]);
        } catch (e) {
            $.writeln("  Could not configure effects: " + e.message);
        }

        // Disabled effect
        try {
            effects.property("Tint").enabled = false;
        } catch (e) {}
    }

    // =========================================================================
    // Pre-composition
    // =========================================================================

    function createPrecomp(proj, mainComp, folders) {
        var preComp = proj.items.addComp("Pre_Comp", 1920, 1080, 1.0, 10, 24);
        preComp.parentFolder = folders.comps;

        // Content inside precomp
        preComp.layers.addSolid([0.3, 0.6, 0.9], "Precomp_BG", 1920, 1080, 1.0);
        var preText = preComp.layers.addText("Precomp");
        preText.name = "Precomp_Text";

        // Precomp marker
        var pm = new MarkerValue("Precomp Marker");
        preComp.markerProperty.setValueAtTime(2, pm);

        // Add precomp to main comp
        var precompLayer = mainComp.layers.add(preComp);
        precompLayer.name = "Nested_Precomp";
        if (precompLayer.canSetCollapseTransformation) {
            precompLayer.collapseTransformation = true;
        }

        return preComp;
    }

    // =========================================================================
    // Separate Compositions for edge cases
    // =========================================================================

    function createDropFrameComp(proj, folders) {
        var comp = proj.items.addComp("DropFrame_Comp", 1920, 1080, 1.0, 60, 29.97);
        comp.parentFolder = folders.comps;
        comp.dropFrame = true;
        comp.layers.addSolid([0.4, 0.4, 0.4], "DF_Solid", 1920, 1080, 1.0);
    }

    function createHighFPSComp(proj, folders) {
        var comp = proj.items.addComp("HighFPS_Comp", 1920, 1080, 1.0, 10, 60);
        comp.parentFolder = folders.comps;
        comp.layers.addSolid([0.2, 0.2, 0.8], "HiFPS_Solid", 1920, 1080, 1.0);
    }

    function createSmallComp(proj, folders) {
        var comp = proj.items.addComp("Small_Comp", 320, 240, 1.0, 5, 24);
        comp.parentFolder = folders.comps;
        comp.resolutionFactor = [2, 2];
        comp.frameBlending = true;
        comp.hideShyLayers = true;

        var layer = comp.layers.addSolid([0.9, 0.1, 0.1], "Small_Solid", 320, 240, 1.0);
        layer.shy = true;
    }

    function createNonSquareComp(proj, folders) {
        var comp = proj.items.addComp("NonSquarePAR_Comp", 720, 576, 1.067, 10, 25);
        comp.parentFolder = folders.comps;
        comp.layers.addSolid([0.5, 0.3, 0.1], "PAR_Solid", 720, 576, 1.067);
    }

    // =========================================================================
    // Render Queue
    // =========================================================================

    function addRenderQueueItem(proj, mainComp) {
        var rqItem = proj.renderQueue.items.add(mainComp);
        rqItem.render = false;

        // Output module
        var om = rqItem.outputModule(1);
        try {
            om.applyTemplate("Lossless");
        } catch (e) {
            $.writeln("  Could not apply Lossless template: " + e.message);
        }

        var downloadFolder = Folder.desktop.fsName;
        om.file = new File(downloadFolder + "/[compName].[fileExtension]");
    }

    // =========================================================================
    // Main
    // =========================================================================

    function main() {
        var scriptFile = new File($.fileName);
        var scriptDir = scriptFile.parent;
        var aeYear = getAEVersionYear();
        var outFolder = new Folder(scriptDir.fsName + "/../../samples/versions/ae" + aeYear);
        if (!outFolder.exists) {
            outFolder.create();
        }

        var assetsPath = outFolder.parent.parent.fsName + "/assets";

        $.writeln("=== Generating Complete Sample for AE " + aeYear + " ===");
        $.writeln("AE Version: " + app.version);
        $.writeln("Output: " + outFolder.fsName);
        $.writeln("");

        try {
            var proj = setupProject();
            var folders = createFolders(proj);

            $.writeln("Creating footage items...");
            var placeholders = createPlaceholders(proj, folders);
            var footage = importFileFootage(proj, folders, assetsPath);

            $.writeln("Creating main composition...");
            var mainComp = createMainComp(proj, folders, placeholders, footage);

            $.writeln("Adding track mattes...");
            addTrackMattes(mainComp);

            $.writeln("Adding masks...");
            addMasks(mainComp);

            $.writeln("Adding keyframes...");
            addKeyframes(mainComp);

            $.writeln("Adding expressions...");
            addExpressions(mainComp);

            $.writeln("Adding effects...");
            addEffects(mainComp);

            $.writeln("Creating pre-composition...");
            createPrecomp(proj, mainComp, folders);

            $.writeln("Creating additional compositions...");
            createDropFrameComp(proj, folders);
            createHighFPSComp(proj, folders);
            createSmallComp(proj, folders);
            createNonSquareComp(proj, folders);

            $.writeln("Adding render queue item...");
            addRenderQueueItem(proj, mainComp);

            // Save
            var outputPath = outFolder.fsName + "/complete.aep";
            proj.save(new File(outputPath));

            $.writeln("");
            $.writeln("=== Complete ===");
            $.writeln("Saved: " + outputPath);
            $.writeln("Items: " + proj.numItems);
            $.writeln("Main comp layers: " + mainComp.numLayers);
            $.writeln("Main comp markers: " + mainComp.markerProperty.numKeys);
            $.writeln("");
            $.writeln("Next: run export_project_json.jsx on the saved project.");

        } catch (e) {
            $.writeln("ERROR: " + e.toString());
            $.writeln("Line: " + e.line);
        }
    }

    main();

})();
