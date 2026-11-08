using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using Rre.Reader;

// Independent contract-only mode: no Lab-2 helper, guest operations, or
// deliberately spawned child-process tests. The default full suite is unchanged.
if (args is ["--production-only"])
{
    try
    {
        var checks = Rre.Reader.Checks.ProductionChecks.Run();
        Console.WriteLine(JsonSerializer.Serialize(new { status = "passed", count = checks.Count, checks }));
        return 0;
    }
    catch (Exception error)
    {
        Console.Error.WriteLine(JsonSerializer.Serialize(new { status = "failed", error = error.ToString() }));
        return 1;
    }
}
var repo = Path.GetFullPath(args.Length == 1 ? args[0] : ".");
var output = Path.Combine(repo, "artifacts", "reader-checks-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(output);
var passed = new List<string>();
void Check(bool value, string message) { if (!value) throw new Exception(message); }
async Task Run(string name, Func<Task> test) { await test(); passed.Add(name); }
Task Sync(Action action) { action(); return Task.CompletedTask; }
Task Reject(Action action) { try { action(); } catch (Exception error) when (error is ReaderFailure or JsonException or FormatException) { return Task.CompletedTask; } throw new Exception("Invalid input accepted"); }
const string session = "0123456789abcdef0123456789abcdef";
JsonObject Row(string id = "A0000000100000000") => new() { ["lookupId"] = id, ["name"] = "Fixture", ["passive"] = false, ["cooldown"] = 0 };
JsonObject Body(long seq = 2, int part = 1, int parts = 1, string id = "A0000000100000000") => new()
{
    ["schemaVersion"] = 1, ["producer"] = "RRE-feasibility-fixture", ["session"] = session,
    ["sequence"] = seq, ["part"] = part, ["parts"] = parts, ["records"] = new JsonArray(Row(id))
};
byte[] Wire(JsonObject body) => RawWire(body.ToJsonString());
byte[] RawWire(string body) { var b = Encoding.ASCII.GetBytes(body); return Encoding.ASCII.GetBytes($"RREC1|{session}|{b.Length:X8}|").Concat(b).Concat("|ENDRREC1"u8.ToArray()).ToArray(); }
JsonObject Decode(JsonObject body) => MemoryScanSource.DecodeFrame(Wire(body), session, 2);
const string lua = "RRECollectorData = {addonVersion=\"0.4.11\",sequence=1,latest={addonVersion=\"0.4.11\",sequence=1,captureComplete=true,abilityList={apiAvailable=true,enumerationComplete=true,detailFailures=0,ignored=0,truncated=0,uniqueCount=1,detailCount=1,rawEntries=1},player={id=\"uFIXTURE\",name=\"Fixture\",level=1,calling=\"rogue\",combat=false,power=0},roleSlot=1,frameTime=10,realTime=20,abilities={{lookupId=\"A0000000100000000\",name=\"Fixture\",passive=false,cooldown=0}}}}";
try
{
    await Run("frame preserves false and zero", () => Sync(() => { var b = Decode(Body()); Check(b["records"]![0]!["passive"]!.GetValue<bool>() == false && b["records"]![0]!["cooldown"]!.GetValue<int>() == 0, "scalar loss"); }));
    await Run("split parts assemble in part order", () => Sync(() => { var rows = MemoryScanSource.Assemble([Decode(Body(part:2,parts:2,id:"A0000000200000000")),Decode(Body(part:1,parts:2))]); Check(rows[0]!["lookupId"]!.GetValue<string>() == "A0000000100000000" && rows.Count == 2, "order"); }));
    await Run("missing part rejected", () => Reject(() => MemoryScanSource.Assemble([Decode(Body(parts:2))])));
    await Run("duplicate part rejected", () => Reject(() => MemoryScanSource.Assemble([Decode(Body(parts:2)),Decode(Body(parts:2))])));
    await Run("mixed sequence rejected", () => Reject(() => { var other = Decode(Body(part:2,parts:2,id:"A0000000200000000")); other["sequence"] = 1L; MemoryScanSource.Assemble([Decode(Body(parts:2)),other]); }));
    await Run("duplicate record across parts rejected", () => Reject(() => MemoryScanSource.Assemble([Decode(Body(parts:2)),Decode(Body(part:2,parts:2))])));
    await Run("wrong session rejected", () => Reject(() => MemoryScanSource.DecodeFrame(Wire(Body()),new string('f',32),2)));
    await Run("stale sequence rejected", () => Reject(() => Decode(Body(seq:1))));
    await Run("fractional sequence rejected", () => Reject(() => { var b = Body(); b["sequence"] = 2.5; Decode(b); }));
    await Run("boolean sequence rejected", () => Reject(() => { var b = Body(); b["sequence"] = true; Decode(b); }));
    await Run("unknown header field rejected", () => Reject(() => { var b = Body(); b["command"] = "untrusted"; Decode(b); }));
    await Run("wrong producer rejected", () => Reject(() => { var b = Body(); b["producer"] = "RiftReader2"; Decode(b); }));
    await Run("part zero rejected", () => Reject(() => { var b = Body(); b["part"] = 0; Decode(b); }));
    await Run("part budget rejected", () => Reject(() => Decode(Body(parts:17))));
    await Run("truncation rejected", () => Reject(() => MemoryScanSource.DecodeFrame(Wire(Body())[..^1],session,2)));
    await Run("trailing bytes rejected outside context", () => Reject(() => MemoryScanSource.DecodeFrame(Wire(Body()).Concat(new byte[]{1}).ToArray(),session,2)));
    await Run("context tail accepted only explicitly", () => Sync(() => MemoryScanSource.DecodeFrame(Wire(Body()).Concat(new byte[]{0}).ToArray(),session,2,true)));
    await Run("bad length rejected", () => Reject(() => { var b = Wire(Body()); b[39] = (byte)'Z'; MemoryScanSource.DecodeFrame(b,session,2); }));
    await Run("duplicate JSON field rejected", () => Reject(() => MemoryScanSource.DecodeFrame(RawWire(Body().ToJsonString()[..^1]+",\"sequence\":2}"),session,2)));
    await Run("nonfinite JSON rejected", () => Reject(() => DataRules.Parse("{\"x\":1e999}"u8.ToArray())));
    await Run("unknown record field rejected", () => Reject(() => { var b = Body(); b["records"]![0]!["command"] = "bad"; Decode(b); }));
    await Run("nested record field rejected", () => Reject(() => { var b = Body(); b["records"]![0]!["name"] = new JsonObject(); Decode(b); }));
    await Run("oversize record string rejected", () => Reject(() => { var row = Row(); row["name"] = new string('x',4097); DataRules.Abilities(new JsonArray(row)); }));
    await Run("no empty catalog claimed complete", () => Reject(() => DataRules.Abilities(new JsonArray())));
    await Run("malformed ID rejected", () => Reject(() => Decode(Body(id:"not-an-id"))));
    await Run("newline-suffixed ID rejected", () => Reject(() => Decode(Body(id:"A0000000100000000\n"))));
    await Run("newline-suffixed session rejected", () => Reject(() => MemoryScanSource.DecodeFrame(Wire(Body()),session+"\n",2)));
    await Run("record budget rejected", () => Reject(() => { var rows = new JsonArray(); for(var i=0;i<513;i++) rows.Add(Row($"A{i:X16}")); DataRules.Abilities(rows); }));
    await Run("public assembler validates schema", () => Reject(() => { var b = Decode(Body()); b["unknown"] = true; MemoryScanSource.Assemble([b]); }));
    await Run("public assembler rejects empty individual part", () => Reject(() => { var b = Decode(Body(parts:2)); b["records"] = new JsonArray(); MemoryScanSource.Assemble([b,Decode(Body(part:2,parts:2,id:"A0000000200000000"))]); }));
    await Run("public assembler rejects zero sequence", () => Reject(() => { var b = Decode(Body()); b["sequence"] = 0; MemoryScanSource.Assemble([b]); }));
    var wire = Wire(Body());
    JsonObject Scan() => new()
    {
        ["Encoding"] = "ascii", ["HitCount"] = 1, ["MaxHits"] = 16, ["SearchText"] = $"RREC1|{session}|",
        ["Hits"] = new JsonArray(new JsonObject
        {
            ["Encoding"] = "ascii", ["Address"] = 65536L,
            ["Context"] = new JsonObject { ["WindowStart"] = "0x10000", ["WindowLength"] = wire.Length,
                ["BytesHex"] = string.Join(" ",wire.Select(b=>b.ToString("X2"))) }
        })
    };
    var scanFile = Path.Combine(output,"scan.json"); await File.WriteAllTextAsync(scanFile,Scan().ToJsonString());
    var replay = await new MemoryScanSource(scanFile,session,2).ReadAsync();
    await Run("real-shaped scan envelope is decoded", () => Sync(() => Check(replay.Fixture && replay.Abilities.Count==1,"scan envelope")));
    await Run("all-module completeness respects unavailable context", () => Sync(() => Check(!ObservationModules.Build(replay,"all")["qualification"]!["complete"]!.GetValue<bool>(),"contradictory completeness")));
    await Run("ability-module completeness remains precise", () => Sync(() => Check(ObservationModules.Build(replay,"abilities")["qualification"]!["complete"]!.GetValue<bool>(),"ability completeness")));
    var malformedScan = Scan(); var hex = malformedScan["Hits"]![0]!["Context"]!["BytesHex"]!.GetValue<string>();
    malformedScan["Hits"]![0]!["Context"]!["BytesHex"] = " "+hex;
    var malformedPath = Path.Combine(output,"malformed-scan.json"); await File.WriteAllTextAsync(malformedPath,malformedScan.ToJsonString());
    await Run("noncanonical hex rejected at adapter boundary", async () => { try { await new MemoryScanSource(malformedPath,session,2).ReadAsync(); } catch(ReaderFailure e) when(e.Message=="context-hex-format") { return; } throw new Exception("hex accepted"); });
    var saved = Path.Combine(output,"valid.lua"); await File.WriteAllTextAsync(saved,lua,new UTF8Encoding(false));
    var capture = await new SavedSource(saved,repo).ReadAsync();
    await Run("saved existing parser preserves context", () => Sync(() => Check(capture.Context!["player"]!["power"]!.GetValue<int>() == 0 && capture.Context["player"]!["combat"]!.GetValue<bool>() == false, "context loss")));
    var targetedPath = Path.Combine(output,"targeted.lua"); await File.WriteAllTextAsync(targetedPath,lua.Replace("name=\"Fixture\",passive=false","name=\"Fixture\",target=\"uTARGET\",passive=false"));
    await Run("saved target survives historical crosswalk redaction", async () => { var c = await new SavedSource(targetedPath,repo).ReadAsync(); Check(c.Abilities[0]!["target"]!.GetValue<string>()=="uTARGET","target lost"); });
    await Run("persisted output never upgrades freshness", () => Sync(() => { var q = ObservationModules.Build(capture,"all")["qualification"]!; Check(!q["live"]!.GetValue<bool>() && !q["freshnessVerified"]!.GetValue<bool>() && !q["processBuildVerified"]!.GetValue<bool>() && !q["restartQualified"]!.GetValue<bool>(),"bad qualification"); }));
    await Run("context-only module excludes catalog", () => Sync(() => Check(!ObservationModules.Build(capture,"context")["modules"]!.AsObject().ContainsKey("abilities"),"wrong module")));
    await Run("fixture context remains unavailable", () => Sync(() => { var x = new SourceCapture(capture.Abilities,null,new JsonObject(),2,true); var o = ObservationModules.Build(x,"all"); Check(o["modules"]!["context"]!["status"]!.GetValue<string>()=="unavailable" && o["qualification"]!["fixture"]!.GetValue<bool>(),"invented context"); }));
    await Run("unknown module rejected", () => Reject(() => ObservationModules.Build(capture,"arbitrary")));
    await Run("public module builder rejects unvalidated empty capture", () => Reject(() => ObservationModules.Build(new SourceCapture(new JsonArray(),null,new JsonObject(),1,false),"all")));
    var old = Path.Combine(output,"preserved-old.lua"); await File.WriteAllTextAsync(old,lua.Replace("latest={addonVersion=\"0.4.11\"","latest={addonVersion=\"0.1.0\""));
    await Run("older retained capture version is preserved", async () => { var c = await new SavedSource(old,repo).ReadAsync(); Check(c.Evidence["producerVersion"]!.GetValue<string>()=="0.1.0" && c.Evidence["savedAddonVersion"]!.GetValue<string>()=="0.4.11","version conflation"); });
    var bad = Path.Combine(output,"expression.lua"); await File.WriteAllTextAsync(bad,"RRECollectorData = os.execute(\"never\")");
    await Run("Lua expression rejected before evaluation", async () => { try { await new SavedSource(bad,repo).ReadAsync(); } catch(ReaderFailure) { return; } throw new Exception("expression accepted"); });
    var incomplete = Path.Combine(output,"incomplete.lua"); await File.WriteAllTextAsync(incomplete,lua.Replace("captureComplete=true","captureComplete=false"));
    await Run("incomplete saved capture rejected", async () => { try { await new SavedSource(incomplete,repo).ReadAsync(); } catch(ReaderFailure) { return; } throw new Exception("partial accepted"); });
    var oversized = Path.Combine(output,"oversize.lua"); await File.WriteAllBytesAsync(oversized,new byte[2_000_001]);
    await Run("saved byte cap before child invocation", async () => { try { await new SavedSource(oversized,repo).ReadAsync(); } catch(ReaderFailure e) when(e.Message=="input-byte-limit") { return; } throw new Exception("oversize accepted"); });
    var published = Path.Combine(output,"published.json");
    await Run("publish refuses existing evidence", () => Sync(() => { Rre.Reader.Program.Publish(published,"original"); try { Rre.Reader.Program.Publish(published,"overwrite"); throw new Exception("overwrite accepted"); } catch(ReaderFailure) { Check(File.ReadAllText(published)=="original","evidence changed"); } }));
    await Run("no publish temporary survives", () => Sync(() => Check(Directory.GetFiles(output,".rre-*.tmp").Length==0,"temp leak")));
    passed.AddRange(Rre.Reader.Checks.NativeChecks.Run());
    passed.AddRange(Rre.Reader.Checks.ProductionChecks.Run());
    passed.AddRange(await Rre.Reader.Checks.Lab2Checks.RunAsync(repo,output));
    var summary = new {status="passed",count=passed.Count,checks=passed,output};
    await File.WriteAllTextAsync(Path.Combine(output,"checks.json"),JsonSerializer.Serialize(summary));
    Console.WriteLine(JsonSerializer.Serialize(summary));
    return 0;
}
catch(Exception error)
{
    Console.Error.WriteLine(JsonSerializer.Serialize(new {status="failed",passed=passed.Count,error=error.ToString(),output}));
    return 1;
}
