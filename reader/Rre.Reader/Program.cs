using System.Text.Json;
using System.Text.Json.Nodes;

namespace Rre.Reader;

public static class Program
{
    public static async Task<int> Main(string[] args)
    {
        try
        {
            if (args.Length == 0 || args is ["--help"] or ["help"])
            {
                Console.WriteLine("RRE host reader 0.2.2 (file adapters and explicit read-only Lab2 acquisition)\n"
                    + "capture|validate --source saved --input FILE --repo RRE_ROOT [--module all|abilities|context] [--output NEW_FILE]\n"
                    + "capture|validate --source memory-scan --input SCAN_JSON --session HEX32 --sequence N [--module all|abilities|context] [--output NEW_FILE]\n"
                    + "capture|validate --source native-snapshot --input SNAPSHOT_JSON --request REQUEST_JSON --session HEX32 --sequence N [--module all|abilities|context] [--output NEW_FILE]\n"
                    + "capture|validate --source publication --input FRAME_ARTIFACT_JSON --session HEX32 --sequence N [--module all|abilities|context] [--output NEW_FILE]\n"
                    + "capture --source lab2 --input BINDING_JSON --window WINDOW_JSON --evidence NEW_ARTIFACT_DIR --repo C:\\work\\rre [--module all|abilities|context] [--output NEW_FILE]\n"
                    + "doctor --repo RRE_ROOT\nOutputs one JSON document per invocation; diagnostics go to stderr. Existing files are never overwritten.");
                return 0;
            }
            var command = args[0];
            DataRules.Require(command is "capture" or "validate" or "doctor", "unknown-command");
            var options = Options(args[1..]);
            JsonObject output;
            if (command == "doctor")
            {
                Only(options, "--repo");
                var repo = Path.GetFullPath(Required(options, "--repo"));
                var node = await OwnedProcess.RunAsync("node", ["--version"], repo, CancellationToken.None);
                output = new JsonObject
                {
                    ["readerVersion"] = "0.2.2", ["dotnet"] = Environment.Version.ToString(),
                    ["nodeAvailable"] = node.ExitCode == 0, ["nodeVersion"] = node.ExitCode == 0 ? node.Stdout.Trim() : null,
                    ["savedHelperPresent"] = File.Exists(Path.Combine(repo, "tools", "rre-reader-saved-snapshot.mjs")),
                    ["literalParserPresent"] = File.Exists(Path.Combine(repo, "tools", "read-rrecollector-saved.mjs")),
                    ["adapters"] = new JsonArray("saved", "memory-scan-replay", "native-snapshot-replay", "publication-replay", "lab2-bounded-acquisition"),
                    ["lab2AcquisitionImplemented"] = true,["liveAcceptanceRequiresCurrentEvidence"] = true,
                    ["gameInputImplemented"] = false
                };
            }
            else
            {
                var source = Required(options, "--source");
                var input = Path.GetFullPath(Required(options, "--input"));
                var module = options.GetValueOrDefault("--module", "all");
                DataRules.Require(module is "all" or "abilities" or "context", "unknown-module");
                IObservationSource adapter;
                if (source == "lab2")
                {
                    DataRules.Require(command=="capture","lab2-capture-only");
                    Only(options,"--source","--input","--window","--evidence","--repo","--module","--output");
                    var repo=Path.GetFullPath(Required(options,"--repo"));
                    var evidence=Path.GetFullPath(Required(options,"--evidence"));
                    Lab2Source.Preflight(repo,evidence,options.GetValueOrDefault("--output"));
                    adapter=new Lab2Source(input,Path.GetFullPath(Required(options,"--window")),evidence,repo);
                }
                else if (source == "saved")
                {
                    Only(options, "--source", "--input", "--repo", "--module", "--output");
                    adapter = new SavedSource(input, Path.GetFullPath(Required(options, "--repo")));
                }
                else if (source == "memory-scan")
                {
                    Only(options, "--source", "--input", "--session", "--sequence", "--module", "--output");
                    DataRules.Require(long.TryParse(Required(options, "--sequence"), out var sequence), "sequence-format");
                    adapter = new MemoryScanSource(input, Required(options, "--session"), sequence);
                }
                else if (source == "publication")
                {
                    Only(options, "--source", "--input", "--session", "--sequence", "--module", "--output");
                    DataRules.Require(long.TryParse(Required(options, "--sequence"), out var sequence), "sequence-format");
                    adapter = new PublicationSource(input, Required(options, "--session"), sequence);
                }
                else if (source == "native-snapshot")
                {
                    Only(options, "--source", "--input", "--request", "--session", "--sequence", "--module", "--output");
                    DataRules.Require(long.TryParse(Required(options, "--sequence"), out var sequence), "sequence-format");
                    adapter = new NativeSnapshotSource(input, Path.GetFullPath(Required(options, "--request")), Required(options, "--session"), sequence);
                }
                else throw new ReaderFailure("unknown-source");
                var capture = await adapter.ReadAsync();
                output = ObservationModules.Build(capture, module);
                if (command == "validate") output = new JsonObject
                {
                    ["valid"] = true, ["source"] = capture.Evidence.DeepClone(), ["sequence"] = capture.Sequence,
                    ["abilityCount"] = capture.Abilities.Count, ["qualification"] = output["qualification"]!.DeepClone()
                };
            }
            var json = output.ToJsonString(new JsonSerializerOptions { WriteIndented = false }) + "\n";
            if (options.TryGetValue("--output", out var destination)) Publish(destination, json);
            else Console.Write(json);
            return 0;
        }
        catch (Exception error) when (error is ReaderFailure or IOException or UnauthorizedAccessException
            or JsonException or FormatException or ArgumentException or InvalidOperationException
            or System.ComponentModel.Win32Exception or OperationCanceledException or OverflowException)
        {
            var code = error is ReaderFailure ? error.Message : error is OperationCanceledException ? "operation-timeout-or-cancelled" : "input-or-runtime-unavailable";
            Console.Error.WriteLine(JsonSerializer.Serialize(new { error = code }));
            return 2;
        }
    }
    private static Dictionary<string, string> Options(string[] args)
    {
        DataRules.Require(args.Length % 2 == 0, "option-value-required");
        var result = new Dictionary<string, string>(StringComparer.Ordinal);
        for (var i = 0; i < args.Length; i += 2)
            DataRules.Require(args[i].StartsWith("--", StringComparison.Ordinal) && !string.IsNullOrWhiteSpace(args[i + 1])
                && result.TryAdd(args[i], args[i + 1]), "duplicate-or-invalid-option");
        return result;
    }
    private static string Required(Dictionary<string, string> options, string name)
        => options.GetValueOrDefault(name) ?? throw new ReaderFailure("missing-option:" + name);
    private static void Only(Dictionary<string, string> options, params string[] allowed)
        => DataRules.Require(options.Keys.All(allowed.Contains), "unknown-option");
    public static void Publish(string destination, string json)
    {
        var full = Path.GetFullPath(destination);
        DataRules.Require(!File.Exists(full) && !Directory.Exists(full), "output-exists");
        var parent = Path.GetDirectoryName(full)!;
        DataRules.Require(Directory.Exists(parent), "output-parent-missing");
        var temporary = Path.Combine(parent, ".rre-" + Guid.NewGuid().ToString("N") + ".tmp");
        try
        {
            using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream, new System.Text.UTF8Encoding(false))) writer.Write(json);
            File.Move(temporary, full, overwrite: false);
        }
        finally { if (File.Exists(temporary)) File.Delete(temporary); }
    }
}
