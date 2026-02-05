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
    // Configuration: Properties to skip during dynamic discovery
    // =========================================================================

    // Properties that would cause infinite recursion or are not useful
    var SKIP_PROPERTIES = {
        // Object references that would cause recursion or duplicates
        "activeItem": true,
        "parent": true,
        "parentFolder": true,
        "parentProperty": true,
        "proxySource": true,
        "rootFolder": true,
        "selectedLayers": true,
        "selectedProperties": true,
        "selection": true,
        "source": true,
        "usedIn": true,

        // Methods disguised as properties or internal
        "reflect": true,
        "toSource": true,
        "unwatch": true,
        "watch": true,
        
        // File objects (handled specially)
        "file": true,
        "mainSource": true,
        
        // Collections (handled separately)
        "layers": true,
        "items": true,

        // GUI stuff
        "dirty": true,
        "toolType": true,
        "selected": true,

        // Not useful
        "xmpPacket": true,
        "dynamicLinkGUID": true,
        "guides": true,
    };

    // =========================================================================
    // Helper Functions
    // =========================================================================

    /**
     * Check if a value is a simple exportable type.
     */
    function isSimpleValue(value) {
        var type = typeof value;
        if (type === "undefined") return true;
        if (value === null) return true;
        if (type === "boolean") return true;
        if (type === "number") return true;
        if (type === "string") return true;
        // Arrays of simple values (like bgColor, resolutionFactor)
        if (value instanceof Array) {
            for (var i = 0; i < value.length; i++) {
                if (!isSimpleValue(value[i])) return false;
            }
            return true;
        }
        return false;
    }

    /**
     * Dynamically get all readable attributes from an object.
     * Skips functions, complex objects, and properties in SKIP_PROPERTIES.
     */
    function getAllAttributes(obj) {
        var result = {};
        
        for (var prop in obj) {
            // Skip properties in our skip list
            if (SKIP_PROPERTIES[prop]) continue;
            
            try {
                var value = obj[prop];
                var type = typeof value;
                
                // Skip functions
                if (type === "function") continue;
                
                // Skip complex objects (but allow arrays and null)
                if (!isSimpleValue(value)) continue;
                
                // Handle undefined
                if (type === "undefined") {
                    result[prop] = {"_undefined": true};
                } else {
                    result[prop] = value;
                }
            } catch (e) {
                // Property threw an error when accessed - skip it
                // (some properties are only valid in certain states)
            }
        }
        
        return result;
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

            // Dynamically get all marker attributes
            var markerAttrs = getAllAttributes(markerValue);
            for (var key in markerAttrs) {
                marker[key] = markerAttrs[key];
            }

            markers.push(marker);
        }

        return markers;
    }

    /**
     * Export keyframes from a property.
     */
    function exportKeyframes(prop) {
        var keyframes = [];
        if (!prop || prop.numKeys === 0) {
            return keyframes;
        }

        for (var i = 1; i <= prop.numKeys; i++) {
            var kf = {
                index: i,
                time: prop.keyTime(i),
                value: prop.keyValue(i)
            };

            // Get interpolation types
            try {
                kf.inInterpolationType = prop.keyInInterpolationType(i);
                kf.outInterpolationType = prop.keyOutInterpolationType(i);
            } catch (e) {}

            // Get spatial tangents for position properties
            try {
                kf.inSpatialTangent = prop.keyInSpatialTangent(i);
                kf.outSpatialTangent = prop.keyOutSpatialTangent(i);
                kf.spatialAutoBezier = prop.keySpatialAutoBezier(i);
                kf.spatialContinuous = prop.keySpatialContinuous(i);
                kf.roving = prop.keyRoving(i);
            } catch (e) {}

            // Get temporal ease
            try {
                kf.inTemporalEase = [];
                kf.outTemporalEase = [];
                var inEase = prop.keyInTemporalEase(i);
                var outEase = prop.keyOutTemporalEase(i);
                for (var j = 0; j < inEase.length; j++) {
                    kf.inTemporalEase.push({
                        speed: inEase[j].speed,
                        influence: inEase[j].influence
                    });
                    kf.outTemporalEase.push({
                        speed: outEase[j].speed,
                        influence: outEase[j].influence
                    });
                }
                kf.temporalAutoBezier = prop.keyTemporalAutoBezier(i);
                kf.temporalContinuous = prop.keyTemporalContinuous(i);
            } catch (e) {}

            keyframes.push(kf);
        }

        return keyframes;
    }

    /**
     * Export a single property (not a group).
     */
    function exportProperty(prop) {
        var result = {
            name: prop.name,
            matchName: prop.matchName,
            propertyIndex: prop.propertyIndex,
            propertyType: "Property",
            isModified: prop.isModified
        };

        // Get property value type
        try {
            result.propertyValueType = prop.propertyValueType;
        } catch (e) {}

        // Check if property has expression
        try {
            result.canSetExpression = prop.canSetExpression;
            if (prop.canSetExpression) {
                result.expression = prop.expression;
                result.expressionEnabled = prop.expressionEnabled;
                result.expressionError = prop.expressionError;
            }
        } catch (e) {}

        // Get current value
        try {
            var val = prop.value;
            if (isSimpleValue(val)) {
                result.value = val;
            }
        } catch (e) {}

        // Get keyframes
        try {
            if (prop.numKeys > 0) {
                result.numKeys = prop.numKeys;
                result.keyframes = exportKeyframes(prop);
            }
        } catch (e) {}

        return result;
    }

    /**
     * Export a property group recursively.
     */
    function exportPropertyGroup(group, depth) {
        if (!group) return null;
        if (typeof depth === "undefined") depth = 0;
        if (depth > 10) return null; // Prevent infinite recursion

        var result = {
            name: group.name,
            matchName: group.matchName,
            propertyIndex: group.propertyIndex,
            propertyType: "PropertyGroup",
            numProperties: group.numProperties,
            enabled: group.enabled
        };

        // Export child properties
        result.properties = [];
        for (var i = 1; i <= group.numProperties; i++) {
            try {
                var child = group.property(i);
                if (!child) continue;

                // Skip markers (handled separately)
                if (child.matchName === "ADBE Marker") continue;

                if (child.propertyType === PropertyType.PROPERTY) {
                    result.properties.push(exportProperty(child));
                } else if (child.propertyType === PropertyType.INDEXED_GROUP || 
                           child.propertyType === PropertyType.NAMED_GROUP) {
                    result.properties.push(exportPropertyGroup(child, depth + 1));
                }
            } catch (e) {}
        }

        return result;
    }

    /**
     * Export effects from a layer.
     */
    function exportEffects(layer) {
        var effects = [];
        
        try {
            var effectsGroup = layer.property("ADBE Effect Parade");
            if (!effectsGroup || effectsGroup.numProperties === 0) {
                return effects;
            }

            for (var i = 1; i <= effectsGroup.numProperties; i++) {
                var effect = effectsGroup.property(i);
                var effectData = {
                    name: effect.name,
                    matchName: effect.matchName,
                    propertyIndex: effect.propertyIndex,
                    enabled: effect.enabled,
                    properties: []
                };

                // Export effect properties
                for (var j = 1; j <= effect.numProperties; j++) {
                    try {
                        var prop = effect.property(j);
                        if (prop.propertyType === PropertyType.PROPERTY) {
                            effectData.properties.push(exportProperty(prop));
                        } else if (prop.propertyType === PropertyType.INDEXED_GROUP || 
                                   prop.propertyType === PropertyType.NAMED_GROUP) {
                            effectData.properties.push(exportPropertyGroup(prop, 0));
                        }
                    } catch (e) {}
                }

                effects.push(effectData);
            }
        } catch (e) {}

        return effects;
    }

    /**
     * Export transform properties from a layer.
     */
    function exportTransform(layer) {
        try {
            var transform = layer.property("ADBE Transform Group");
            if (!transform) return null;
            return exportPropertyGroup(transform, 0);
        } catch (e) {
            return null;
        }
    }

    /**
     * Export a FootageSource object.
     */
    function exportFootageSource(source) {
        if (!source) return null;

        var result = {
            type: source.toString()
        };

        // Determine source type
        if (source instanceof SolidSource) {
            result.sourceType = "SolidSource";
        } else if (source instanceof FileSource) {
            result.sourceType = "FileSource";
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

        // Dynamically get all source attributes
        var sourceAttrs = getAllAttributes(source);
        for (var key in sourceAttrs) {
            result[key] = sourceAttrs[key];
        }

        return result;
    }

    /**
     * Export a Layer object.
     */
    function exportLayer(layer) {
        // Dynamically get all layer attributes
        var result = getAllAttributes(layer);

        // Determine layer type
        if (layer instanceof CameraLayer) {
            result.layerType = "CameraLayer";
        } else if (layer instanceof LightLayer) {
            result.layerType = "LightLayer";
        } else if (layer instanceof AVLayer) {
            // AVLayer includes TextLayer, ShapeLayer
            if (layer instanceof TextLayer) {
                result.layerType = "TextLayer";
            } else if (layer instanceof ShapeLayer) {
                result.layerType = "ShapeLayer";
            } else {
                result.layerType = "AVLayer";
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

        // Export layer markers
        if (layer.marker) {
            result.markers = exportMarkers(layer.marker);
        }

        // Export transform properties
        var transform = exportTransform(layer);
        if (transform) {
            result.transform = transform;
        }

        // Export effects
        var effects = exportEffects(layer);
        if (effects.length > 0) {
            result.effects = effects;
        }

        return result;
    }

    /**
     * Export an Item object (CompItem, FootageItem, or FolderItem).
     */
    function exportItem(item) {
        // Dynamically get all item attributes
        var result = getAllAttributes(item);

        // Get parent folder reference
        if (item.parentFolder && item.parentFolder !== app.project.rootFolder) {
            result.parentFolderId = item.parentFolder.id;
            result.parentFolderName = item.parentFolder.name;
        }

        if (item instanceof CompItem) {
            result.itemType = "CompItem";

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

            // Get file reference
            if (item.file) {
                result.filePath = item.file.fsName;
                result.fileName = item.file.name;
            }

            // Export mainSource
            result.mainSource = exportFootageSource(item.mainSource);

        } else if (item instanceof FolderItem) {
            result.itemType = "FolderItem";

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

        var result = {};

        // Get project file info
        if (project.file) {
            result.projectName = project.file.name;
        } else {
            result.projectName = "Untitled";
        }

        // Dynamically get all project attributes
        var projectAttrs = getAllAttributes(project);
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
