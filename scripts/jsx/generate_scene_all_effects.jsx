// This script chunks the installed effects into groups of 10,
// and saves a separate .aep file for each chunk.

app.beginUndoGroup("Apply Chunked Effects");

// Where to save the generated projects
var repoRoot = new File($.fileName).parent.parent;
var saveDir = repoRoot.fsName + "/samples/assets/";
var assetPath = saveDir + "mov_23_976.mov";

var chunkSize = 10;
var appliedCount = 0;
var failedEffects = [];

if (app.effects && app.effects.length > 0) {
    var totalEffects = app.effects.length;
    var numChunks = Math.ceil(totalEffects / chunkSize);

    for (var chunkIdx = 0; chunkIdx < numChunks; chunkIdx++) {
        $.writeln("\n>>> Processing chunk " + (chunkIdx + 1) + " of " + numChunks + "...");

        // Create a new project (prompts to save or discard previous if dirty, but we are saving explicitly)
        app.newProject();
        
        if (app.project.bitsPerChannel != undefined) {
            app.project.bitsPerChannel = 16;
        }

        var importOptions = new ImportOptions(new File(assetPath));
        var movItem;
        try {
            movItem = app.project.importFile(importOptions);
        } catch (e) {
            $.writeln("Error importing asset: " + e.toString());
            break;
        }

        var compName = "Effects Comp Part " + (chunkIdx + 1);
        var myComp = app.project.items.addComp(
            compName, 1920, 1080, 1.0, 10.0, 30.0
        );

        myComp.openInViewer();
        var myLayer = myComp.layers.add(movItem);

        var sX = (1920 / movItem.width) * 100;
        var sY = (1080 / movItem.height) * 100;
        var s = Math.min(sX, sY);
        myLayer.property("ADBE Transform Group").property("ADBE Scale").setValue([s, s, s]);
        myLayer.audioEnabled = true;

        var startIndex = chunkIdx * chunkSize;
        var endIndex = Math.min(startIndex + chunkSize, totalEffects);

        for (var i = startIndex; i < endIndex; i++) {
            var fxMatchName = app.effects[i].matchName;
            try {
                $.writeln("Applying effect: " + fxMatchName);
                myLayer.property("ADBE Effect Parade").addProperty(fxMatchName);
                appliedCount++;
            } catch (e) {
                failedEffects.push(app.effects[i].displayName + " (" + fxMatchName + ")");
            }
        }

        // Save the project file
        var saveFile = new File(saveDir + "All_Effects_Part_" + (chunkIdx + 1) + ".aep");
        app.project.save(saveFile);
        $.writeln("Saved project chunk to: " + saveFile.fsName);
    }
} else {
    $.writeln("Could not retrieve the effects list.");
}

app.endUndoGroup();

$.writeln("\nDONE! Successfully applied " + appliedCount + " effects across " + numChunks + " projects.");
if (failedEffects.length > 0) {
    $.writeln(failedEffects.length + " effects could not be applied:");
    for (var f = 0; f < failedEffects.length; f++) {
        $.writeln(" - " + failedEffects[f]);
    }
}
