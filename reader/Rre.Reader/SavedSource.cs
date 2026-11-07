using System.Diagnostics;
using System.Text;
using System.Text.Json.Nodes;

namespace Rre.Reader;

public sealed class SavedSource(string input, string repositoryRoot) : IObservationSource
{
    public async Task<SourceCapture> ReadAsync(CancellationToken cancellationToken = default)
    {
        var bytes = await DataRules.ReadFileAsync(input, 2_000_000, cancellationToken);
        var expectedSha = DataRules.Sha(bytes);
        var helper = Path.Combine(repositoryRoot, "tools", "rre-reader-saved-snapshot.mjs");
        var parser = Path.Combine(repositoryRoot, "tools", "read-rrecollector-saved.mjs");
        var helperSha = DataRules.Sha(await DataRules.ReadFileAsync(helper, 1_000_000, cancellationToken));
        var parserSha = DataRules.Sha(await DataRules.ReadFileAsync(parser, 1_000_000, cancellationToken));
        var result = await OwnedProcess.RunAsync("node", [helper, Path.GetFullPath(input)], repositoryRoot, cancellationToken);
        DataRules.Require(result.ExitCode == 0, "saved-parser-rejected");
        DataRules.Require(helperSha == DataRules.Sha(await DataRules.ReadFileAsync(helper, 1_000_000, cancellationToken))
            && parserSha == DataRules.Sha(await DataRules.ReadFileAsync(parser, 1_000_000, cancellationToken)), "saved-helper-source-changed");
        var root = DataRules.Object(DataRules.Parse(Encoding.UTF8.GetBytes(result.Stdout)), "saved-adapter-object");
        DataRules.ExactKeys(root, "adapterContract", "sourceSha256", "sourceBytes", "addonVersion", "savedAddonVersion", "sequence",
            "abilities", "context", "counts", "structure");
        DataRules.Require(DataRules.Text(root["adapterContract"], "adapter-contract") == "rre-saved-snapshot/1", "adapter-contract");
        DataRules.Require(DataRules.Text(root["sourceSha256"], "adapter-sha") == expectedSha
            && DataRules.Integer(root["sourceBytes"], "adapter-bytes") == bytes.Length, "saved-input-changed");
        var sequence = DataRules.Integer(root["sequence"], "saved-sequence");
        DataRules.Require(sequence is > 0 and <= 9_007_199_254_740_991, "saved-sequence-limit");
        var structure = DataRules.Object(root["structure"], "saved-structure");
        DataRules.Require(DataRules.Boolean(structure["offlineStructureQualified"], "saved-structure-flag"), "saved-structure-unqualified");
        foreach (var flag in new[] { "freshnessVerified", "processBuildVerified", "eventDeliveryVerified", "eventComparisonReady" })
            DataRules.Require(!DataRules.Boolean(structure[flag], "saved-structure-flags"), "unexpected-live-qualification");
        var abilities = DataRules.Abilities(root["abilities"]);
        var counts = DataRules.Object(root["counts"], "saved-counts");
        DataRules.Require(DataRules.Integer(counts["detailCount"], "detail-count") == abilities.Count
            && DataRules.Integer(counts["uniqueCount"], "unique-count") == abilities.Count, "saved-count-mismatch");
        return new(abilities, (JsonObject)DataRules.Object(root["context"], "saved-context").DeepClone(), new JsonObject
        {
            ["kind"] = "persisted-savedvariables", ["path"] = Path.GetFullPath(input), ["sha256"] = expectedSha,
            ["bytes"] = bytes.Length, ["producer"] = "RRECollector", ["producerVersion"] = root["addonVersion"]?.DeepClone(),
            ["savedAddonVersion"] = root["savedAddonVersion"]?.DeepClone(),
            ["helperSha256"] = helperSha, ["literalParserSha256"] = parserSha,
            ["counts"] = counts.DeepClone(), ["structure"] = structure.DeepClone()
        }, sequence, false);
    }
}

public sealed record ProcessResult(int ExitCode, string Stdout, string Stderr);
public static class OwnedProcess
{
    public static async Task<ProcessResult> RunAsync(string executable, IReadOnlyList<string> args, string cwd, CancellationToken ct)
    {
        using var limit = CancellationTokenSource.CreateLinkedTokenSource(ct);
        limit.CancelAfter(TimeSpan.FromSeconds(10));
        using var process = new Process { StartInfo = new ProcessStartInfo(executable)
        {
            WorkingDirectory = cwd, UseShellExecute = false, CreateNoWindow = true,
            RedirectStandardOutput = true, RedirectStandardError = true,
            StandardOutputEncoding = Encoding.UTF8, StandardErrorEncoding = Encoding.UTF8
        } };
        foreach (var arg in args) process.StartInfo.ArgumentList.Add(arg);
        process.Start();
        try
        {
            var stdout = ReadBoundedAsync(process.StandardOutput, 4_000_000, limit.Token);
            var stderr = ReadBoundedAsync(process.StandardError, 8192, limit.Token);
            var exit = process.WaitForExitAsync(limit.Token);
            var first = await Task.WhenAny(stdout, stderr, exit);
            if (first.IsFaulted) await first;
            await Task.WhenAll(stdout, stderr, exit);
            return new(process.ExitCode, await stdout, await stderr);
        }
        finally
        {
            if (!process.HasExited) { process.Kill(entireProcessTree: true); await process.WaitForExitAsync(CancellationToken.None); }
        }
    }
    private static async Task<string> ReadBoundedAsync(StreamReader stream, int cap, CancellationToken ct)
    {
        var result = new StringBuilder(); var buffer = new char[4096];
        while (true)
        {
            var n = await stream.ReadAsync(buffer.AsMemory(), ct);
            if (n == 0) return result.ToString();
            DataRules.Require(result.Length + n <= cap, "child-output-limit");
            result.Append(buffer, 0, n);
        }
    }
}
