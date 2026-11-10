using System.Globalization;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

namespace Rre.Reader;

/// <summary>Explicit bounded read-only acquisition; RREC2 semantics stay in NativeSnapshotSource.</summary>
public sealed class Lab2Source(string input, string windowPath, string evidenceDirectory, string repository) : IObservationSource
{
    public const string Root = @"C:\work\rre";
    public const string Python = @"C:\work\rre\.venv\Scripts\python.exe";
    public const string Bundle = "F4148B838AF694EF95FD46DE76859CE9DF55194A9FE8BE1DF74FC2F8F0BCE80F";
    public const string NativeHelperPath = @"C:\Users\mrkoo\AppData\Local\RiftReader2\codex-jobs\current-ability-records-F4148B838AF694EF\RiftReader2.Live.exe";
    public const string Build = "1935A05C9DB6D468E34E0055014A4A99C1B5AFCEB1695884E24600F5C20A4BE8";
    public const string HelperSha = "4F3315324DF204D9C40F0477A65578B3126BA5C8DB74CFB159C9E9E739D95154";
    public static readonly IReadOnlyDictionary<string,string> Dependencies = new Dictionary<string,string>(StringComparer.Ordinal)
    {
        [@"C:\work\riftreader2\scripts\vmware_guest_session.py"]="A3808F907224FEA709F2709CAB56345859474D268B910087A4236B2A0AED4048",
        [@"C:\work\riftreader2\scripts\vm_console_native.py"]="5B6863660F23712C14C9548DFF96A10FC0E7BF1DEE95CF3B3D3362E35A4E6990",
        [@"C:\work\riftreader2\scripts\launch_live_reader.py"]="E70EF5A1D80688ADBE029874EDEE4052259A42F780342E37A751964A8C3C3199",
        [@"C:\Program Files\VMware\VMware Workstation\vmrun.exe"]="112EC6C7D122F8D9220A5D44CC4B59AD270BA1D7CEFAECEE38FD07C2A4DAFE30",
        [Python]="199CE15A9F0D4F9522EDBA59338E4879D28CF61F88E377B8164BCB716275ED22",
        [@"C:\Python314\python.exe"]="03168C01B7B7491423350E82C26FEE71F35B43694D1319D3C668BDA6903A0C38",
        [@"C:\Python314\python314.dll"]="FDE89CDB5C2D08AE65DE7EF4ABCA1876C93BA3796002F5AC0BF7E4D4F5A94DA0"
    };
    public static bool Under(string path,string parent) => Path.GetFullPath(path).StartsWith(Path.GetFullPath(parent).TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase);
    public static void Preflight(string repo,string evidence,string? finalOutput)
    {
        DataRules.Require(Path.GetFullPath(repo).TrimEnd(Path.DirectorySeparatorChar).Equals(Root,StringComparison.OrdinalIgnoreCase),"lab2-fixed-repository");
        DataRules.Require(Under(evidence,Path.Combine(Root,"artifacts")) && !File.Exists(evidence) && !Directory.Exists(evidence)
            && Directory.Exists(Path.GetDirectoryName(Path.GetFullPath(evidence))),"lab2-fresh-evidence-directory");
        if(finalOutput is not null)
        {
            var full=Path.GetFullPath(finalOutput);
            DataRules.Require(!File.Exists(full) && !Directory.Exists(full) && Directory.Exists(Path.GetDirectoryName(full))
                && !Under(full,evidence) && !full.Equals(Path.GetFullPath(evidence),StringComparison.OrdinalIgnoreCase),"lab2-final-output-preflight");
        }
    }
    public async Task<SourceCapture> ReadAsync(CancellationToken cancellationToken=default)
    {
        Preflight(repository,evidenceDirectory,null);
        var bindingBytes=await DataRules.ReadFileAsync(input,8192,cancellationToken);
        var windowBytes=await DataRules.ReadFileAsync(windowPath,8192,cancellationToken);
        var binding=Binding(bindingBytes);
        var window=Window(windowBytes);
        var image=BoundImage(binding);
        var imageBytes=await DataRules.ReadFileAsync(image,20*1024*1024,cancellationToken);
        DataRules.Require(imageBytes.AsSpan().StartsWith(new byte[]{137,80,78,71,13,10,26,10})
            && Same(DataRules.Sha(imageBytes),DataRules.Text(binding["imageSha256"],"binding-image-sha")),"lab2-image-drift");
        var now=DateTimeOffset.UtcNow;
        DataRules.Require(now>=Time(window["startsAtUtc"]) && Time(window["endsAtUtc"])-now>=TimeSpan.FromSeconds(60)
            && now-Time(binding["observedAtUtc"]) is var age && age>=TimeSpan.Zero && age<=TimeSpan.FromMinutes(15),"lab2-window-or-binding-age");
        var helper=Path.Combine(Root,"tools","rre_lab2_acquire.py");
        var expected=new Dictionary<string,string>(Dependencies,StringComparer.Ordinal)
        {
            [helper]=HelperSha,[Path.GetFullPath(input)]=DataRules.Sha(bindingBytes),[Path.GetFullPath(windowPath)]=DataRules.Sha(windowBytes)
        };
        await CheckFiles(expected,cancellationToken);
        var run=await OwnedProcess.RunAsync(Python,["-B",helper,"--binding",Path.GetFullPath(input),"--window",Path.GetFullPath(windowPath),"--output",Path.GetFullPath(evidenceDirectory)],Root,cancellationToken,TimeSpan.FromSeconds(240));
        DataRules.Require(run.ExitCode==0,"lab2-helper-failed-see-evidence");
        DataRules.Require(!File.Exists(Path.Combine(evidenceDirectory,"failure.json")),"lab2-helper-failure-receipt");
        var acquisitionBytes=await DataRules.ReadFileAsync(Path.Combine(evidenceDirectory,"acquisition.json"),2_000_000,cancellationToken);
        var request=await DataRules.ReadFileAsync(Path.Combine(evidenceDirectory,"request.json"),1_000_000,cancellationToken);
        var snapshot=await DataRules.ReadFileAsync(Path.Combine(evidenceDirectory,"snapshot.json"),2_000_000,cancellationToken);
        var capture=DecodeAcquired(bindingBytes,windowBytes,acquisitionBytes,request,snapshot,evidenceDirectory,expected);
        var cleanupBytes=await DataRules.ReadFileAsync(Path.Combine(evidenceDirectory,"guest-cleanup.json"),256_000,cancellationToken);
        var cleanup=DataRules.Object(DataRules.Parse(cleanupBytes),"lab2-cleanup");
        DataRules.ExactKeys(cleanup,"complete","failures");
        DataRules.Require(DataRules.Boolean(cleanup["complete"],"cleanup-complete") && cleanup["failures"] is JsonArray {Count:0},"lab2-cleanup-contradiction");
        var scopeBytes=await DataRules.ReadFileAsync(Path.Combine(evidenceDirectory,"guest-scope.json"),256_000,cancellationToken);
        var scope=DataRules.Object(DataRules.Parse(scopeBytes),"lab2-scope");
        ValidateScope(scope,DataRules.Object(DataRules.Parse(acquisitionBytes),"acquisition"),evidenceDirectory);
        var finalFiles=new Dictionary<string,string>(expected,StringComparer.Ordinal)
        {
            [image]=DataRules.Sha(imageBytes),[Path.Combine(evidenceDirectory,"acquisition.json")]=DataRules.Sha(acquisitionBytes),
            [Path.Combine(evidenceDirectory,"request.json")]=DataRules.Sha(request),[Path.Combine(evidenceDirectory,"snapshot.json")]=DataRules.Sha(snapshot),
            [Path.Combine(evidenceDirectory,"guest-cleanup.json")]=DataRules.Sha(cleanupBytes),[Path.Combine(evidenceDirectory,"guest-scope.json")]=DataRules.Sha(scopeBytes)
        };
        foreach(var (remote,node) in scope["processes"]!.AsObject())
        {
            var local=Path.Combine(evidenceDirectory,remote[(DataRules.Text(scope["root"],"root").Length+1)..]);
            var bytes=await DataRules.ReadFileAsync(local,8192,cancellationToken);
            ValidateOwnedProcessJournal(bytes,DataRules.Text(scope["knownFiles"]![remote],"journal-sha"),node!["identity"]);
            finalFiles[local]=DataRules.Sha(bytes);
        }
        await CheckFiles(finalFiles,cancellationToken);
        Program.Publish(Path.Combine(evidenceDirectory,"acceptance.json"),new JsonObject
        {
            ["schemaVersion"]=1,["status"]="acquired-cleaned-decoded",["acquisitionSha256"]=DataRules.Sha(acquisitionBytes),
            ["payloadSha256"]=capture.Evidence["payloadSha256"]?.DeepClone(),["sequence"]=capture.Sequence,
            ["cleanupSha256"]=DataRules.Sha(cleanupBytes),["scopeSha256"]=DataRules.Sha(scopeBytes),
            ["qualification"]=ObservationModules.Build(capture,"all")["qualification"]!.DeepClone()
        }.ToJsonString()+"\n");
        return capture;
    }
    private static async Task CheckFiles(IReadOnlyDictionary<string,string> expected,CancellationToken ct)
    {
        foreach(var (path,sha) in expected)
            DataRules.Require(Same(DataRules.Sha(await DataRules.ReadFileAsync(path,32*1024*1024,ct)),sha),"lab2-dependency-or-input-drift");
    }
    public static SourceCapture DecodeAcquired(byte[] bindingBytes,byte[] windowBytes,byte[] acquisitionBytes,byte[] request,byte[] snapshot,string evidence,IReadOnlyDictionary<string,string> expectedSources)
    {
        var b=Binding(bindingBytes);var w=Window(windowBytes);
        var a=DataRules.Object(DataRules.Parse(acquisitionBytes),"lab2-acquisition");
        DataRules.ExactKeys(a,"schemaVersion","evidenceKind","status","startedAtUtc","completedAtUtc","bindingSha256","windowSha256","requestSha256","snapshotSha256","guestCleanupComplete","vmIdentity","scoutPasses","sourceHashes","guestRoot","freshGameIdentity");
        DataRules.Require(DataRules.Integer(a["schemaVersion"],"lab2-schema")==1 && DataRules.Text(a["evidenceKind"],"lab2-kind")=="rre-lab2-acquisition/1"
            && DataRules.Text(a["status"],"lab2-status")=="acquired-cleaned-awaiting-decode" && DataRules.Boolean(a["guestCleanupComplete"],"lab2-cleanup"),"lab2-acquisition-contract");
        foreach(var (key,bytes) in new[]{("bindingSha256",bindingBytes),("windowSha256",windowBytes),("requestSha256",request),("snapshotSha256",snapshot)})
            DataRules.Require(Same(DataRules.Text(a[key],key),DataRules.Sha(bytes)),"lab2-acquisition-hash");
        var begin=Time(a["startedAtUtc"]);var end=Time(a["completedAtUtc"]);
        DataRules.Require(begin>=Time(w["startsAtUtc"]) && end>=begin && end-begin<=TimeSpan.FromSeconds(240)
            && Time(w["endsAtUtc"])-begin>=TimeSpan.FromSeconds(60) && begin-Time(b["observedAtUtc"]) is var age
            && age>=TimeSpan.Zero && age<=TimeSpan.FromMinutes(15),"lab2-acquisition-clock");
        var vm=DataRules.Object(a["vmIdentity"],"lab2-vm");
        DataRules.ExactKeys(vm,"vmx","port","logEpoch","listenerPid","pid","image","startTicks");
        DataRules.Require(DataRules.Text(vm["vmx"],"vmx").Equals(@"c:\rift modding\vms\rift-lab-2\rift-lab.vmx",StringComparison.OrdinalIgnoreCase)
            && DataRules.Integer(vm["port"],"vm-port")==5962 && DataRules.Integer(vm["pid"],"vm-pid") is >0 and <=int.MaxValue
            && DataRules.Integer(vm["listenerPid"],"listener-pid")==DataRules.Integer(vm["pid"],"vm-pid")
            && DataRules.Integer(vm["startTicks"],"vm-start")>0
            && DataRules.Text(vm["image"],"vm-image").Equals(@"C:\Program Files\VMware\VMware Workstation\x64\vmware-vmx.exe",StringComparison.OrdinalIgnoreCase),"lab2-vm-target");
        Time(vm["logEpoch"]);
        var fresh=DataRules.Object(a["freshGameIdentity"],"lab2-game");
        DataRules.ExactKeys(fresh,"machine","processId","processStartUtcTicks","executablePath","executableSha256");
        DataRules.Require(DataRules.Text(fresh["machine"],"machine")=="RIFT-LAB-2" && DataRules.Integer(fresh["processId"],"pid")==DataRules.Integer(b["processId"],"pid")
            && DataRules.Text(fresh["processStartUtcTicks"],"ticks")==DataRules.Text(b["processStartUtcTicks"],"ticks")
            && DataRules.Text(fresh["executablePath"],"game-path").Equals(@"C:\RIFT_TRANSFER\RIFT\rift_x64.exe",StringComparison.OrdinalIgnoreCase)
            && Same(DataRules.Text(fresh["executableSha256"],"build"),Build),"lab2-fresh-game-binding");
        DataRules.Require(Regex.IsMatch(DataRules.Text(a["guestRoot"],"guest-root"),@"\AC:\\Users\\Public\\Documents\\RRE-Acquire-[0-9a-f]{32}\z"),"lab2-guest-scope");
        var sources=DataRules.Object(a["sourceHashes"],"lab2-sources");
        DataRules.Require(sources.Count==expectedSources.Count && sources.Select(x=>x.Key).Distinct(StringComparer.OrdinalIgnoreCase).Count()==sources.Count
            && sources.All(x=>expectedSources.Keys.Contains(x.Key,StringComparer.OrdinalIgnoreCase)),"lab2-source-key-set");
        foreach(var (path,sha) in expectedSources)DataRules.Require(Same(DataRules.Text(sources.First(x=>x.Key.Equals(path,StringComparison.OrdinalIgnoreCase)).Value,"source-sha"),sha),"lab2-source-hash");
        DataRules.Require(a["scoutPasses"] is JsonArray {Count:>=1 and <=3},"lab2-scout-count");
        var located=new HashSet<string>(StringComparer.Ordinal);
        foreach(var item in a["scoutPasses"]!.AsArray())
        {
            var p=DataRules.Object(item,"scout-pass");DataRules.ExactKeys(p,"status","reason","nextAddress","attemptedBytes","examinedBytes","holes","coveredSpans","candidateCount","exactStarts");
            DataRules.Require(DataRules.Integer(p["attemptedBytes"],"scan-bytes") is >=0 and <=1_073_741_824
                && DataRules.Integer(p["candidateCount"],"candidate-count") is >=0 and <=128
                && DataRules.Integer(p["examinedBytes"],"examined-bytes")>=0 && DataRules.Integer(p["examinedBytes"],"examined-bytes")<=DataRules.Integer(p["attemptedBytes"],"scan-bytes")
                && DataRules.Text(p["status"],"scout-status") is "complete" or "partial"
                && p["holes"] is JsonArray {Count:<=32768} && p["coveredSpans"] is JsonArray {Count:<=32768}
                && p["exactStarts"] is JsonArray {Count:<=16},"lab2-scout-budget");
            if(p["reason"] is not null)DataRules.Require(DataRules.Text(p["reason"],"scout-reason").Length<=256,"lab2-scout-reason");
            if(p["nextAddress"] is not null)Address(p["nextAddress"]);
            foreach(var address in p["exactStarts"]!.AsArray())located.Add(Address(address));
        }
        var session=DataRules.Text(b["session"],"session");var sequence=DataRules.Integer(b["sequence"],"sequence");
        var snapshotDocument=DataRules.Object(DataRules.Parse(snapshot),"snapshot");
        DataRules.Require(Time(snapshotDocument["startedAtUtc"])>=begin && Time(snapshotDocument["completedAtUtc"])<=end,"lab2-native-outside-acquisition-interval");
        var capture=NativeSnapshotSource.Decode(snapshot,request,session,sequence,Path.Combine(evidence,"snapshot.json"),Path.Combine(evidence,"request.json"));
        var n=capture.Evidence;
        var requested=DataRules.Object(DataRules.Parse(request),"request")["ranges"]!.AsArray().Select(x=>DataRules.Text(x!["address"],"range-address")).ToHashSet(StringComparer.Ordinal);
        DataRules.Require(located.SetEquals(requested),"lab2-scout-snapshot-address-binding");
        DataRules.Require(!capture.Fixture && capture.Context is not null && capture.Sequence==sequence
            && DataRules.Text(n["publicationContract"],"contract")=="RREC2" && DataRules.Text(n["producer"],"producer")=="RRECollector"
            && DataRules.Text(n["producerVersion"],"version")==DataRules.Text(b["addonVersion"],"version")
            && DataRules.Integer(n["partCount"],"parts")==DataRules.Integer(b["parts"],"parts")
            && DataRules.Integer(n["payloadBytes"],"bytes")==DataRules.Integer(b["payloadBytes"],"bytes")
            && DataRules.Integer(n["expectedProcessId"],"pid")==DataRules.Integer(b["processId"],"pid")
            && DataRules.Text(n["expectedProcessStartUtcTicks"],"ticks")==DataRules.Text(b["processStartUtcTicks"],"ticks")
            && Same(DataRules.Text(n["expectedExecutableSha256"],"build"),Build)
            && Same(DataRules.Text(n["producerDeclaredBundleSha256"],"bundle"),Bundle),"lab2-publication-binding");
        var wrapped=(JsonObject)n.DeepClone();wrapped["kind"]="lab2-bounded-acquisition";
        wrapped["nativeEvidence"]=n.DeepClone();wrapped["acquisitionSha256"]=DataRules.Sha(acquisitionBytes);wrapped["acquisition"]=a.DeepClone();
        wrapped["limit"]="Active read-only Lab2 acquisition with caller-supplied coordination context. Retained API data freshness, authorship, atomicity and restart remain unqualified.";
        return new(capture.Abilities,capture.Context,wrapped,sequence,false);
    }
    private static JsonObject Binding(byte[] bytes)
    {
        var b=DataRules.Object(DataRules.Parse(bytes),"lab2-binding");
        DataRules.ExactKeys(b,"schemaVersion","evidenceKind","processId","processStartUtcTicks","executableSha256","addonVersion","session","sequence","parts","payloadBytes","imagePath","imageSha256","observedAtUtc");
        var ticks=DataRules.Text(b["processStartUtcTicks"],"ticks");var parts=DataRules.Integer(b["parts"],"parts");var length=DataRules.Integer(b["payloadBytes"],"bytes");
        DataRules.Require(DataRules.Integer(b["schemaVersion"],"schema")==1 && DataRules.Text(b["evidenceKind"],"kind")=="rre-lab2-publication-binding/1"
            && DataRules.Integer(b["processId"],"pid") is >0 and <=int.MaxValue && Regex.IsMatch(ticks,@"\A[1-9][0-9]{0,18}\z")
            && long.TryParse(ticks,NumberStyles.None,CultureInfo.InvariantCulture,out var t) && t<=DateTime.MaxValue.Ticks
            && Same(DataRules.Text(b["executableSha256"],"build"),Build)
            && DataRules.Text(b["addonVersion"],"version") is "0.4.12" or "0.4.13" or "0.4.14" or "0.4.15" or "0.4.16" or "0.4.17"
            && DataRules.Session.IsMatch(DataRules.Text(b["session"],"session")) && DataRules.Integer(b["sequence"],"sequence") is >0 and <=9_007_199_254_740_991
            && parts is >=1 and <=16 && length is >=1 and <=65536 && parts==(length+4095)/4096,"lab2-binding-contract");
        var image=DataRules.Text(b["imagePath"],"image-path");var imageSha=DataRules.Text(b["imageSha256"],"image-sha");
        DataRules.Require(!string.IsNullOrWhiteSpace(image) && image.Length<=1024 && Regex.IsMatch(imageSha,@"\A[0-9a-f]{64}\z"),"lab2-image-binding");
        Time(b["observedAtUtc"]);return b;
    }
    private static JsonObject Window(byte[] bytes)
    {
        var w=DataRules.Object(DataRules.Parse(bytes),"lab2-window");DataRules.ExactKeys(w,"schemaVersion","evidenceKind","target","startsAtUtc","endsAtUtc","owner");
        var duration=Time(w["endsAtUtc"])-Time(w["startsAtUtc"]);var owner=DataRules.Text(w["owner"],"owner");
        DataRules.Require(DataRules.Integer(w["schemaVersion"],"schema")==1 && DataRules.Text(w["evidenceKind"],"kind")=="rre-lab2-window/1"
            && DataRules.Text(w["target"],"target")=="Lab2" && duration>TimeSpan.Zero && duration<=TimeSpan.FromMinutes(15)
            && !string.IsNullOrWhiteSpace(owner) && owner.Length<=256,"lab2-window-contract");return w;
    }
    private static DateTimeOffset Time(JsonNode? node)
    {
        var text=DataRules.Text(node,"utc");DataRules.Require(Regex.IsMatch(text,@"\A\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?(?:Z|\+00:00)\z")
            && DateTimeOffset.TryParse(text,CultureInfo.InvariantCulture,DateTimeStyles.None,out _),"lab2-utc");
        return DateTimeOffset.Parse(text,CultureInfo.InvariantCulture,DateTimeStyles.None);
    }
    private static string BoundImage(JsonObject binding)
    {
        var image=Path.GetFullPath(Path.Combine(Root,DataRules.Text(binding["imagePath"],"binding-image")));
        DataRules.Require(Under(image,Path.Combine(Root,"artifacts")) && Path.GetExtension(image).Equals(".png",StringComparison.OrdinalIgnoreCase),"lab2-image-scope");
        return image;
    }
    /// <summary>Offline recovery-journal coherence only; no guest or process operation.</summary>
    public static void ValidateScope(JsonObject scope,JsonObject acquisition,string evidence)
    {
        DataRules.ExactKeys(scope,"root","knownFiles","directories","processes","controlQuarantined","cleanupComplete");
        var root=DataRules.Text(scope["root"],"scope-root");
        DataRules.Require(root==DataRules.Text(acquisition["guestRoot"],"guest-root")
            && DataRules.Boolean(scope["cleanupComplete"],"scope-cleanup") && !DataRules.Boolean(scope["controlQuarantined"],"scope-quarantine"),"lab2-control-quarantined");
        var files=DataRules.Object(scope["knownFiles"],"scope-files");
        DataRules.Require(files.Count is >0 and <=800,"lab2-scope-file-budget");
        foreach(var (path,hash) in files)
            DataRules.Require(path.StartsWith(root+"-",StringComparison.Ordinal) && path.Length<=256 && !path.Contains("..",StringComparison.Ordinal)
                && Regex.IsMatch(DataRules.Text(hash,"scope-file-sha"),@"\A[0-9A-F]{64}\z"),"lab2-scope-file");
        var directories=scope["directories"] as JsonArray ?? throw new ReaderFailure("scope-directories");
        DataRules.Require(directories.Count is >=1 and <=3,"lab2-scope-directories");
        var names=directories.Select(x=>DataRules.Text(x,"scope-directory")).ToArray();
        DataRules.Require(names.Distinct(StringComparer.OrdinalIgnoreCase).Count()==names.Length
            && names.All(x=>Regex.IsMatch(x,"\\A"+Regex.Escape(root)+"-scout-[1-3]\\z")),"lab2-scope-directory");
        var processes=DataRules.Object(scope["processes"],"scope-processes");
        DataRules.Require(processes.Count==directories.Count+1,"lab2-scope-process-count");
        var ids=new HashSet<string>();
        foreach(var (path,node) in processes)
        {
            DataRules.Require(files.ContainsKey(path) && Regex.IsMatch(path,"\\A"+Regex.Escape(root)+"-(?:scout-[1-3]|snapshot)\\.process\\.json\\z"),"lab2-process-journal-path");
            var process=DataRules.Object(node,"scope-process");DataRules.ExactKeys(process,"exitConfirmed","hostJournal","identity");
            var identity=DataRules.Object(process["identity"],"process-identity");DataRules.ExactKeys(identity,"pid","ticks","path");
            var id=DataRules.Integer(identity["pid"],"process-id");
            var ticks=DataRules.Text(identity["ticks"],"process-ticks");
            DataRules.Require(DataRules.Boolean(process["exitConfirmed"],"process-exit") && id is >0 and <=int.MaxValue && ids.Add(id+":"+ticks)
                && Regex.IsMatch(DataRules.Text(identity["ticks"],"process-ticks"),@"\A[1-9][0-9]{0,18}\z")
                && DataRules.Text(identity["path"],"process-path")==NativeHelperPath
                && Path.GetFullPath(DataRules.Text(process["hostJournal"],"host-journal")).Equals(Path.GetFullPath(Path.Combine(evidence,path[(root.Length+1)..])),StringComparison.OrdinalIgnoreCase),"lab2-process-exit-or-identity");
        }
    }
    private static string Address(JsonNode? node)
    {
        var text=DataRules.Text(node,"scout-address");
        DataRules.Require(Regex.IsMatch(text,@"\A0x[0-9A-F]{1,12}\z") && ulong.TryParse(text.AsSpan(2),NumberStyles.AllowHexSpecifier,CultureInfo.InvariantCulture,out var address)
            && address is >=0x10000 and <0x800000000000 && text=="0x"+address.ToString("X"),"lab2-scout-address");
        return text;
    }
    private static bool Same(string a,string b)=>a.Length==64 && b.Length==64 && a.Equals(b,StringComparison.OrdinalIgnoreCase);
    public static void ValidateOwnedProcessJournal(byte[] raw,string declaredSha,JsonNode? identity)
    {
        DataRules.Require(raw.Length is >0 and <=8192 && Same(DataRules.Sha(raw),declaredSha),"lab2-process-journal-raw-hash");
        // Windows PowerShell5 Set-Content UTF8 prepends one BOM. Preserve/hash
        // original bytes; normalize only this owned journal's semantic parse.
        var json=raw.AsSpan().StartsWith(new byte[]{0xEF,0xBB,0xBF}) ? raw[3..] : raw;
        JsonNode? parsed;
        try { parsed=DataRules.Parse(json); }
        catch(System.Text.Json.JsonException) { throw new ReaderFailure("lab2-owned-process-journal-json"); }
        DataRules.Require(JsonNode.DeepEquals(parsed,identity),"lab2-process-journal-identity");
    }
}
