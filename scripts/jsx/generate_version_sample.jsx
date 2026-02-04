/**
 * Generate Version-Specific Complete Sample
 * 
 * This script creates a comprehensive test project containing at least one
 * instance of every item type, with various effects and attribute values.
 * The resulting project is used to test parser compatibility across AE versions.
 * 
 * This project should be saved in samples/versions/ae<YEAR>/complete.aep
 * 
 * Usage:
 *   1. Open After Effects (any version you want to test)
 *   2. Run this script: File > Scripts > Run Script File
 *   3. Select the version-specific output folder (e.g., samples/versions/ae2024/)
 *   4. Project will be saved as complete.aep
 * 
 * The generated project includes:
 *   - Multiple compositions with various settings
 *   - Solids, shapes, text, cameras, lights
 *   - 2D and 3D layers
 *   - Effects from various categories
 *   - Expressions
 *   - Markers (comp and layer)
 *   - Folder hierarchy
 *   - Various keyframe types
 *   - Parenting relationships
 *   - Track mattes
 */

//@include "json2.jsx"

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

    function getAEVersionYear() {
        var version = app.version;
        var major = parseInt(version.split(".")[0], 10);

        // Mapping of major version to year
        var versionMap = {
            15: 2018,
            16: 2019,
            17: 2020,
            18: 2021,
            22: 2022,
            23: 2023,
            24: 2024,
            25: 2025
        };

        return versionMap[major] || major;
    }

    // =========================================================================
    // Content Generators
    // =========================================================================

    function createFolderStructure(proj) {
        $.writeln("Creating folder structure...");

        var rootFolder = proj.items.addFolder("_Project Assets");

        var folders = {
            comps: proj.items.addFolder("Compositions"),
            footage: proj.items.addFolder("Footage"),
            solids: proj.items.addFolder("Solids"),
            precomps: proj.items.addFolder("Pre-comps"),
            output: proj.items.addFolder("Output Comps")
        };

        // Move all folders under root
        folders.comps.parentFolder = rootFolder;
        folders.footage.parentFolder = rootFolder;
        folders.solids.parentFolder = rootFolder;
        folders.precomps.parentFolder = rootFolder;
        folders.output.parentFolder = rootFolder;

        // Nested folders
        var subFolder = proj.items.addFolder("Subfolder Level 2");
        subFolder.parentFolder = folders.footage;

        var subSubFolder = proj.items.addFolder("Subfolder Level 3");
        subSubFolder.parentFolder = subFolder;

        return folders;
    }

    function createPlaceholders(proj, folders) {
        $.writeln("Creating placeholder footage...");

        // Still image placeholder
        var stillPlaceholder = proj.importPlaceholder("Still_Image_Placeholder", 1920, 1080, 24, 0);
        stillPlaceholder.parentFolder = folders.footage;

        // Video placeholder
        var videoPlaceholder = proj.importPlaceholder("Video_Placeholder", 1920, 1080, 24, 300);
        videoPlaceholder.parentFolder = folders.footage;

        // 4K placeholder
        var placeholder4K = proj.importPlaceholder("4K_Placeholder", 3840, 2160, 24, 60);
        placeholder4K.parentFolder = folders.footage;

        return {
            still: stillPlaceholder,
            video: videoPlaceholder,
            hires: placeholder4K
        };
    }

    function importFileFootage(proj, folders, assetsPath) {
        $.writeln("Importing file-based footage...");

        var result = {
            video: null,
            audio: null
        };

        // Import MOV file
        var movFile = new File(assetsPath + "/mov_480.mov");
        if (movFile.exists) {
            var importOptions = new ImportOptions(movFile);
            result.video = proj.importFile(importOptions);
            result.video.parentFolder = folders.footage;

            // Test various FILE_SOURCE_ATTRS
            result.video.mainSource.alphaMode = AlphaMode.STRAIGHT;
            result.video.mainSource.conformFrameRate = 24;
            result.video.mainSource.loop = 2;

            $.writeln("  Imported: " + movFile.name);
        } else {
            $.writeln("  SKIP: mov_480.mov not found at " + movFile.fsName);
        }

        // Import WAV file
        var wavFile = new File(assetsPath + "/wav.wav");
        if (wavFile.exists) {
            var importOptions = new ImportOptions(wavFile);
            result.audio = proj.importFile(importOptions);
            result.audio.parentFolder = folders.footage;
            $.writeln("  Imported: " + wavFile.name);
        } else {
            $.writeln("  SKIP: wav.wav not found at " + wavFile.fsName);
        }

        return result;
    }

    function addAudioLayers(comp, footage) {
        $.writeln("Adding audio layers...");

        if (!footage.audio) {
            $.writeln("  SKIP: No audio footage available");
            return [];
        }

        var audioLayers = [];

        // Audio layer with audio enabled (default)
        var audioLayer1 = comp.layers.add(footage.audio);
        audioLayer1.name = "Audio_Enabled";
        audioLayer1.audioEnabled = true;
        audioLayers.push(audioLayer1);

        // Audio layer with audio disabled
        var audioLayer2 = comp.layers.add(footage.audio);
        audioLayer2.name = "Audio_Disabled";
        audioLayer2.audioEnabled = false;
        audioLayer2.startTime = 5; // Offset to avoid overlap
        audioLayers.push(audioLayer2);

        return audioLayers;
    }

    function addVideoFootageLayers(comp, footage) {
        $.writeln("Adding video footage layers...");

        if (!footage.video) {
            $.writeln("  SKIP: No video footage available");
            return [];
        }

        var videoLayers = [];

        // Video footage layer
        var videoLayer = comp.layers.add(footage.video);
        videoLayer.name = "Video_Footage";
        videoLayers.push(videoLayer);

        // Video footage with time remap
        var timeRemapLayer = comp.layers.add(footage.video);
        timeRemapLayer.name = "Video_TimeRemap";
        if (timeRemapLayer.canSetTimeRemapEnabled) {
            timeRemapLayer.timeRemapEnabled = true;
        }
        timeRemapLayer.startTime = 10;
        videoLayers.push(timeRemapLayer);

        return videoLayers;
    }

    function createMainComposition(proj, folders, placeholders) {
        $.writeln("Creating main composition...");

        var mainComp = proj.items.addComp("Main_Composition", 1920, 1080, 1.0, 60, 24);
        mainComp.parentFolder = folders.comps;
        mainComp.bgColor = [0.1, 0.1, 0.1];
        mainComp.motionBlur = true;
        mainComp.shutterAngle = 180;
        mainComp.shutterPhase = 0;
        mainComp.workAreaStart = 0;
        mainComp.workAreaDuration = 30;

        // Add comp markers
        var marker1 = new MarkerValue("Intro Start");
        marker1.duration = 5;
        mainComp.markerProperty.setValueAtTime(0, marker1);

        var marker2 = new MarkerValue("Main Section");
        marker2.chapter = "Chapter 1";
        mainComp.markerProperty.setValueAtTime(10, marker2);

        var marker3 = new MarkerValue("Outro");
        marker3.label = 3;
        mainComp.markerProperty.setValueAtTime(50, marker3);

        return mainComp;
    }

    function addSolidLayers(comp, proj, folders) {
        $.writeln("Adding solid layers...");

        // Various colored solids
        var colors = [
            [[1, 0, 0], "Solid_Red"],
            [[0, 1, 0], "Solid_Green"],
            [[0, 0, 1], "Solid_Blue"],
            [[1, 1, 0], "Solid_Yellow"],
            [[1, 0, 1], "Solid_Magenta"],
            [[0, 1, 1], "Solid_Cyan"],
            [[0.18, 0.18, 0.18], "Solid_Gray"]
        ];

        var solidLayers = [];
        for (var i = 0; i < colors.length; i++) {
            var layer = comp.layers.addSolid(
                colors[i][0],
                colors[i][1],
                1920, 1080, 1.0
            );
            layer.enabled = i < 3; // Only enable first 3
            solidLayers.push(layer);
        }

        return solidLayers;
    }

    function addShapeLayers(comp) {
        $.writeln("Adding shape layers...");

        var shapes = [];

        // Rectangle shape
        var rectShape = comp.layers.addShape();
        rectShape.name = "Shape_Rectangle";
        var rectGroup = rectShape.property("Contents").addProperty("ADBE Vector Group");
        rectGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rectGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        shapes.push(rectShape);

        // Ellipse shape
        var ellipseShape = comp.layers.addShape();
        ellipseShape.name = "Shape_Ellipse";
        var ellipseGroup = ellipseShape.property("Contents").addProperty("ADBE Vector Group");
        ellipseGroup.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipseGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        shapes.push(ellipseShape);

        // Polygon shape
        var polyShape = comp.layers.addShape();
        polyShape.name = "Shape_Polygon";
        var polyGroup = polyShape.property("Contents").addProperty("ADBE Vector Group");
        polyGroup.property("Contents").addProperty("ADBE Vector Shape - Star");
        polyGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        polyGroup.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
        shapes.push(polyShape);

        return shapes;
    }

    function addTextLayers(comp) {
        $.writeln("Adding text layers...");

        var textLayers = [];

        // Simple text
        var text1 = comp.layers.addText("Hello World");
        text1.name = "Text_Simple";
        textLayers.push(text1);

        // Paragraph text
        var text2 = comp.layers.addText("Lorem ipsum dolor sit amet, consectetur adipiscing elit.");
        text2.name = "Text_Paragraph";
        textLayers.push(text2);

        // Animated text
        var text3 = comp.layers.addText("Animated Text");
        text3.name = "Text_Animated";
        var opacity = text3.property("Opacity");
        opacity.setValueAtTime(0, 0);
        opacity.setValueAtTime(1, 100);
        opacity.setValueAtTime(4, 100);
        opacity.setValueAtTime(5, 0);
        textLayers.push(text3);

        // Unicode text
        var text4 = comp.layers.addText("Unicode: 日本語 中文 한국어");
        text4.name = "Text_Unicode";
        textLayers.push(text4);

        return textLayers;
    }

    function addCameraAndLights(comp) {
        $.writeln("Adding camera and lights...");

        var result = {};

        // Camera
        result.camera = comp.layers.addCamera("Main_Camera", [960, 540]);
        result.camera.property("Position").setValue([960, 540, -1500]);

        // Point light
        result.pointLight = comp.layers.addLight("Light_Point", [960, 540]);
        result.pointLight.lightType = LightType.POINT;

        // Spot light
        result.spotLight = comp.layers.addLight("Light_Spot", [500, 300]);
        result.spotLight.lightType = LightType.SPOT;

        // Ambient light
        result.ambientLight = comp.layers.addLight("Light_Ambient", [960, 540]);
        result.ambientLight.lightType = LightType.AMBIENT;

        return result;
    }

    function addNullLayers(comp) {
        $.writeln("Adding null layers...");

        var null1 = comp.layers.addNull();
        null1.name = "Null_Controller";

        var null2 = comp.layers.addNull();
        null2.name = "Null_3D_Controller";
        null2.threeDLayer = true;

        return [null1, null2];
    }

    function setupLayerProperties(layers, comp) {
        $.writeln("Setting up layer properties...");

        // Find or create test layers
        var testLayers = [];
        for (var i = 1; i <= comp.numLayers && testLayers.length < 5; i++) {
            if (comp.layer(i).name.indexOf("Solid_") === 0) {
                testLayers.push(comp.layer(i));
            }
        }

        if (testLayers.length >= 5) {
            // Blending modes
            testLayers[0].blendingMode = BlendingMode.MULTIPLY;
            testLayers[1].blendingMode = BlendingMode.SCREEN;
            testLayers[2].blendingMode = BlendingMode.OVERLAY;

            // 3D layer
            testLayers[3].threeDLayer = true;

            // Motion blur
            testLayers[4].motionBlur = true;
        }

        // Labels
        for (var i = 1; i <= comp.numLayers && i <= 16; i++) {
            var layer = comp.layer(i);
            layer.label = (i - 1) % 17;
        }

        // Comments
        if (comp.numLayers >= 2) {
            comp.layer(1).comment = "This layer has a comment";
            comp.layer(2).comment = "Another comment with unicode: 日本語";
        }
    }

    function setupParenting(comp) {
        $.writeln("Setting up parenting...");

        var nullLayer = null;
        var childLayers = [];

        for (var i = 1; i <= comp.numLayers; i++) {
            var layer = comp.layer(i);
            if (layer.name === "Null_Controller") {
                nullLayer = layer;
            } else if (layer.name.indexOf("Shape_") === 0 && childLayers.length < 3) {
                childLayers.push(layer);
            }
        }

        if (nullLayer && childLayers.length > 0) {
            for (var i = 0; i < childLayers.length; i++) {
                childLayers[i].parent = nullLayer;
            }
        }
    }

    function setupTrackMattes(comp) {
        $.writeln("Setting up track mattes...");

        // Add matte and target layers
        var matteLayer = comp.layers.addSolid([1, 1, 1], "Track_Matte", 1920, 1080, 1.0);
        var targetLayer = comp.layers.addSolid([1, 0, 0], "Track_Matte_Target", 1920, 1080, 1.0);

        // Try the new setTrackMatte method (AE 23.0+)
        if (typeof targetLayer.setTrackMatte === "function") {
            targetLayer.setTrackMatte(matteLayer, TrackMatteType.ALPHA);
        } else {
            targetLayer.trackMatteType = TrackMatteType.ALPHA;
        }
    }

    function addKeyframes(comp) {
        $.writeln("Adding keyframes with various interpolation types...");

        var keyframeLayer = comp.layers.addSolid([0.5, 0.5, 0.5], "Keyframe_Demo", 1920, 1080, 1.0);

        // Position with bezier easing
        var pos = keyframeLayer.property("Position");
        pos.setValueAtTime(0, [100, 540]);
        pos.setValueAtTime(2, [960, 100]);
        pos.setValueAtTime(4, [1820, 540]);
        pos.setValueAtTime(6, [960, 980]);
        pos.setValueAtTime(8, [100, 540]);

        // Set interpolation types
        for (var i = 1; i <= pos.numKeys; i++) {
            pos.setInterpolationTypeAtKey(i, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);

            // Set spatial tangents for curved motion
            if (i < pos.numKeys) {
                pos.setSpatialContinuousAtKey(i, true);
            }
        }

        // Opacity with hold keyframes
        var opacity = keyframeLayer.property("Opacity");
        opacity.setValueAtTime(0, 100);
        opacity.setValueAtTime(2, 50);
        opacity.setValueAtTime(4, 100);
        opacity.setInterpolationTypeAtKey(2, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);

        // Scale with linear interpolation
        var scale = keyframeLayer.property("Scale");
        scale.setValueAtTime(0, [100, 100]);
        scale.setValueAtTime(4, [150, 150]);
        scale.setValueAtTime(8, [100, 100]);
        for (var i = 1; i <= scale.numKeys; i++) {
            scale.setInterpolationTypeAtKey(i, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR);
        }

        // Rotation
        var rotation = keyframeLayer.property("Rotation");
        rotation.setValueAtTime(0, 0);
        rotation.setValueAtTime(8, 360);

        return keyframeLayer;
    }

    function addExpressions(comp) {
        $.writeln("Adding expressions...");

        var exprLayer = comp.layers.addSolid([0.2, 0.8, 0.2], "Expression_Demo", 1920, 1080, 1.0);

        // Wiggle expression on position
        var pos = exprLayer.property("Position");
        pos.expression = "wiggle(2, 50)";

        // Time-based opacity
        var opacity = exprLayer.property("Opacity");
        opacity.expression = "Math.abs(Math.sin(time * 2)) * 100";

        // Rotation expression
        var rotation = exprLayer.property("Rotation");
        rotation.expression = "time * 36";

        // Disabled expression
        var disabledExprLayer = comp.layers.addSolid([0.8, 0.2, 0.2], "Expression_Disabled", 1920, 1080, 1.0);
        var scale = disabledExprLayer.property("Scale");
        scale.expression = "[100 + Math.sin(time) * 20, 100 + Math.sin(time) * 20]";
        scale.expressionEnabled = false;

        return exprLayer;
    }

    function addLayerMarkers(comp) {
        $.writeln("Adding layer markers...");

        var markerLayer = comp.layers.addSolid([0.5, 0.5, 1.0], "Layer_With_Markers", 1920, 1080, 1.0);

        var m1 = new MarkerValue("Layer Marker 1");
        markerLayer.marker.setValueAtTime(0.5, m1);

        var m2 = new MarkerValue("Layer Marker 2");
        m2.duration = 1;
        markerLayer.marker.setValueAtTime(2, m2);

        var m3 = new MarkerValue("Cue Point");
        m3.cuePointName = "cue_1";
        markerLayer.marker.setValueAtTime(4, m3);

        return markerLayer;
    }

    function addEffects(comp) {
        $.writeln("Adding effects...");

        var effectLayer = comp.layers.addSolid([1, 0.5, 0], "Effect_Demo", 1920, 1080, 1.0);

        // Add common effects
        var effectsToTry = [
            "ADBE Gaussian Blur 2",     // Gaussian Blur
            "ADBE Drop Shadow",          // Drop Shadow
            "ADBE Fill",                 // Fill
            "ADBE Glo2",                 // Glow
            "ADBE HUE SATURATION",       // Hue/Saturation
            "ADBE Tint",                 // Tint
            "ADBE Exposure2",            // Exposure
            "ADBE Fast Blur"             // Fast Blur (legacy)
        ];

        var effects = effectLayer.property("Effects");

        for (var i = 0; i < effectsToTry.length; i++) {
            var effect = effects.addProperty(effectsToTry[i]);
            $.writeln("  Added effect: " + effect.name);
        }

        var blur = effects.property("Gaussian Blur");
        blur.property("Blurriness").setValue(10);

        var shadow = effects.property("Drop Shadow");
        shadow.property("Distance").setValue(20);
        shadow.property("Softness").setValue(30);

        return effectLayer;
    }

    function createPrecomposition(proj, mainComp, folders) {
        $.writeln("Creating pre-composition...");

        // Create a simple pre-comp
        var preComp = proj.items.addComp("Pre_Composition", 1920, 1080, 1.0, 10, 24);
        preComp.parentFolder = folders.precomps;

        // Add content to pre-comp
        var precompSolid = preComp.layers.addSolid([0.3, 0.6, 0.9], "Precomp_Content", 1920, 1080, 1.0);
        var precompText = preComp.layers.addText("Pre-composition");

        // Add pre-comp to main comp
        var precompLayer = mainComp.layers.add(preComp);
        precompLayer.name = "Nested_Precomp";

        // Enable collapse transformation
        if (precompLayer.canSetCollapseTransformation) {
            precompLayer.collapseTransformation = true;
        }

        return preComp;
    }

    function setupLayerTimings(comp) {
        $.writeln("Setting up layer timings...");

        // Offset layers in time
        for (var i = 1; i <= Math.min(comp.numLayers, 10); i++) {
            var layer = comp.layer(i);
            layer.startTime = i * 0.5;
        }

        // Set specific in/out points
        if (comp.numLayers >= 3) {
            var layer1 = comp.layer(1);
            var layer2 = comp.layer(2);
            var layer3 = comp.layer(3);

            layer1.inPoint = 5;
            layer1.outPoint = 55;

            layer2.inPoint = 0;
            layer2.outPoint = 30;

            layer3.stretch = 200;
        }
    }

    function createOutputComp(proj, mainComp, folders) {
        $.writeln("Creating output composition...");

        // Various output resolutions
        var outputs = [
            ["Output_HD", 1920, 1080, 24],
            ["Output_720p", 1280, 720, 24],
            ["Output_4K", 3840, 2160, 24]
        ];

        for (var i = 0; i < outputs.length; i++) {
            var outputComp = proj.items.addComp(outputs[i][0], outputs[i][1], outputs[i][2], 1.0, 60, outputs[i][3]);
            outputComp.parentFolder = folders.output;
            outputComp.layers.add(mainComp);
        }
    }

    // =========================================================================
    // Main Execution
    // =========================================================================

    function main() {
        // Prompt for output folder
        var folder = Folder.selectDialog("Select the version-specific folder (e.g., samples/versions/ae2024/)");
        if (!folder) {
            alert("No folder selected. Aborting.");
            return;
        }

        // Determine assets path (samples/assets relative to samples/versions/aeXXXX)
        var assetsPath = folder.parent.parent.fsName + "/assets";

        var aeYear = getAEVersionYear();
        $.writeln("=== Generating Complete Sample for After Effects " + aeYear + " ===");
        $.writeln("AE Version: " + app.version);
        $.writeln("Output folder: " + folder.fsName);
        $.writeln("Assets path: " + assetsPath);
        $.writeln("");

        try {
            // Create new project
            var proj = createProject();

            // Set project settings
            proj.bitsPerChannel = 16;
            proj.linearBlending = true;

            // Create structure
            var folders = createFolderStructure(proj);
            var placeholders = createPlaceholders(proj, folders);

            // Import file-based footage (mov and wav)
            var fileFootage = importFileFootage(proj, folders, assetsPath);

            // Create main composition with all content
            var mainComp = createMainComposition(proj, folders, placeholders);

            addSolidLayers(mainComp, proj, folders);
            addShapeLayers(mainComp);
            addTextLayers(mainComp);
            addCameraAndLights(mainComp);
            addNullLayers(mainComp);
            addAudioLayers(mainComp, fileFootage);
            addVideoFootageLayers(mainComp, fileFootage);

            setupLayerProperties([], mainComp);
            setupParenting(mainComp);
            setupTrackMattes(mainComp);

            addKeyframes(mainComp);
            addExpressions(mainComp);
            addLayerMarkers(mainComp);
            addEffects(mainComp);

            var preComp = createPrecomposition(proj, mainComp, folders);

            setupLayerTimings(mainComp);
            createOutputComp(proj, mainComp, folders);

            // Save project
            var outputPath = folder.fsName + "/complete.aep";
            saveProject(proj, outputPath);

            $.writeln("");
            $.writeln("=== Complete Sample Generated ===");
            $.writeln("Saved to: " + outputPath);
            $.writeln("");
            $.writeln("Statistics:");
            $.writeln("  Total items: " + proj.numItems);
            $.writeln("  Main comp layers: " + mainComp.numLayers);
            $.writeln("  Main comp markers: " + mainComp.markerProperty.numKeys);
            $.writeln("");
            $.writeln("Next steps:");
            $.writeln("1. Review the project in After Effects");
            $.writeln("2. Run export_project_json.jsx to create the reference JSON");

            alert("Complete sample generated for AE " + aeYear + "!\n\nSaved to:\n" + outputPath + "\n\nItems: " + proj.numItems + "\nMain comp layers: " + mainComp.numLayers);

        } catch(e) {
            $.writeln("ERROR: " + e.toString());
            alert("Error generating sample:\n" + e.toString());
        }
    }

    main();

})();
