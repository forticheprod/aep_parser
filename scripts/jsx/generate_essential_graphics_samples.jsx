/**
 * Generate Test Samples for Essential Graphics (MotionGraphics) Testing
 *
 * Creates ONE .aep file and corresponding .json export per test case.
 *
 * These use addToMotionGraphicsTemplate() / addToMotionGraphicsTemplateAs()
 * on the "primary" comp, then nest it into a "main" comp so the essential
 * properties surface on the precomp layer (ADBE Layer Overrides group).
 *
 * Usage:
 *   1. Open After Effects CC 2019+ (16.1+ for addToMotionGraphicsTemplateAs)
 *   2. Run this script: File > Scripts > Run Script File
 *   3. Files will be saved to samples/essential_graphics/
 *
 * Requires export_project_json.jsx as library.
 */

// Include export_project_json as library
var AEP_EXPORT_AS_LIBRARY = true;
#include "export_project_json.jsx"

(function() {
    "use strict";

    var currentScene = "(init)";

    // =========================================================================
    // Utility Functions (same pattern as generate_model_samples.jsx)
    // =========================================================================

    function createProject(sceneName) {
        currentScene = sceneName || "(unknown)";
        if (app.project) {
            app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
        }
        return app.newProject();
    }

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
        exportProjectJson(filePath);
    }

    function ensureFolder(folderPath) {
        var folder = new Folder(folderPath);
        if (!folder.exists) {
            folder.create();
        }
        return folder;
    }

    /**
     * Create a standard setup: primary comp with a solid + Fill effect,
     * nested into main comp. Returns {proj, primary, main, solid, layer}.
     */
    function createBaseSetup() {
        var proj = app.project;
        var primary = proj.items.addComp("primary", 1000, 1000, 1, 10, 24);
        var layer = primary.layers.addSolid([0.5, 0.5, 0.5], "Gray Solid 1", 1000, 1000, 1);
        // Add Fill effect
        layer.property("ADBE Effect Parade").addProperty("ADBE Fill");
        // Nest primary into main
        var main = proj.items.addComp("main", 1000, 1000, 1, 10, 24);
        main.layers.add(primary);
        return {proj: proj, primary: primary, main: main, layer: layer};
    }

    // =========================================================================
    // Essential Graphics Samples
    // =========================================================================

    /**
     * Run a scene function, catching errors so one failure does not
     * block subsequent scenes.
     */
    function runScene(sceneName, folderPath, sceneFunc) {
        try {
            var proj = createProject(sceneName);
            sceneFunc(proj, folderPath);
        } catch (e) {
            $.writeln("  SKIPPED '" + sceneName + "': " + e.toString());
        }
    }

    function generateSamples(outputPath) {
        var folder = ensureFolder(outputPath);

        // -----------------------------------------------------------------
        // base: comp with Fill effect, no essential properties added
        // -----------------------------------------------------------------
        runScene("base", folder.fsName, function() {
            var setup = createBaseSetup();
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // fill_color_added: Fill > Color added to EGP
        // -----------------------------------------------------------------
        runScene("fill_color_added", folder.fsName, function() {
            var setup = createBaseSetup();
            var prop = setup.layer.property("ADBE Effect Parade")
                                  .property("ADBE Fill")
                                  .property("ADBE Fill-0002"); // Color
            prop.addToMotionGraphicsTemplate(setup.primary);
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // fill_color_renamed: Fill > Color added to EGP then renamed
        // -----------------------------------------------------------------
        runScene("fill_color_renamed", folder.fsName, function() {
            var setup = createBaseSetup();
            var prop = setup.layer.property("ADBE Effect Parade")
                                  .property("ADBE Fill")
                                  .property("ADBE Fill-0002"); // Color
            prop.addToMotionGraphicsTemplateAs(setup.primary, "BG color");
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // fill_and_opacity_added: Fill > Color and Fill > Opacity added
        // -----------------------------------------------------------------
        runScene("fill_and_opacity_added", folder.fsName, function() {
            var setup = createBaseSetup();
            var colorProp = setup.layer.property("ADBE Effect Parade")
                                       .property("ADBE Fill")
                                       .property("ADBE Fill-0002"); // Color
            var opacityProp = setup.layer.property("ADBE Effect Parade")
                                         .property("ADBE Fill")
                                         .property("ADBE Fill-0005"); // Opacity
            colorProp.addToMotionGraphicsTemplateAs(setup.primary, "BG color");
            opacityProp.addToMotionGraphicsTemplate(setup.primary);
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // fill_color_changed_on_comp: Fill > Color added, then value
        // changed on the precomp layer (Essential Properties override)
        // -----------------------------------------------------------------
        runScene("fill_color_changed_on_comp", folder.fsName, function() {
            var setup = createBaseSetup();
            var prop = setup.layer.property("ADBE Effect Parade")
                                  .property("ADBE Fill")
                                  .property("ADBE Fill-0002"); // Color
            prop.addToMotionGraphicsTemplateAs(setup.primary, "BG color");
            // Override value on the precomp layer in main comp
            var mainLayer = setup.main.layer(1);
            var epGroup = mainLayer.property("ADBE Layer Overrides");
            if (epGroup.numProperties > 0) {
                epGroup.property(1).setValue([1.0, 0.0, 0.0, 1.0]); // Red
            }
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // transform_opacity: Transform > Opacity added (non-effect property)
        // -----------------------------------------------------------------
        runScene("transform_opacity", folder.fsName, function() {
            var setup = createBaseSetup();
            var prop = setup.layer.property("ADBE Transform Group")
                                  .property("ADBE Opacity");
            prop.addToMotionGraphicsTemplate(setup.primary);
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // transform_position: Transform > Position added (spatial property)
        // -----------------------------------------------------------------
        runScene("transform_position", folder.fsName, function() {
            var setup = createBaseSetup();
            var prop = setup.layer.property("ADBE Transform Group")
                                  .property("ADBE Position");
            prop.addToMotionGraphicsTemplate(setup.primary);
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // custom_template_name: EGP with a custom template name
        // -----------------------------------------------------------------
        runScene("custom_template_name", folder.fsName, function() {
            var setup = createBaseSetup();
            setup.primary.motionGraphicsTemplateName = "My Custom Template";
            var prop = setup.layer.property("ADBE Effect Parade")
                                  .property("ADBE Fill")
                                  .property("ADBE Fill-0002");
            prop.addToMotionGraphicsTemplate(setup.primary);
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // multiple_controllers: Multiple properties from different groups
        // -----------------------------------------------------------------
        runScene("multiple_controllers", folder.fsName, function() {
            var setup = createBaseSetup();
            setup.layer.property("ADBE Effect Parade").addProperty("ADBE Brightness & Contrast 2");

            var fillColor = setup.layer.property("ADBE Effect Parade")
                                       .property("ADBE Fill")
                                       .property("ADBE Fill-0002");
            var opacity = setup.layer.property("ADBE Transform Group")
                                     .property("ADBE Opacity");
            var brightness = setup.layer.property("ADBE Effect Parade")
                                        .property("ADBE Brightness & Contrast 2")
                                        .property("ADBE Brightness & Contrast 2-0001");

            fillColor.addToMotionGraphicsTemplateAs(setup.primary, "Background Color");
            opacity.addToMotionGraphicsTemplateAs(setup.primary, "Layer Opacity");
            brightness.addToMotionGraphicsTemplateAs(setup.primary, "Brightness");
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // checkbox_controller: Expression Controls > Checkbox added to EGP
        // -----------------------------------------------------------------
        runScene("checkbox_controller", folder.fsName, function() {
            var setup = createBaseSetup();
            setup.layer.property("ADBE Effect Parade").addProperty("ADBE Checkbox Control");
            var prop = setup.layer.property("ADBE Effect Parade")
                                  .property("ADBE Checkbox Control")
                                  .property("ADBE Checkbox Control-0001");
            prop.addToMotionGraphicsTemplateAs(setup.primary, "Toggle Visibility");
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // slider_controller: Expression Controls > Slider added to EGP
        // -----------------------------------------------------------------
        runScene("slider_controller", folder.fsName, function() {
            var setup = createBaseSetup();
            setup.layer.property("ADBE Effect Parade").addProperty("ADBE Slider Control");
            var prop = setup.layer.property("ADBE Effect Parade")
                                  .property("ADBE Slider Control")
                                  .property("ADBE Slider Control-0001");
            prop.addToMotionGraphicsTemplateAs(setup.primary, "Intensity");
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // color_controller: Expression Controls > Color Control added to EGP
        // -----------------------------------------------------------------
        runScene("color_controller", folder.fsName, function() {
            var setup = createBaseSetup();
            setup.layer.property("ADBE Effect Parade").addProperty("ADBE Color Control");
            var prop = setup.layer.property("ADBE Effect Parade")
                                  .property("ADBE Color Control")
                                  .property("ADBE Color Control-0001");
            prop.addToMotionGraphicsTemplateAs(setup.primary, "Custom Color");
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // point_controller: Expression Controls > Point Control added to EGP
        // -----------------------------------------------------------------
        runScene("point_controller", folder.fsName, function() {
            var setup = createBaseSetup();
            setup.layer.property("ADBE Effect Parade").addProperty("ADBE Point Control");
            var prop = setup.layer.property("ADBE Effect Parade")
                                  .property("ADBE Point Control")
                                  .property("ADBE Point Control-0001");
            prop.addToMotionGraphicsTemplateAs(setup.primary, "Center Point");
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // dropdown_controller: Expression Controls > Dropdown Menu Control
        // Access first user-facing property by index (1) since the
        // matchName varies across AE versions.
        // -----------------------------------------------------------------
        runScene("dropdown_controller", folder.fsName, function() {
            var setup = createBaseSetup();
            var effect = setup.layer.property("ADBE Effect Parade")
                                    .addProperty("ADBE Dropdown Control");
            // The dropdown value property is the first child of the effect
            var prop = effect.property(1);
            prop.addToMotionGraphicsTemplateAs(setup.primary, "Style");
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // text_source_text: Source Text property added to EGP
        // Requires a text layer instead of solid + Fill
        // -----------------------------------------------------------------
        runScene("text_source_text", folder.fsName, function() {
            var proj = app.project;
            var primaryText = proj.items.addComp("primary", 1000, 1000, 1, 10, 24);
            var textLayer = primaryText.layers.addText("Sample Text");
            var sourceText = textLayer.property("ADBE Text Properties")
                                      .property("ADBE Text Document");
            sourceText.addToMotionGraphicsTemplateAs(primaryText, "Title Text");
            var mainText = proj.items.addComp("main", 1000, 1000, 1, 10, 24);
            mainText.layers.add(primaryText);
            saveProject(proj, folder.fsName);
        });

        // -----------------------------------------------------------------
        // two_layers: Essential properties from two different layers
        // -----------------------------------------------------------------
        runScene("two_layers", folder.fsName, function() {
            var proj = app.project;
            var primaryTwoLayers = proj.items.addComp("primary", 1000, 1000, 1, 10, 24);
            var layer1 = primaryTwoLayers.layers.addSolid([0.5, 0.5, 0.5], "Solid 1", 1000, 1000, 1);
            var layer2 = primaryTwoLayers.layers.addSolid([0.3, 0.3, 0.3], "Solid 2", 1000, 1000, 1);
            layer1.property("ADBE Effect Parade").addProperty("ADBE Fill");
            layer2.property("ADBE Effect Parade").addProperty("ADBE Fill");
            var color1 = layer1.property("ADBE Effect Parade")
                               .property("ADBE Fill")
                               .property("ADBE Fill-0002");
            var color2 = layer2.property("ADBE Effect Parade")
                               .property("ADBE Fill")
                               .property("ADBE Fill-0002");
            color1.addToMotionGraphicsTemplateAs(primaryTwoLayers, "Color Layer 1");
            color2.addToMotionGraphicsTemplateAs(primaryTwoLayers, "Color Layer 2");
            var mainTwoLayers = proj.items.addComp("main", 1000, 1000, 1, 10, 24);
            mainTwoLayers.layers.add(primaryTwoLayers);
            saveProject(proj, folder.fsName);
        });

        // -----------------------------------------------------------------
        // no_essential_properties: Template name set but no controllers
        // -----------------------------------------------------------------
        runScene("no_essential_properties", folder.fsName, function() {
            var setup = createBaseSetup();
            setup.primary.motionGraphicsTemplateName = "Empty Template";
            saveProject(app.project, folder.fsName);
        });

        // -----------------------------------------------------------------
        // controller_renamed: Property added, then controller renamed
        // via setMotionGraphicsControllerName (AE 16.1+)
        // -----------------------------------------------------------------
        runScene("controller_renamed", folder.fsName, function() {
            var setup = createBaseSetup();
            var prop = setup.layer.property("ADBE Effect Parade")
                                  .property("ADBE Fill")
                                  .property("ADBE Fill-0002");
            prop.addToMotionGraphicsTemplate(setup.primary);
            setup.primary.setMotionGraphicsControllerName(1, "Renamed Color");
            saveProject(app.project, folder.fsName);
        });

        $.writeln("Generated essential graphics samples in: " + folder.fsName);
    }

    // =========================================================================
    // Main Execution
    // =========================================================================

    function main() {
        var scriptFile = new File($.fileName);
        var scriptDir = scriptFile.parent;
        var egFolder = new Folder(scriptDir.fsName + "/../../samples/essential_graphics");
        if (!egFolder.exists) {
            egFolder.create();
        }

        $.writeln("=== Starting Essential Graphics Sample Generation ===");
        $.writeln("Output folder: " + egFolder.fsName);
        $.writeln("Creating ONE .aep file per test case.");
        $.writeln("");

        try {
            generateSamples(egFolder.fsName);
        } catch(e) {
            $.writeln("ERROR in scene '" + currentScene + "': " + e.toString());
            return;
        }

        $.writeln("");
        $.writeln("=== Essential Graphics Sample Generation Complete ===");
        $.writeln("Each .aep tests ONE essential graphics scenario.");
        $.writeln("Corresponding .json files have been generated automatically.");
        $.writeln("Output: " + egFolder.fsName);
    }

    main();

})();
