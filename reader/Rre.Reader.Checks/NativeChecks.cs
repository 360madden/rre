using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using Rre.Reader;

namespace Rre.Reader.Checks;

public static class NativeChecks
{
    private const string Session = "0123456789abcdef0123456789abcdef";
    private const string Bundle = "F4148B838AF694EF95FD46DE76859CE9DF55194A9FE8BE1DF74FC2F8F0BCE80F";
    public static IReadOnlyList<string> Run()
    {
        var passed = new List<string>();
        void Accept(string name, Action action) { action(); passed.Add(name); }
        void Reject(string name, Action<JsonObject, JsonObject> mutate, bool rehashRequest = false)
        {
            var (request, snapshot) = Fixture(); mutate(request, snapshot);
            var rawRequest = Bytes(request);
            if (rehashRequest) snapshot["source"]!["requestSha256"] = DataRules.Sha(rawRequest);
            try { NativeSnapshotSource.Decode(Bytes(snapshot), rawRequest, Session, 2); }
            catch (Exception error) when (error is ReaderFailure or JsonException or FormatException) { passed.Add(name); return; }
            throw new Exception("Native invalid input accepted: " + name);
        }
        Accept("native snapshot joins both4KiB chunks", () =>
        {
            var (request, snapshot) = Fixture(); var c = NativeSnapshotSource.Decode(Bytes(snapshot),Bytes(request),Session,2);
            if(c.Abilities.Count!=1 || c.Abilities[0]!["description"]!.GetValue<string>().Length!=4096 || !c.Fixture)throw new Exception("native join");
            var q=ObservationModules.Build(c,"abilities")["qualification"]!;
            if(q["live"]!.GetValue<bool>() || q["processBuildVerified"]!.GetValue<bool>())throw new Exception("native qualification upgraded");
        });
        Reject("native request raw-byte SHA mismatch", (r,s)=>r["maxDurationMilliseconds"]=4999);
        Reject("native exact tick mismatch is not rounded", (r,s)=>s["identity"]!["processStartUtcTicks"]=639296711399704026L);
        Reject("native process mismatch", (r,s)=>s["identity"]!["processId"]=124);
        Reject("native unknown report field", (r,s)=>s["unexpected"]=true);
        Reject("native omitted null reason rejected", (r,s)=>s.Remove("reason"));
        Reject("native missing chunk error field rejected", (r,s)=>s["chunks"]![0]!.AsObject().Remove("win32ErrorCode"));
        Reject("native malformed module identity rejected", (r,s)=>s["identity"]!["moduleSize"]=new JsonObject());
        Reject("native malformed tool version rejected", (r,s)=>s["source"]!["implementation"]!["toolVersion"]=new JsonArray());
        Reject("native malformed limitations rejected", (r,s)=>s["limitations"]=123);
        Reject("native partial report rejected", (r,s)=>s["status"]="partial");
        Reject("native partial chunk rejected", (r,s)=>s["chunks"]![0]!["status"]="partial");
        Reject("native missing chunk rejected", (r,s)=>s["chunks"]!.AsArray().RemoveAt(1));
        Reject("native duplicate chunk rejected", (r,s)=>s["chunks"]!.AsArray().Add(s["chunks"]![0]!.DeepClone()));
        Reject("native unexpected chunk rejected", (r,s)=>{var c=s["chunks"]![0]!.DeepClone();c["address"]="0x20000";s["chunks"]!.AsArray().Add(c);});
        Reject("native overlapping requested ranges rejected", (r,s)=>r["ranges"]!.AsArray().Add(r["ranges"]![0]!.DeepClone()),true);
        Reject("native unknown range kind rejected", (r,s)=>r["ranges"]![0]!["addressKind"]="module-relative-rva",true);
        Reject("native oversized requested range rejected", (r,s)=>r["ranges"]![0]!["byteLength"]=8193,true);
        Reject("native misaligned partition rejected", (r,s)=>s["chunks"]![1]!["address"]="0x11001");
        Reject("native chunk hash mismatch rejected", (r,s)=>s["chunks"]![0]!["bytesSha256"]=new string('0',64));
        Reject("native chunk length mismatch rejected", (r,s)=>s["chunks"]![0]!["bytesRead"]=4095);
        Reject("native base64 must be canonical", (r,s)=>
        {
            r["ranges"]![0]!["byteLength"]=8191;
            var c=s["chunks"]![1]!;var raw=Convert.FromBase64String(c["bytesBase64"]!.GetValue<string>())[..4095];
            c["requestedByteLength"]=4095;c["bytesRead"]=4095;c["bytesSha256"]=DataRules.Sha(raw);
            c["bytesBase64"]=Convert.ToBase64String(raw)+"\n";
        },true);
        Reject("native unqualified reader rejected", (r,s)=>s["source"]!["implementation"]!["bundleSha256"]=new string('0',64));
        Reject("native backwards source clock rejected", (r,s)=>s["completedAtUtc"]="2026-11-06T00:00:00Z");
        Reject("native capture before process creation rejected", (r,s)=>{s["startedAtUtc"]="2026-11-06T00:00:00Z";s["completedAtUtc"]="2026-11-06T00:00:00.001Z";});
        return passed;
    }
    private static byte[] Bytes(JsonNode node)=>Encoding.UTF8.GetBytes(node.ToJsonString());
    internal static (JsonObject Request,JsonObject Snapshot) Fixture(byte[]? productionWire = null)
    {
        var body=new JsonObject { ["schemaVersion"]=1,["producer"]="RRE-feasibility-fixture",["session"]=Session,["sequence"]=2,["part"]=1,["parts"]=1,
            ["records"]=new JsonArray(new JsonObject{["lookupId"]="A0000000100000000",["name"]="Fixture",["description"]=new string('x',4096),["passive"]=false,["cooldown"]=0})};
        var payload=Bytes(body);var wire=Encoding.ASCII.GetBytes($"RREC1|{Session}|{payload.Length:X8}|").Concat(payload).Concat("|ENDRREC1"u8.ToArray()).ToArray();
        var memory=new byte[8192];(productionWire ?? wire).CopyTo(memory,0);
        var target=new JsonObject{["processId"]=123,["processStartUtcTicks"]=639296711399704025L,["executableSha256"]=new string('A',64)};
        var request=new JsonObject{["schemaVersion"]=1,["evidenceKind"]="native-memory-snapshot-request/1",["target"]=target.DeepClone(),["maxDurationMilliseconds"]=5000,
            ["ranges"]=new JsonArray(new JsonObject{["addressKind"]="absolute-session-address",["address"]="0x10000",["byteLength"]=8192})};
        var chunks=new JsonArray();
        for(var i=0;i<2;i++){var raw=memory.AsSpan(i*4096,4096).ToArray();chunks.Add(new JsonObject{["address"]=$"0x{65536+i*4096:X}",["requestedByteLength"]=4096,["status"]="success",["bytesRead"]=4096,["bytesBase64"]=Convert.ToBase64String(raw),["bytesSha256"]=DataRules.Sha(raw),["win32ErrorCode"]=null,["reason"]=null});}
        var identity=(JsonObject)target.DeepClone();identity["executablePath"]="C:\\fixture.exe";identity["moduleBaseAddress"]=0x140000000L;identity["moduleSize"]=4096;
        var snapshot=new JsonObject{["schemaVersion"]=1,["evidenceKind"]="native-memory-snapshot/1",["source"]=new JsonObject{["requestEvidenceKind"]="native-memory-snapshot-request/1",["requestSha256"]=DataRules.Sha(Bytes(request)),["requestSha256Verification"]="producer-declared",
            ["implementation"]=new JsonObject{["toolVersion"]="0.1.0.0",["deploymentKind"]="single-file-bundle",["assemblySha256"]=null,["bundleFileName"]="RiftReader2.Live.exe",["bundleSha256"]=Bundle}},
            ["identity"]=identity,["startedAtUtc"]="2026-11-07T18:00:00Z",["completedAtUtc"]="2026-11-07T18:00:00.001Z",["status"]="complete",["reason"]=null,["chunks"]=chunks,["limitations"]=new JsonArray()};
        return(request,snapshot);
    }
}
