using System.Text;
using System.Text.Json.Nodes;

namespace Rre.Reader;

/// <summary>Offline casting feedback. Separate from ability SourceCapture: no invented sequence/inventory.</summary>
public static class CastingEvidenceSource
{
    public static async Task<JsonObject> ReadAsync(string input, string repositoryRoot,
        CancellationToken cancellationToken = default)
    {
        DataRules.Require(Path.GetFileName(input) == "RiftReader2Casting.lua", "casting-filename");
        var bytes = await DataRules.ReadFileAsync(input, 32_000_000, cancellationToken);
        var sourceSha = DataRules.Sha(bytes);
        var helper = Path.Combine(repositoryRoot, "tools", "rre-casting-observation.mjs");
        var dependencies = new[] { helper,
            Path.Combine(repositoryRoot, "tools", "read-rrecollector-saved.mjs"),
            Path.Combine(repositoryRoot, "tools", "read-stable-original.mjs") };
        var hashes = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var file in dependencies)
            hashes.Add(file, DataRules.Sha(await DataRules.ReadFileAsync(file, 1_000_000, cancellationToken)));
        var result = await OwnedProcess.RunAsync("node", [helper, Path.GetFullPath(input)],
            repositoryRoot, cancellationToken);
        DataRules.Require(result.ExitCode == 0, "casting-parser-rejected");
        foreach (var file in dependencies)
            DataRules.Require(hashes[file] == DataRules.Sha(await DataRules.ReadFileAsync(file, 1_000_000, cancellationToken)),
                "casting-helper-source-changed");
        var root = DataRules.Object(DataRules.Parse(Encoding.UTF8.GetBytes(result.Stdout)), "casting-adapter-object");
        DataRules.Require(DataRules.Text(root["adapterContract"], "casting-contract") == "rre-casting-evidence/1"
            && DataRules.Text(root["producer"], "casting-producer") == "RiftReader2Casting"
            && DataRules.Text(root["producerVersion"], "casting-version") == "0.4.0", "casting-contract");
        DataRules.Require(DataRules.Text(root["sourceSha256"], "casting-sha") == sourceSha
            && DataRules.Integer(root["sourceBytes"], "casting-bytes") == bytes.Length, "casting-input-changed");
        var qualification = DataRules.Object(root["qualification"], "casting-qualification");
        DataRules.Require(DataRules.Boolean(qualification["offlineStructureVerified"], "casting-structure"),
            "casting-structure-unqualified");
        foreach (var key in new[] { "live", "freshnessVerified", "processBuildVerified", "sourceAuthenticityVerified",
            "castDeliveryVerified", "eventHistoryComplete", "currentActionAuthorized" })
            DataRules.Require(!DataRules.Boolean(qualification[key], "casting-qualification-field"),
                "casting-unexpected-live-qualification");
        foreach (var key in new[] { "trials", "previousTrials" })
            DataRules.Require(root[key] is JsonArray rows && rows.Count <= 8, "casting-trial-count");
        DataRules.Require(DataRules.Text(root["status"], "casting-status") is "no-trials" or "observations-available",
            "casting-status");
        root["reader"] = "Rre.Reader";
        root["readerVersion"] = Program.ReaderVersion;
        return root;
    }
}
