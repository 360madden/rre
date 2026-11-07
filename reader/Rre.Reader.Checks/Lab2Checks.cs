using System.Diagnostics;
using System.Text;
using System.Text.Json.Nodes;
using Rre.Reader;

namespace Rre.Reader.Checks;

public static class Lab2Checks
{
    public static async Task<IReadOnlyList<string>> RunAsync(string repo,string output)
    {
        var passed=new List<string>();
        JsonObject Read(string name)=>JsonNode.Parse(File.ReadAllText(Path.Combine(repo,"artifacts","sc628-live-context-20261107-1533",name)))!.AsObject();
        byte[] Bytes(JsonObject value)=>Encoding.UTF8.GetBytes(value.ToJsonString());
        var request=File.ReadAllBytes(Path.Combine(repo,"artifacts","sc628-live-context-20261107-1533","wire","request.json"));
        var snapshot=File.ReadAllBytes(Path.Combine(repo,"artifacts","sc628-live-context-20261107-1533","wire","snapshot.json"));
        var target=JsonNode.Parse(request)!["target"]!;
        var expected=Read("expected-wire.json");var install=Read("install/receipt.json");
        JsonObject Binding()=>new()
        {
            ["schemaVersion"]=1,["evidenceKind"]="rre-lab2-publication-binding/1",["processId"]=target["processId"]!.DeepClone(),
            ["processStartUtcTicks"]=target["processStartUtcTicks"]!.ToString(),["executableSha256"]=Lab2Source.Build,
            ["addonVersion"]="0.4.13",["session"]=expected["session"]!.DeepClone(),["sequence"]=7,["parts"]=5,["payloadBytes"]=18295,
            ["imagePath"]=expected["image"]!.DeepClone(),["imageSha256"]=expected["imageSha256"]!.DeepClone(),["observedAtUtc"]="2026-11-07T20:40:54Z"
        };
        JsonObject Window()=>new()
        {
            ["schemaVersion"]=1,["evidenceKind"]="rre-lab2-window/1",["target"]="Lab2",["startsAtUtc"]="2026-11-07T20:36:32.953019Z",
            ["endsAtUtc"]="2026-11-07T20:51:32Z",["owner"]="Offline composite fixture; no permission or live operation"
        };
        var sources=new Dictionary<string,string>{["offline-fixture-not-a-live-helper"]=new string('0',64)};
        JsonObject Receipt(JsonObject b,JsonObject w)=>new()
        {
            ["schemaVersion"]=1,["evidenceKind"]="rre-lab2-acquisition/1",["status"]="acquired-cleaned-awaiting-decode",
            ["startedAtUtc"]="2026-11-07T20:41:00Z",["completedAtUtc"]="2026-11-07T20:42:00Z",
            ["bindingSha256"]=DataRules.Sha(Bytes(b)),["windowSha256"]=DataRules.Sha(Bytes(w)),
            ["requestSha256"]=DataRules.Sha(request),["snapshotSha256"]=DataRules.Sha(snapshot),["guestCleanupComplete"]=true,
            ["vmIdentity"]=install["vmIdentity"]!.DeepClone(),["guestRoot"]=@"C:\Users\Public\Documents\RRE-Acquire-00000000000000000000000000000001",
            ["sourceHashes"]=new JsonObject{[sources.Keys.Single()]=sources.Values.Single()},
            ["freshGameIdentity"]=new JsonObject
            {
                ["processId"]=target["processId"]!.DeepClone(),["processStartUtcTicks"]=target["processStartUtcTicks"]!.ToString(),
                ["executablePath"]=@"C:\RIFT_TRANSFER\RIFT\rift_x64.exe",["executableSha256"]=Lab2Source.Build,["machine"]="RIFT-LAB-2"
            },
            ["scoutPasses"]=new JsonArray(new JsonObject{["status"]="partial",["reason"]="fixture",["nextAddress"]="0x20000",
                ["attemptedBytes"]=770723840,["examinedBytes"]=770723840,["holes"]=new JsonArray(),["coveredSpans"]=new JsonArray(),
                ["candidateCount"]=6,["exactStarts"]=Read("scan-001/receipt.json")["exactFrameStarts"]!.DeepClone()})
        };
        SourceCapture Decode(JsonObject b,JsonObject w,JsonObject a)=>Lab2Source.DecodeAcquired(Bytes(b),Bytes(w),Bytes(a),request,snapshot,output,sources);
        void Accept(string name,Action action){action();passed.Add(name);}
        void BadReceipt(string name,Action<JsonObject> mutate)
        {
            var b=Binding();var w=Window();var a=Receipt(b,w);mutate(a);
            try{Decode(b,w,a);}catch(ReaderFailure){passed.Add(name);return;}throw new Exception("Bad Lab2 receipt accepted: "+name);
        }
        Accept("Lab2 offline composite decodes retained54 records with qualification false",()=>
        {
            var b=Binding();var w=Window();var capture=Decode(b,w,Receipt(b,w));
            if(capture.Abilities.Count!=54 || capture.Context!["player"]!["zone"]!.GetValue<string>()!="z0000000CB7B53FD7")throw new Exception("composite loss");
            var q=ObservationModules.Build(capture,"all")["qualification"]!.AsObject();
            foreach(var key in new[]{"live","freshnessVerified","processBuildVerified","runtimeProducerVerified","sourceAuthenticityVerified","atomicSnapshotVerified","restartQualified"})
                if(q[key]!.GetValue<bool>())throw new Exception("false qualification upgraded");
        });
        BadReceipt("Lab2 incomplete cleanup rejected",a=>a["guestCleanupComplete"]=false);
        BadReceipt("Lab2 snapshot hash drift rejected",a=>a["snapshotSha256"]=new string('0',64));
        BadReceipt("Lab2 input hash drift rejected",a=>a["bindingSha256"]=new string('0',64));
        BadReceipt("Lab2 other VM rejected",a=>a["vmIdentity"]!["port"]=5961);
        BadReceipt("Lab2 unreviewed source key rejected",a=>a["sourceHashes"]!["C:\\unrelated-secret"]=new string('0',64));
        BadReceipt("Lab2 source hash disagreement rejected",a=>a["sourceHashes"]![sources.Keys.Single()]=new string('1',64));
        BadReceipt("Lab2 foreign guest scope rejected",a=>a["guestRoot"]=@"C:\Windows\foreign");
        BadReceipt("Lab2 false fresh process ticks rejected",a=>a["freshGameIdentity"]!["processStartUtcTicks"]="639294897826627678");
        BadReceipt("Lab2 reversed acquisition interval rejected",a=>a["completedAtUtc"]="2026-11-07T20:40:00Z");
        BadReceipt("Lab2 retained native capture cannot predate claimed active acquisition",a=>a["startedAtUtc"]="2026-11-07T20:41:58Z");
        BadReceipt("Lab2 native capture cannot finish after acquisition receipt",a=>a["completedAtUtc"]="2026-11-07T20:41:56Z");
        BadReceipt("Lab2 unbounded scout rejected",a=>a["scoutPasses"]![0]!["attemptedBytes"]=1_073_741_825L);
        BadReceipt("Lab2 late admission cannot be replayed as valid",a=>{a["startedAtUtc"]="2026-11-07T20:51:31Z";a["completedAtUtc"]="2026-11-07T20:51:32Z";});
        Accept("Lab2 malformed image binding rejected before composite acceptance",()=>
        {
            var b=Binding();b["imageSha256"]=false;var w=Window();
            try{Decode(b,w,Receipt(b,w));}catch(ReaderFailure){return;}throw new Exception("image metadata accepted");
        });
        JsonObject Scope()
        {
            var root=@"C:\Users\Public\Documents\RRE-Acquire-00000000000000000000000000000001";
            var files=new JsonObject();var processes=new JsonObject();var number=100;
            foreach(var label in new[]{"scout-1","snapshot"})
            {
                var remote=root+"-"+label+".process.json";files[remote]=new string('A',64);
                processes[remote]=new JsonObject{["exitConfirmed"]=true,["hostJournal"]=Path.Combine(output,label+".process.json"),
                    ["identity"]=new JsonObject{["pid"]=number++,["ticks"]="1",["path"]=Lab2Source.NativeHelperPath}};
            }
            return new JsonObject{["root"]=root,["knownFiles"]=files,["directories"]=new JsonArray(root+"-scout-1"),
                ["processes"]=processes,["controlQuarantined"]=false,["cleanupComplete"]=true};
        }
        void ScopeCase(string name,Action<JsonObject>? mutate=null)
        {
            var scope=Scope();var b=Binding();var w=Window();var a=Receipt(b,w);
            if(mutate is null){Lab2Source.ValidateScope(scope,a,output);passed.Add(name);return;}
            mutate(scope);
            try{Lab2Source.ValidateScope(scope,a,output);}catch(ReaderFailure){passed.Add(name);return;}throw new Exception("Bad recovery scope accepted");
        }
        ScopeCase("Lab2 complete scoped process-exit journals accepted offline");
        ScopeCase("Lab2 favorable scope flags alone are insufficient",s=>s.Remove("processes"));
        ScopeCase("Lab2 scope must match this acquisition",s=>s["root"]=@"C:\Users\Public\Documents\RRE-Acquire-00000000000000000000000000000002");
        ScopeCase("Lab2 unknown file hash prevents cleanup acceptance",s=>s["knownFiles"]![s["knownFiles"]!.AsObject().First().Key]=null);
        ScopeCase("Lab2 unconfirmed native exit prevents acceptance",s=>s["processes"]!.AsObject().First().Value!["exitConfirmed"]=false);
        ScopeCase("Lab2 foreign host process journal rejected",s=>s["processes"]!.AsObject().First().Value!["hostJournal"]=Path.Combine(repo,"outside.json"));
        ScopeCase("Lab2 foreign native process path rejected",s=>s["processes"]!.AsObject().First().Value!["identity"]!["path"]=@"C:\RIFT_TRANSFER\RIFT\rift_x64.exe");
        var actualScope=Read("../sc625-live-adapter-trial2-20261107-1655/acquisition/guest-scope.json");
        Accept("Trial2 exact retained acquisition decodes offline without relabeling failed CLI",()=>
        {
            var trial=Path.Combine(repo,"artifacts","sc625-live-adapter-trial2-20261107-1655");
            var acquired=Path.Combine(trial,"acquisition");
            byte[] Raw(string path)=>File.ReadAllBytes(path);
            var receipt=JsonNode.Parse(Raw(Path.Combine(acquired,"acquisition.json")))!.AsObject();
            var pins=new Dictionary<string,string>(Lab2Source.Dependencies,StringComparer.Ordinal)
            {
                [Path.Combine(repo,"tools","rre_lab2_acquire.py")]=Lab2Source.HelperSha,
                [Path.Combine(trial,"binding.json")]=DataRules.Sha(Raw(Path.Combine(trial,"binding.json"))),
                [Path.Combine(trial,"window.json")]=DataRules.Sha(Raw(Path.Combine(trial,"window.json")))
            };
            var decoded=Lab2Source.DecodeAcquired(Raw(Path.Combine(trial,"binding.json")),Raw(Path.Combine(trial,"window.json")),Raw(Path.Combine(acquired,"acquisition.json")),Raw(Path.Combine(acquired,"request.json")),Raw(Path.Combine(acquired,"snapshot.json")),acquired,pins);
            Lab2Source.ValidateScope(actualScope,receipt,acquired);
            if(decoded.Abilities.Count!=54 || decoded.Sequence!=9)throw new Exception("trial2 publication mismatch");
            File.WriteAllText(Path.Combine(output,"trial2-offline-reader.json"),ObservationModules.Build(decoded,"all").ToJsonString()+"\n");
        });
        foreach(var (remote,node) in actualScope["processes"]!.AsObject())
        {
            var file=Path.Combine(repo,"artifacts","sc625-live-adapter-trial2-20261107-1655","acquisition",Path.GetFileName(node!["hostJournal"]!.GetValue<string>()));
            var raw=File.ReadAllBytes(file);var declared=actualScope["knownFiles"]![remote]!.GetValue<string>();var identity=node!["identity"];
            Accept("Owned PowerShell BOM journal retains exact raw SHA: "+Path.GetFileName(remote),()=>Lab2Source.ValidateOwnedProcessJournal(raw,declared,identity));
            var plain=raw[3..];Accept("Owned no-BOM journal remains valid: "+Path.GetFileName(remote),()=>Lab2Source.ValidateOwnedProcessJournal(plain,DataRules.Sha(plain),identity));
        }
        var journal=Encoding.UTF8.GetBytes("{\"pid\":1}");var bom=new byte[]{0xEF,0xBB,0xBF};
        void BadJournal(string name,byte[] bytes,string? declared=null,JsonNode? identity=null)
        {
            try{Lab2Source.ValidateOwnedProcessJournal(bytes,declared??DataRules.Sha(bytes),identity??JsonNode.Parse(journal));}
            catch(Exception error) when(error is ReaderFailure or System.Text.Json.JsonException){passed.Add(name);return;}
            throw new Exception("Bad journal accepted: "+name);
        }
        BadJournal("Owned journal mutation still fails original raw hash",bom.Concat(journal).ToArray(),new string('0',64));
        BadJournal("Owned journal identity mismatch rejected",bom.Concat(journal).ToArray(),identity:JsonNode.Parse("{\"pid\":2}"));
        BadJournal("Owned journal repeated BOM rejected",bom.Concat(bom).Concat(journal).ToArray());
        BadJournal("Owned journal UTF16 BOM rejected",new byte[]{0xFF,0xFE}.Concat(journal).ToArray());
        BadJournal("Owned journal BOM-only rejected",bom);
        Accept("Global strict JSON parser still rejects BOM",()=>{try{DataRules.Parse(bom.Concat(journal).ToArray());}catch(System.Text.Json.JsonException){return;}throw new Exception("global parser widened");});
        Accept("Lab2 decoded publication must match optional-field producer version",()=>
        {
            var b=Binding();b["addonVersion"]="0.4.12";var w=Window();
            try{Decode(b,w,Receipt(b,w));}catch(ReaderFailure){return;}throw new Exception("producer mismatch accepted");
        });
        Accept("Lab2 final output preflight rejects existing file before helper",()=>
        {
            var existing=Path.Combine(output,"existing-output.json");File.WriteAllText(existing,"preserve");
            try{Lab2Source.Preflight(repo,Path.Combine(repo,"artifacts","unused-"+Guid.NewGuid().ToString("N")),existing);}
            catch(ReaderFailure){if(File.ReadAllText(existing)!="preserve")throw new Exception("output altered");return;}
            throw new Exception("late-output rejection");
        });
        Accept("Lab2 validate command cannot acquire",()=>
        {
            var result=Rre.Reader.Program.Main(["validate","--source","lab2","--input","unused.json"]).GetAwaiter().GetResult();
            if(result!=2)throw new Exception("validate did not reject");
        });
        var bindingFile=Path.Combine(output,"source-set-binding.json");var windowFile=Path.Combine(output,"source-set-window.json");
        await File.WriteAllBytesAsync(bindingFile,Bytes(Binding()));await File.WriteAllBytesAsync(windowFile,Bytes(Window()));
        var helper=Path.Combine(repo,"tools","rre_lab2_acquire.py");
        var sourceScript="import importlib.util,json,sys;from pathlib import Path;s=importlib.util.spec_from_file_location('rre',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print(json.dumps(m.execution_hashes(sys.argv[2],Path(sys.argv[2]).read_bytes(),sys.argv[3],Path(sys.argv[3]).read_bytes())))";
        var sourceRun=await OwnedProcess.RunAsync(Lab2Source.Python,["-B","-c",sourceScript,helper,bindingFile,windowFile],repo,CancellationToken.None);
        if(sourceRun.ExitCode!=0)throw new Exception("offline execution-source interop failed: "+sourceRun.Stderr);
        var sourceObject=JsonNode.Parse(sourceRun.Stdout)!.AsObject();
        var fixedSources=new Dictionary<string,string>(Lab2Source.Dependencies,StringComparer.Ordinal)
        {
            [helper]=DataRules.Sha(await File.ReadAllBytesAsync(helper)),[bindingFile]=DataRules.Sha(await File.ReadAllBytesAsync(bindingFile)),
            [windowFile]=DataRules.Sha(await File.ReadAllBytesAsync(windowFile))
        };
        if(sourceObject.Count!=10 || fixedSources.Count!=10 || fixedSources.Any(x=>!sourceObject.Any(y=>y.Key.Equals(x.Key,StringComparison.OrdinalIgnoreCase) && y.Value!.GetValue<string>().Equals(x.Value,StringComparison.OrdinalIgnoreCase))))
            throw new Exception("Python/C# exact source set disagreement");
        passed.Add("Python and C# agree on all10 fixed execution and input source hashes offline");
        var pidPath=Path.Combine(output,"owned-timeout.pid");
        var script="import os,time;from pathlib import Path;Path("+System.Text.Json.JsonSerializer.Serialize(pidPath)+").write_text(str(os.getpid()));time.sleep(30)";
        try{await OwnedProcess.RunAsync(Lab2Source.Python,["-B","-c",script],repo,CancellationToken.None,TimeSpan.FromSeconds(1));throw new Exception("timeout missing");}
        catch(OperationCanceledException)
        {
            if(!File.Exists(pidPath))throw new Exception("controlled child did not start");
            var pid=int.Parse(await File.ReadAllTextAsync(pidPath));
            try{using var child=Process.GetProcessById(pid);if(!child.HasExited)throw new Exception("owned child survived timeout");}catch(ArgumentException){}
            passed.Add("OwnedProcess timeout terminates its controlled host child");
        }
        return passed;
    }
}
