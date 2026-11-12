using System.Text;
using System.Text.Json.Nodes;
using Rre.Reader;

namespace Rre.Reader.Checks;

public static class QuestChecks
{
    public static async Task<IReadOnlyList<string>> RunAsync(string repository, string fengari)
    {
        var repo = Path.GetFullPath(repository);
        var artifacts = Path.Combine(repo, "artifacts", "quest-checks-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(artifacts);
        var passed = new List<string>();
        void Require(bool value, string reason) { if (!value) throw new Exception(reason); }
        var lua = await OwnedProcess.RunAsync("node", [Path.Combine(repo, "tools", "run-collector-lua.mjs"),
            Path.GetFullPath(fengari), "tools/agents/quest_journal/verify_quest_command.lua", "--emit-saved"], repo, CancellationToken.None);
        Require(lua.ExitCode == 0 && lua.Stdout.Contains("QUEST_COMMAND_PASS 16", StringComparison.Ordinal), "actual Lua command fixture failed");
        var resultLine = lua.Stdout.Split('\n').Single(line => line.StartsWith("RRE_LUA_RESULT ", StringComparison.Ordinal));
        var runtime = DataRules.Object(DataRules.Parse(Encoding.UTF8.GetBytes(resultLine[15..].Trim())), "lua-runtime-result");
        Require(runtime["status"]!.GetValue<string>() == "passed" && runtime["snapshotUnchanged"]!.GetValue<bool>(), "Lua source mutated or failed");
        passed.Add("all nine actual addon modules initialize and manual quest command passes16 assertions in Fengari");
        var savedLine = lua.Stdout.Split('\n').Single(line => line.StartsWith("RRE_QUEST_SAVED ", StringComparison.Ordinal));
        var input = Path.Combine(artifacts, "RRECollector.lua");
        await File.WriteAllTextAsync(input, savedLine[16..].Trim() + "\n", new UTF8Encoding(false));
        var result = await QuestJournalSource.ReadAsync(input, repo);
        Require(result["nextObjectives"] is JsonArray goals && goals.Count == 1
            && goals[0]!["remaining"]!.GetValue<int>() == 2
            && goals[0]!["locations"]![0]!["coordZ"]!.GetValue<int>() == 30, "Lua to quest consumer mismatch");
        Require(result["sourceSha256"]!.GetValue<string>() == DataRules.Sha(await File.ReadAllBytesAsync(input)), "quest original hash mismatch");
        passed.Add("actual Lua capture serializes through literal parser and C# quest goals with exact original hash");
        Require(result["lastRecordedAttempt"]!["status"]!.GetValue<string>() == "unavailable"
            && result["journalRetainedAfterFailure"]!.GetValue<bool>(), "failed capture hidden behind retained snapshot");
        passed.Add("preserved journal exposes later recorded API/player failure");
        foreach (var key in new[] { "live", "freshnessVerified", "coordinateFrameVerified", "travelFeasibilityVerified", "completionActionsVerified" })
            Require(!result["qualification"]![key]!.GetValue<bool>(), "quest source granted runtime acceptance");
        passed.Add("quest reader does not promote synthetic data to live navigation or completion");

        var missingDir = Path.Combine(artifacts, "missing"); Directory.CreateDirectory(missingDir);
        var noJournal = Path.Combine(missingDir, "RRECollector.lua");
        await File.WriteAllTextAsync(noJournal, "RRECollectorData={addonVersion=\"0.4.20\"}", new UTF8Encoding(false));
        try { await QuestJournalSource.ReadAsync(noJournal, repo); throw new Exception("missing journal became empty success"); }
        catch (ReaderFailure e) when (e.Message == "quest-parser-rejected") { }
        passed.Add("missing quest capture cannot fabricate goals");

        async Task<(int Exit, string Error)> Cli(params string[] args)
        {
            var priorOut = Console.Out; var priorError = Console.Error;
            using var stdout = new StringWriter(); using var stderr = new StringWriter();
            try
            {
                Console.SetOut(stdout); Console.SetError(stderr);
                return (await Rre.Reader.Program.Main(args), stderr.ToString());
            }
            finally { Console.SetOut(priorOut); Console.SetError(priorError); }
        }
        var output = Path.Combine(artifacts, "quests.json");
        var first = await Cli("quests", "--input", input, "--repo", repo, "--output", output);
        Require(first.Exit == 0, "quest CLI publish failed");
        var before = await File.ReadAllBytesAsync(output);
        var second = await Cli("quests", "--input", input, "--repo", repo, "--output", output);
        var after = await File.ReadAllBytesAsync(output);
        Require(second.Exit == 2 && second.Error.Contains("output-exists", StringComparison.Ordinal)
            && before.AsSpan().SequenceEqual(after), "quest CLI overwrote evidence");
        passed.Add("quest CLI uses exclusive evidence publication");
        var unsupported = await Cli("quests", "--input", input, "--repo", repo, "--source", "lab2");
        Require(unsupported.Exit == 2 && unsupported.Error.Contains("unknown-option", StringComparison.Ordinal), "quest CLI admitted acquisition options");
        passed.Add("quest file command rejects game-acquisition parameters");
        return passed;
    }
}
