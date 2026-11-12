using System.Text;
using System.Text.Json.Nodes;

namespace Rre.Reader;

/// <summary>Offline quest goals from the existing collector; no gameplay acquisition.</summary>
public static class QuestJournalSource
{
    public static async Task<JsonObject> ReadAsync(string input, string repositoryRoot,
        CancellationToken cancellationToken = default)
    {
        DataRules.Require(Path.GetFileName(input) == "RRECollector.lua", "quest-filename");
        var bytes = await DataRules.ReadFileAsync(input, 2_000_000, cancellationToken);
        var sourceSha = DataRules.Sha(bytes);
        var helper = Path.Combine(repositoryRoot, "tools", "export-rrecollector-quests.mjs");
        var dependencies = new[] { helper,
            Path.Combine(repositoryRoot, "tools", "read-rrecollector-saved.mjs"),
            Path.Combine(repositoryRoot, "tools", "read-stable-original.mjs") };
        var hashes = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var file in dependencies)
            hashes.Add(file, DataRules.Sha(await DataRules.ReadFileAsync(file, 1_000_000, cancellationToken)));
        var result = await OwnedProcess.RunAsync("node", [helper, Path.GetFullPath(input)], repositoryRoot, cancellationToken);
        DataRules.Require(result.ExitCode == 0, "quest-parser-rejected");
        foreach (var file in dependencies)
            DataRules.Require(hashes[file] == DataRules.Sha(await DataRules.ReadFileAsync(file, 1_000_000, cancellationToken)),
                "quest-helper-source-changed");
        var root = DataRules.Object(DataRules.Parse(Encoding.UTF8.GetBytes(result.Stdout)), "quest-adapter-object");
        DataRules.Require(DataRules.Integer(root["schemaVersion"], "quest-schema") == 1
            && DataRules.Text(root["producerVersion"], "quest-version") == "0.4.20", "quest-contract");
        DataRules.Require(DataRules.Text(root["sourceSha256"], "quest-sha") == sourceSha
            && DataRules.Integer(root["sourceBytes"], "quest-bytes") == bytes.Length, "quest-input-changed");
        var sequence = DataRules.Integer(root["sequence"], "quest-sequence");
        DataRules.Require(sequence is > 0 and <= 9_007_199_254_740_991, "quest-sequence-limit");
        var qualification = DataRules.Object(root["qualification"], "quest-qualification");
        foreach (var key in new[] { "live", "freshnessVerified", "coordinateFrameVerified",
            "travelFeasibilityVerified", "completionActionsVerified" })
            DataRules.Require(!DataRules.Boolean(qualification[key], "quest-qualification-field"),
                "quest-unexpected-live-qualification");
        DataRules.Require(root["journal"] is JsonArray journal && journal.Count <= 128
            && root["nextObjectives"] is JsonArray goals && goals.Count <= 512, "quest-count-limit");
        root["adapterContract"] = "rre-quest-journal/1";
        root["reader"] = "Rre.Reader";
        root["readerVersion"] = Program.ReaderVersion;
        return root;
    }
}
