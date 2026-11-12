using System.Text;
using System.Text.Json.Nodes;
using Rre.Reader;

namespace Rre.Reader.Checks;

public static class CombatChecks
{
    public static async Task<IReadOnlyList<string>> RunAsync(string repository)
    {
        var repo = Path.GetFullPath(repository);
        var artifacts = Path.Combine(repo, "artifacts", "combat-checks-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(artifacts);
        var passed = new List<string>();
        const string empty = "RiftReader2CastingEvidence={schemaVersion=1,source=\"RIFT Lua API\",addonVersion=\"0.4.0\",trials={},previousTrials={}}";
        const string observed = """
            RiftReader2CastingEvidence={schemaVersion=1,source="RIFT Lua API",addonVersion="0.4.0",previousTrials={},trials={{
              status="finished",started=100,deadline=160,playerId="uPLAYER",targetId="uTARGET",
              abilityId="A1111111111111111",abilityNewId="A2222222222222222",hit=true,
              healingConfirmed=false,overhealObserved=false,reason="intended-hit-confirmed",
              samples={{sequence=1,clock=100,playerId="uPLAYER",targetId="uTARGET",abilityId="A1111111111111111",
                status="ready",reason="observed-ready",player={health=100,power=0,combat=false},target={health=100},
                ability={idNew="A2222222222222222",target="uTARGET"}}},
              events={{kind="damage",clock=105,caster="uPLAYER",target="uTARGET",ability="A1111111111111111",
                abilityNew="A2222222222222222",normalizedAbilityId="A2222222222222222",
                abilityMappingSource="Event.Combat.abilityNew",damage=10,matchesAbility=true,matchesTarget=true}},cooldowns={}}}}
            """;
        void Require(bool okay, string message) { if (!okay) throw new Exception(message); }
        async Task<string> Input(string label, string contents)
        {
            var dir = Path.Combine(artifacts, label); Directory.CreateDirectory(dir);
            var file = Path.Combine(dir, "RiftReader2Casting.lua");
            await File.WriteAllTextAsync(file, contents, new UTF8Encoding(false));
            return file;
        }
        async Task<(int Exit, string Out, string Error)> Cli(params string[] args)
        {
            var priorOut = Console.Out; var priorError = Console.Error;
            using var stdout = new StringWriter(); using var stderr = new StringWriter();
            try
            {
                Console.SetOut(stdout); Console.SetError(stderr);
                var exit = await Rre.Reader.Program.Main(args);
                return (exit, stdout.ToString(), stderr.ToString());
            }
            finally { Console.SetOut(priorOut); Console.SetError(priorError); }
        }
        var noTrials = await Input("empty", empty);
        var emptyResult = await CastingEvidenceSource.ReadAsync(noTrials, repo);
        Require(emptyResult["status"]!.GetValue<string>() == "no-trials"
            && !emptyResult.ContainsKey("sequence"), "casting invented observations or sequence");
        passed.Add("empty casting source has no trial and no fabricated sequence");

        var positive = await Input("positive", observed);
        var actual = await CastingEvidenceSource.ReadAsync(positive, repo);
        Require(actual["trials"]![0]!["outcome"]!.GetValue<string>() == "exact-target-damage"
            && actual["sourceSha256"]!.GetValue<string>() == DataRules.Sha(await File.ReadAllBytesAsync(positive)),
            "casting outcome or original byte hash missing");
        passed.Add("actual Node and C# casting adapters preserve exact-target outcome and original hash");
        foreach (var flag in new[] { "live", "freshnessVerified", "processBuildVerified", "sourceAuthenticityVerified",
            "castDeliveryVerified", "eventHistoryComplete", "currentActionAuthorized" })
            Require(!actual["qualification"]![flag]!.GetValue<bool>(), "casting granted live authority");
        passed.Add("casting source never grants live freshness or action authority");

        var wrong = observed.Replace("abilityNew=\"A2222222222222222\"", "abilityNew=\"A3333333333333333\"");
        var negative = await CastingEvidenceSource.ReadAsync(await Input("wrong-modern", wrong), repo);
        Require(negative["trials"]![0]!["outcome"]!.GetValue<string>() == "inconclusive",
            "wrong modern ability was rescued by raw ability ID");
        passed.Add("C# consumer retains modern-ID precedence through the real parser");

        var malformed = await Input("executable", "RiftReader2CastingEvidence=(function() return {} end)()");
        try { await CastingEvidenceSource.ReadAsync(malformed, repo); throw new Exception("executable Lua accepted"); }
        catch (ReaderFailure e) when (e.Message == "casting-parser-rejected") { }
        passed.Add("executable Lua rejected before combat evidence");

        var output = Path.Combine(artifacts, "combat.json");
        var first = await Cli("combat", "--input", positive, "--repo", repo, "--output", output);
        Require(first.Exit == 0 && first.Out.Length == 0 && first.Error.Length == 0, "combat CLI publish failed");
        var original = await File.ReadAllBytesAsync(output);
        var second = await Cli("combat", "--input", positive, "--repo", repo, "--output", output);
        var after = await File.ReadAllBytesAsync(output);
        Require(second.Exit == 2 && second.Error.Contains("output-exists", StringComparison.Ordinal)
            && original.AsSpan().SequenceEqual(after), "combat CLI overwrote evidence");
        passed.Add("combat CLI publishes exclusively without overwriting evidence");

        var unavailable = await Cli("combat", "--input", Path.Combine(artifacts, "private@example.invalid", "RiftReader2Casting.lua"), "--repo", repo);
        Require(unavailable.Exit == 2 && unavailable.Out.Length == 0
            && !unavailable.Error.Contains("private@example.invalid", StringComparison.Ordinal), "combat CLI disclosed private path");
        passed.Add("unavailable original is rejected with bounded path-free diagnostics");

        const string savedLua = "RRECollectorData={addonVersion=\"0.4.11\",sequence=1,latest={addonVersion=\"0.4.11\",sequence=1,captureComplete=true,abilityList={apiAvailable=true,enumerationComplete=true,detailFailures=0,ignored=0,truncated=0,uniqueCount=1,detailCount=1,rawEntries=1},player={id=\"uFIXTURE\",name=\"Fixture\",level=1,calling=\"rogue\",combat=false,power=0},roleSlot=1,frameTime=10,realTime=20,abilities={{lookupId=\"A0000000100000000\",name=\"Fixture\",passive=false,cooldown=0}}}}";
        var savedFile = Path.Combine(artifacts, "RRECollector.lua");
        await File.WriteAllTextAsync(savedFile, savedLua, new UTF8Encoding(false));
        var legacy = await new SavedSource(savedFile, repo).ReadAsync();
        Require(legacy.Abilities.Count == 1 && legacy.Sequence == 1, "casting widened or broke collector source contract");
        passed.Add("existing collector SavedSource still uses its original inventory/sequence contract");
        return passed;
    }
}
