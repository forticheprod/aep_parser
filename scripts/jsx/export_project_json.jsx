/**
 * Export After Effects Project to JSON for testing aep_parser.
 * 
 * This script dynamically discovers and exports all readable attributes
 * from AE objects, making tests low-maintenance when new attributes are added.
 * 
 * Usage (standalone):
 *   1. Open After Effects (the latest version you have to get the most attributes)
 *   2. Open the .aep file you want to export
 *   3. Run this script: File > Scripts > Run Script File
 *   4. A .json file will be saved next to the .aep file
 * 
 * Usage (as library):
 *   Set AEP_EXPORT_AS_LIBRARY = true before including this script.
 *   Then call AepExport.exportProject() and AepExport.saveProjectJson().
 * 
 * The exported JSON serves as the "ground truth" for Python tests.
 */

// Polyfill for JSON (AE uses ES3)
#include "json2.jsx";

// Global namespace for library usage
var AepExport = AepExport || {};

(function(exports) {
    "use strict";

    // =========================================================================
    // Configuration: Define which attributes to export for each object type
    // These are based on the After Effects Scripting Guide
    // =========================================================================

    var PROJECT_ATTRS = [
        "bitsPerChannel",
        "colorManagementSystem",
        "compensateForSceneReferredProfiles",
        "displayStartFrame",
        "expressionEngine",
        "feetFramesFilmType",
        "footageTimecodeDisplayStartType",
        "framesCountType",
        "framesUseFeetFrames",
        "gpuAccelType",
        "linearBlending",
        "linearizeWorkingSpace",
        "lutInterpolationMethod",
        "numItems",
        "ocioConfigurationFile",
        "revision",
        "timeDisplayType",
        "transparencyGridThumbnails",
        "workingGamma",
        "workingSpace"
    ];

    var ITEM_ATTRS = [
        "name",
        "id",
        "comment",
        "typeName",
        "label"
    ];

    var AVITEM_ATTRS = [
        "duration",
        "footageMissing",
        "frameDuration",
        "frameRate",
        "hasAudio",
        "hasVideo",
        "height",
        "pixelAspect",
        "time",
        "useProxy",
        "width"
    ];

    var COMPITEM_ATTRS = [
        "bgColor",
        "displayStartFrame",
        "displayStartTime",
        "draft3d",
        "dropFrame",
        "frameBlending",
        "hideShyLayers",
        "motionBlur",
        "motionBlurAdaptiveSampleLimit",
        "motionBlurSamplesPerFrame",
        "numLayers",
        "preserveNestedFrameRate",
        "preserveNestedResolution",
        "renderer",
        "resolutionFactor",
        "shutterAngle",
        "shutterPhase",
        "workAreaDuration",
        "workAreaStart"
    ];

    var FOOTAGEITEM_ATTRS = [
        // file is handled separately
    ];

    var LAYER_ATTRS = [
        "name",
        "index",
        "comment",
        "enabled",
        "hasVideo",
        "id",
        "inPoint",
        "isNameSet",
        "label",
        "locked",
        "nullLayer",
        "outPoint",
        "shy",
        "solo",
        "startTime",
        "stretch",
        "time"
    ];

    var AVLAYER_ATTRS = [
        "adjustmentLayer",
        "audioActive",
        "audioEnabled",
        "blendingMode",
        "canSetCollapseTransformation",
        "canSetTimeRemapEnabled",
        "collapseTransformation",
        "effectsActive",
        "environmentLayer",
        "frameBlending",
        "frameBlendingType",
        "guideLayer",
        "hasAudio",
        "hasTrackMatte",
        "height",
        "isNameFromSource",
        "isTrackMatte",
        "motionBlur",
        "preserveTransparency",
        "quality",
        "samplingQuality",
        "threeDLayer",
        "threeDPerChar",
        "timeRemapEnabled",
        "trackMatteType",
        "width"
    ];

    var LIGHTLAYER_ATTRS = [
        "lightType"
    ];

    var FOOTAGE_SOURCE_ATTRS = [
        "alphaMode",
        "conformFrameRate",
        "displayFrameRate",
        "fieldSeparationType",
        "hasAlpha",
        "highQualityFieldSeparation",
        "invertAlpha",
        "isStill",
        "loop",
        "nativeFrameRate",
        "premulColor",
        "removePulldown"
    ];

    var SOLID_SOURCE_ATTRS = [
        "color"
    ];

    var FILE_SOURCE_ATTRS = [
        "missingFootagePath"
    ];

    var MARKER_ATTRS = [
        "comment",
        "chapter",
        "url",
        "frameTarget",
        "cuePointName",
        "duration",
        "label",
        "protectedRegion"
    ];

    // =========================================================================
    // Helper Functions
    // =========================================================================

    /**
     * Safely get an attribute value, returning null on error.
     */
    function safeGet(obj, attrName) {
        try {
            var value = obj[attrName];
            // Handle undefined
            if (typeof value === "undefined") {
                return {"_undefined": true};
            }
            return value;
        } catch (e) {
            return {"_error": e.toString()};
        }
    }

    /**
     * Get multiple attributes from an object.
     */
    function getAttributes(obj, attrList) {
        var result = {};
        for (var i = 0; i < attrList.length; i++) {
            var attr = attrList[i];
            result[attr] = safeGet(obj, attr);
        }
        return result;
    }

    /**
     * Convert enum values to readable strings.
     */
    function enumToString(value) {
        if (value === null || typeof value === "undefined") {
            return null;
        }
        // Enums in AE are numbers, try to return the value
        return value;
    }

    /**
     * Export markers from a property group.
     */
    function exportMarkers(markerProperty) {
        var markers = [];
        if (!markerProperty || markerProperty.numKeys === 0) {
            return markers;
        }

        for (var i = 1; i <= markerProperty.numKeys; i++) {
            var markerValue = markerProperty.keyValue(i);
            var marker = {
                time: markerProperty.keyTime(i),
                index: i
            };

            // Get all marker attributes
            for (var j = 0; j < MARKER_ATTRS.length; j++) {
                var attr = MARKER_ATTRS[j];
                marker[attr] = safeGet(markerValue, attr);
            }

            markers.push(marker);
        }

        return markers;
    }

    /**
     * Export a FootageSource object.
     */
    function exportFootageSource(source) {
        if (!source) return null;

        var result = {
            type: source.toString()
        };

        // Get base FootageSource attributes
        var baseAttrs = getAttributes(source, FOOTAGE_SOURCE_ATTRS);
        for (var key in baseAttrs) {
            result[key] = baseAttrs[key];
        }

        // Determine source type and get specific attributes
        if (source instanceof SolidSource) {
            result.sourceType = "SolidSource";
            var solidAttrs = getAttributes(source, SOLID_SOURCE_ATTRS);
            for (var key in solidAttrs) {
                result[key] = solidAttrs[key];
            }
        } else if (source instanceof FileSource) {
            result.sourceType = "FileSource";
            var fileAttrs = getAttributes(source, FILE_SOURCE_ATTRS);
            for (var key in fileAttrs) {
                result[key] = fileAttrs[key];
            }
            // Get file path
            if (source.file) {
                result.filePath = source.file.fsName;
                result.fileName = source.file.name;
            }
        } else if (source instanceof PlaceholderSource) {
            result.sourceType = "PlaceholderSource";
        } else {
            result.sourceType = "FootageSource";
        }

        return result;
    }

    /**
     * Export a Layer object.
     */
    function exportLayer(layer) {
        var result = getAttributes(layer, LAYER_ATTRS);

        // Determine layer type
        if (layer instanceof CameraLayer) {
            result.layerType = "CameraLayer";
        } else if (layer instanceof LightLayer) {
            result.layerType = "LightLayer";
            var lightAttrs = getAttributes(layer, LIGHTLAYER_ATTRS);
            for (var key in lightAttrs) {
                result[key] = lightAttrs[key];
            }
        } else if (layer instanceof AVLayer) {
            // AVLayer includes TextLayer, ShapeLayer
            if (layer instanceof TextLayer) {
                result.layerType = "TextLayer";
            } else if (layer instanceof ShapeLayer) {
                result.layerType = "ShapeLayer";
            } else {
                result.layerType = "AVLayer";
            }

            var avAttrs = getAttributes(layer, AVLAYER_ATTRS);
            for (var key in avAttrs) {
                result[key] = avAttrs[key];
            }

            // Get source reference
            if (layer.source) {
                result.sourceId = layer.source.id;
                result.sourceName = layer.source.name;
            }
        } else {
            result.layerType = "Layer";
        }

        // Get parent reference
        if (layer.parent) {
            result.parentIndex = layer.parent.index;
            result.parentName = layer.parent.name;
        }

        // Get autoOrient (enum)
        result.autoOrient = enumToString(safeGet(layer, "autoOrient"));

        // Export layer markers
        if (layer.marker) {
            result.markers = exportMarkers(layer.marker);
        }

        return result;
    }

    /**
     * Export an Item object (CompItem, FootageItem, or FolderItem).
     */
    function exportItem(item) {
        var result = getAttributes(item, ITEM_ATTRS);

        // Get parent folder reference
        if (item.parentFolder && item.parentFolder !== app.project.rootFolder) {
            result.parentFolderId = item.parentFolder.id;
            result.parentFolderName = item.parentFolder.name;
        }

        if (item instanceof CompItem) {
            result.itemType = "CompItem";

            // Get AVItem attributes
            var avAttrs = getAttributes(item, AVITEM_ATTRS);
            for (var key in avAttrs) {
                result[key] = avAttrs[key];
            }

            // Get CompItem attributes
            var compAttrs = getAttributes(item, COMPITEM_ATTRS);
            for (var key in compAttrs) {
                result[key] = compAttrs[key];
            }

            // Get renderers list
            result.renderers = safeGet(item, "renderers");

            // Export composition markers
            if (item.markerProperty) {
                result.markers = exportMarkers(item.markerProperty);
            }

            // Export layers
            result.layers = [];
            for (var i = 1; i <= item.numLayers; i++) {
                result.layers.push(exportLayer(item.layer(i)));
            }

        } else if (item instanceof FootageItem) {
            result.itemType = "FootageItem";

            // Get AVItem attributes
            var avAttrs = getAttributes(item, AVITEM_ATTRS);
            for (var key in avAttrs) {
                result[key] = avAttrs[key];
            }

            // Get file reference
            if (item.file) {
                result.filePath = item.file.fsName;
                result.fileName = item.file.name;
            }

            // Export mainSource
            result.mainSource = exportFootageSource(item.mainSource);

        } else if (item instanceof FolderItem) {
            result.itemType = "FolderItem";
            result.numItems = item.numItems;

            // List child item IDs
            result.childItemIds = [];
            for (var i = 1; i <= item.numItems; i++) {
                result.childItemIds.push(item.item(i).id);
            }
        }

        return result;
    }

    /**
     * Export the entire project.
     */
    function exportProject() {
        var project = app.project;

        var result = {
            exportVersion: "1.0",
            exportDate: new Date().toISOString(),
            aeVersion: app.version,
            aeBuildNumber: app.buildNumber
        };

        // Get project file info
        if (project.file) {
            result.projectFile = project.file.fsName;
            result.projectName = project.file.name;
        } else {
            result.projectFile = null;
            result.projectName = "Untitled";
        }

        // Get project attributes
        var projectAttrs = getAttributes(project, PROJECT_ATTRS);
        for (var key in projectAttrs) {
            result[key] = projectAttrs[key];
        }

        // Export all items
        result.items = [];
        for (var i = 1; i <= project.numItems; i++) {
            result.items.push(exportItem(project.item(i)));
        }

        return result;
    }

    // =========================================================================
    // Public API (for library usage)
    // =========================================================================

    exports.exportProject = exportProject;

    /**
     * Save project data to a JSON file.
     * @param {Object} projectData - The exported project data
     * @param {string} outputPath - The file path to save to
     * @returns {boolean} True if successful
     */
    exports.saveProjectJson = function(projectData, outputPath) {
        try {
            var jsonString = JSON.stringify(projectData, null, 2);
            var outputFile = new File(outputPath);
            outputFile.open("w");
            outputFile.encoding = "UTF-8";
            outputFile.write(jsonString);
            outputFile.close();
            return true;
        } catch(e) {
            return false;
        }
    };

    // =========================================================================
    // Main Execution (only when run directly)
    // =========================================================================

    function main() {
        if (!app.project) {
            alert("No project open");
            return;
        }

        var projectData = exportProject();
        var jsonString = JSON.stringify(projectData, null, 2);

        // Determine output file path
        var outputFile;
        if (app.project.file) {
            outputFile = new File(app.project.file.fsName.replace(/\.aep$/i, ".json"));
        } else {
            outputFile = File.saveDialog("Save JSON export", "JSON:*.json");
        }

        if (outputFile) {
            outputFile.open("w");
            outputFile.encoding = "UTF-8";
            outputFile.write(jsonString);
            outputFile.close();
            alert("Exported to:\n" + outputFile.fsName);
        }
    }

    // Run main() only if not used as a library
    if (typeof AEP_EXPORT_AS_LIBRARY === "undefined" || !AEP_EXPORT_AS_LIBRARY) {
        main();
    }

})(AepExport);
