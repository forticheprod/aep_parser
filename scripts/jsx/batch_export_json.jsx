/**
 * Batch Export All Sample Projects to JSON
 * 
 * This script iterates through all .aep files in the selected folder
 * and exports each one to JSON using the export_project_json module.
 * 
 * Usage:
 *   1. Open After Effects (the latest version you have to get the most attributes)
 *   2. Run this script: File > Scripts > Run Script File
 *   3. Select a folder
 *   4. All .aep files in selected folder and subfolders will be exported to .json files in the same location
 * 
 * Output:
 *   - Each .aep file gets a corresponding .json file next to it
 *   - A summary is printed to the console with success/failure counts
 */

// Polyfill for JSON (AE uses ES3)
//@include "json2.jsx"

// Set library mode before including export module
var AEP_EXPORT_AS_LIBRARY = true;

// Include the export module
#include "export_project_json.jsx";

(function() {
    "use strict";

    // =========================================================================
    // Batch Processing Functions
    // =========================================================================

    /**
     * Recursively find all .aep files in a folder.
     * @param {Folder} folder - The folder to search
     * @param {Array} fileList - Array to collect files into
     * @returns {Array} The fileList with found files
     */
    function findAepFiles(folder, fileList) {
        var files = folder.getFiles();

        for (var i = 0; i < files.length; i++) {
            var file = files[i];

            if (file instanceof Folder) {
                // Skip assets folder (contains source files, not AEP projects)
                if (file.name.toLowerCase() !== "assets") {
                    findAepFiles(file, fileList);
                }
            } else if (file instanceof File) {
                if (file.name.match(/\.aep$/i)) {
                    fileList.push(file);
                }
            }
        }

        return fileList;
    }

    /**
     * Process a single .aep file: open, export to JSON, close.
     * @param {File} aepFile - The .aep file to process
     * @returns {Object} Result with success status and details
     */
    function processAepFile(aepFile) {
        try {
            // Open the project
            var project = app.open(aepFile);

            if (!project) {
                return { success: false, error: "Failed to open project" };
            }

            // Export using the AepExport module
            var projectData = AepExport.exportProject();

            // Save JSON file next to the AEP
            var jsonPath = aepFile.fsName.replace(/\.aep$/i, ".json");
            var success = AepExport.saveProjectJson(projectData, jsonPath);

            // Close without saving changes
            app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);

            if (success) {
                return { success: true, jsonPath: jsonPath };
            } else {
                return { success: false, error: "Failed to write JSON file" };
            }

        } catch(e) {
            // Try to close any open project
            try {
                if (app.project) {
                    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
                }
            } catch(e2) {}

            return { success: false, error: e.toString() };
        }
    }

    // =========================================================================
    // Main Execution
    // =========================================================================

    function main() {
        // Check that AepExport is available
        if (typeof AepExport === "undefined" || typeof AepExport.exportProject !== "function") {
            alert("Error: export_project_json.jsx must be included before this script.\n\n" +
                  "Make sure the @include directive is uncommented and the file path is correct.");
            return;
        }

        // Prompt for folder
        var selectedFolder = Folder.selectDialog("Select a folder containing .aep files (directly or in subfolders)");
        if (!selectedFolder) {
            alert("No folder selected. Aborting.");
            return;
        }

        $.writeln("=== Batch Export to JSON ===");
        $.writeln("Selected folder: " + selectedFolder.fsName);
        $.writeln("");

        // Find all .aep files
        var aepFiles = findAepFiles(selectedFolder, []);

        if (aepFiles.length === 0) {
            alert("No .aep files found in the selected folder.");
            return;
        }

        $.writeln("Found " + aepFiles.length + " .aep files");
        $.writeln("");

        // Process each file
        var successCount = 0;
        var failureCount = 0;
        var failures = [];

        for (var i = 0; i < aepFiles.length; i++) {
            var aepFile = aepFiles[i];
            var relativePath = aepFile.fsName.replace(selectedFolder.fsName, "");

            $.writeln("[" + (i + 1) + "/" + aepFiles.length + "] " + relativePath);

            var result = processAepFile(aepFile);

            if (result.success) {
                $.writeln("  -> OK");
                successCount++;
            } else {
                $.writeln("  -> FAILED: " + result.error);
                failureCount++;
                failures.push({ file: relativePath, error: result.error });
            }
        }

        // Summary
        $.writeln("");
        $.writeln("=== Summary ===");
        $.writeln("Success: " + successCount);
        $.writeln("Failed: " + failureCount);
        $.writeln("Total: " + aepFiles.length);

        if (failures.length > 0) {
            $.writeln("");
            $.writeln("Failed files:");
            for (var i = 0; i < failures.length; i++) {
                $.writeln("  " + failures[i].file + ": " + failures[i].error);
            }
        }

        var message = "Batch export complete!\n\n" +
                      "Success: " + successCount + "\n" +
                      "Failed: " + failureCount + "\n" +
                      "Total: " + aepFiles.length;

        if (failures.length > 0) {
            message += "\n\nCheck console for details on failures.";
        }

        alert(message);
    }

    main();

})();
