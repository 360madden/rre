using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using Rre.Reader;

namespace Rre.Reader.Checks;

public static class ProductionChecks
{
    private const string Session = "0123456789abcdef0123456789abcdef";
    private static readonly JsonSerializerOptions JsonOptions = new() { Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping };
    public static IReadOnlyList<string> Run()
    {
        var passed = new List<string>();
        void Accept(string name, Action action) { action(); passed.Add(name); }
        void Reject(string name, Action action)
        {
            try { action(); }
            catch (Exception e) when (e is ReaderFailure or JsonException or FormatException or ArgumentException) { passed.Add(name); return; }
            throw new Exception("Production invalid input accepted: " + name);
        }
        ProductionPublication Decode(JsonObject doc) => ProductionFrameCodec.Assemble(Frames(Bytes(doc),DataRules.Text(doc["addonVersion"],"fixture-version")).Select(b => ProductionFrameCodec.DecodeFrame(Wire(b), Session, 2)).ToList());
        void BadDoc(string name, Action<JsonObject> mutate) { Reject(name, () => { var d = Document(); mutate(d); Decode(d); }); }
        void BadBody(string name, Action<JsonObject> mutate) { Reject(name, () => { var b = Frames(Bytes(Document()))[0]; mutate(b); ProductionFrameCodec.DecodeFrame(Wire(b), Session, 2); }); }
        Accept("LEGION rejects Lab2 before acquisition", () =>
        {
            foreach (var host in new[] { "LEGION", "legion", "Legion" })
            {
                try { Program.RequireSourceHost("lab2", host); }
                catch (ReaderFailure e) when (e.Message == "legion-physical-only") { continue; }
                throw new Exception("LEGION Lab2 source was not rejected: " + host);
            }
        });
        Accept("LEGION offline sources stay available", () =>
        {
            foreach (var source in new[] { "saved", "memory-scan", "native-snapshot", "publication" })
                Program.RequireSourceHost(source, "LEGION");
        });
        Accept("other host retains explicitly scoped Lab2 route", () => Program.RequireSourceHost("lab2", "AMD-DESKTOP"));
        Accept("doctor tolerates absent Node executable", () =>
        {
            var repo = Environment.CurrentDirectory;
            var absent = Path.Combine(repo, "rre-missing-node-" + Guid.NewGuid().ToString("N") + ".exe");
            var probe = Program.ProbeNodeAsync(repo, absent).GetAwaiter().GetResult();
            if (probe.Available || probe.Version is not null)
                throw new Exception("missing Node executable reported available");
        });
        Accept("production Unicode false zero and target survive", () =>
        {
            var p = Decode(Document()); var r = p.Abilities[0]!;
            if(r["name"]!.GetValue<string>()!="Éclair 水 😀" || r["passive"]!.GetValue<bool>() || r["cooldown"]!.GetValue<int>()!=0 || r["target"]!.GetValue<string>()!="uTARGET") throw new Exception("production scalars");
        });
        Accept("production multipart reordered assembly", () =>
        {
            var d = Document(); d["abilities"]![0]!["description"] = new string('é', 2048);
            var frames = Frames(Bytes(d)); if(frames.Count<2)throw new Exception("fixture not multipart");
            var p=ProductionFrameCodec.Assemble(frames.AsEnumerable().Reverse().ToList());
            if(p.Abilities[0]!["description"]!.GetValue<string>().Length!=2048)throw new Exception("multipart");
        });
        Accept("production scalar fallback accepted", () => { var d=Document();d["counts"]!["batchDetailAvailable"]=false;d["counts"]!["fallbackCalls"]=1;Decode(d); });
        Accept("production duplicate-list accounting accepted", () => { var d=Document();d["counts"]!["rawEntries"]=2;d["counts"]!["duplicates"]=1;Decode(d); });
        Accept("Adler32 independent RFC vector", () => { if(ProductionFrameCodec.Adler32("Wikipedia"u8)!="11e60398")throw new Exception("Adler32"); });
        Accept("production0413 optional unit metadata preserved",()=>
        {
            var d=Document("0.4.13");var p=d["context"]!["player"]!;p["race"]="mathosian";p["raceName"]="Mathosian";p["zone"]="zOPAQUE";
            var result=Decode(d);if(result.AddonVersion!="0.4.13" || result.Context["player"]!["zone"]!.GetValue<string>()!="zOPAQUE")throw new Exception("metadata loss");
        });
        Accept("production0413 absent metadata remains unknown",()=>{var p=Decode(Document("0.4.13"));if(p.Context["player"]!.AsObject().ContainsKey("race"))throw new Exception("invented metadata");});
        Accept("production0413 raw metadata scalar types retained",()=>{var d=Document("0.4.13");d["context"]!["player"]!["race"]=false;d["context"]!["player"]!["raceName"]=0;var p=Decode(d);if(p.Context["player"]!["race"]!.GetValue<bool>() || p.Context["player"]!["raceName"]!.GetValue<int>()!=0)throw new Exception("scalar loss");});
        BadDoc("production0412 does not silently gain new fields",d=>d["context"]!["player"]!["race"]="mathosian");
        Accept("production0413 target metadata retained",()=>{var d=Document("0.4.13");d["context"]!["target"]=new JsonObject{["race"]="mathosian",["raceName"]="Mathosian",["zone"]="zTARGET"};if(Decode(d).Context["target"]!["zone"]!.GetValue<string>()!="zTARGET")throw new Exception("target metadata loss");});
        BadDoc("production0412 target metadata rejected",d=>d["context"]!["target"]=new JsonObject{["race"]="mathosian"});
        Reject("production document and frame versions must agree",()=>{var b=Frames(Bytes(Document("0.4.13")),"0.4.12");ProductionFrameCodec.Assemble(b);});
        Reject("production mixed supported frame versions rejected",()=>{var d=Document();d["abilities"]![0]!["description"]=new string('x',4096);var b=Frames(Bytes(d));b[1]["addonVersion"]="0.4.13";ProductionFrameCodec.Assemble(b);});
        Reject("production0413 undocumented decoration rejected",()=>{var d=Document("0.4.13");d["context"]!["player"]!["decoration"]=1704;Decode(d);});
        Accept("production0413 native carrier reports actual producer version",()=>{var b=Frames(Bytes(Document("0.4.13")),"0.4.13")[0];var(r,s)=NativeChecks.Fixture(Wire(b));var c=NativeSnapshotSource.Decode(Bytes(s),Bytes(r),Session,2);if(c.Evidence["producerVersion"]!.GetValue<string>()!="0.4.13")throw new Exception("wrong version");});
        Accept("production0416 current-load Rogue and Experience contract preserved", () =>
        {
            var d=Document("0.4.16");
            d["context"]!["capabilities"]!["experience"]=true;
            d["context"]!["experience"]=new JsonObject{["accumulated"]=0,["needed"]=144};
            d["context"]!["player"]!["zone"]="zROGUE";
            var p=Decode(d);
            if(p.AddonVersion!="0.4.16" || p.Abilities.Count!=1
                || p.Context["player"]!["calling"]!.GetValue<string>()!="rogue"
                || p.Context["experience"]!["needed"]!.GetValue<int>()!=144)
                throw new Exception("v16 ability/Experience regression");
        });
        BadDoc("production0416 rejects missing Experience capability",
            d=>d["addonVersion"]="0.4.16");
        Accept("production0415 Rogue calling and Experience contract preserved", () =>
        {
            var d=Document("0.4.15");
            d["context"]!["capabilities"]!["experience"]=true;
            d["context"]!["experience"]=new JsonObject{["needed"]=0};
            d["context"]!["player"]!["zone"]="zROGUE";
            var frames=Frames(Bytes(d),"0.4.15");
            var publication=ProductionFrameCodec.Assemble(frames.Select(p=>ProductionFrameCodec.DecodeFrame(Wire(p),Session,2)).ToList());
            if(publication.AddonVersion!="0.4.15" || publication.Abilities.Count!=1
                || publication.Context["player"]!["calling"]!.GetValue<string>()!="rogue"
                || publication.Context["player"]!["zone"]!.GetValue<string>()!="zROGUE"
                || publication.Context["experience"]!["needed"]!.GetValue<int>()!=0)
                throw new Exception("v15 calling/Experience regression");
        });
        BadDoc("production0415 missing Experience capability rejected",d=>d["addonVersion"]="0.4.15");
        Accept("production0414 Experience zero partial and metadata survive",()=>
        {
            var d=Document("0.4.14"); d["context"]!["capabilities"]!["experience"]=true;
            d["context"]!["experience"]=new JsonObject{["accumulated"]=0,["needed"]=1234};
            d["context"]!["player"]!["zone"]="zOPAQUE";
            var p=Decode(d);
            if(p.AddonVersion!="0.4.14" || p.Context["experience"]!["accumulated"]!.GetValue<int>()!=0
                || p.Context["experience"]!["needed"]!.GetValue<int>()!=1234
                || p.Context["experience"]!.AsObject().ContainsKey("rested")
                || p.Context["player"]!["zone"]!.GetValue<string>()!="zOPAQUE")throw new Exception("v14 data loss");
        });
        Accept("production0414 empty Experience object allowed",()=>{
            var d=Document("0.4.14");d["context"]!["capabilities"]!["experience"]=true;d["context"]!["experience"]=new JsonObject();
            if(Decode(d).Context["experience"] is not JsonObject {Count:0})throw new Exception("empty map lost");
        });
        Accept("production0414 unavailable Experience explicitly false",()=>{
            var d=Document("0.4.14");d["context"]!["capabilities"]!["experience"]=false;
            if(Decode(d).Context.ContainsKey("experience"))throw new Exception("invented experience");
        });
        BadDoc("production0414 missing capability rejected",d=>d["addonVersion"]="0.4.14");
        BadDoc("production0414 true missing map rejected",d=>{d["addonVersion"]="0.4.14";d["context"]!["capabilities"]!["experience"]=true;});
        BadDoc("production0414 false with map rejected",d=>{d["addonVersion"]="0.4.14";d["context"]!["capabilities"]!["experience"]=false;d["context"]!["experience"]=new JsonObject();});
        BadDoc("production0414 unknown Experience field rejected",d=>{d["addonVersion"]="0.4.14";d["context"]!["capabilities"]!["experience"]=true;d["context"]!["experience"]=new JsonObject{["unknown"]=1};});
        BadDoc("production0414 string Experience value rejected",d=>{d["addonVersion"]="0.4.14";d["context"]!["capabilities"]!["experience"]=true;d["context"]!["experience"]=new JsonObject{["needed"]="5"};});
        BadDoc("production0414 array Experience rejected",d=>{d["addonVersion"]="0.4.14";d["context"]!["capabilities"]!["experience"]=true;d["context"]!["experience"]=new JsonArray();});
        BadDoc("production0414 four-key Experience rejected",d=>{d["addonVersion"]="0.4.14";d["context"]!["capabilities"]!["experience"]=true;d["context"]!["experience"]=new JsonObject{["accumulated"]=0,["needed"]=1,["rested"]=2,["extra"]=3};});
        BadDoc("production0413 Experience flag forbidden",d=>d["context"]!["capabilities"]!["experience"]=false);
        BadDoc("production0413 Experience map forbidden",d=>d["context"]!["experience"]=new JsonObject{["needed"]=0});
        Accept("production0414 coherent reordered two-part generation survives", () =>
        {
            var d=Document("0.4.14");
            d["context"]!["capabilities"]!["experience"]=true;
            d["context"]!["experience"]=new JsonObject{["needed"]=0};
            d["abilities"]![0]!["description"]=new string('x',4096);
            var parts=Frames(Bytes(d),"0.4.14");
            if(parts.Count!=2)throw new Exception("expected two-part v0.4.14 control");
            var decoded=parts.Select(p=>ProductionFrameCodec.DecodeFrame(Wire(p),Session,2)).Reverse().ToList();
            var publication=ProductionFrameCodec.Assemble(decoded);
            if(publication.AddonVersion!="0.4.14" || publication.Context["experience"]!["needed"]!.GetValue<int>()!=0)
                throw new Exception("coherent v0.4.14 reordered payload rejected or changed");
        });
        Accept("production0414 shared-header mixed generations reject checksum mismatch", () =>
        {
            var d=Document("0.4.14");
            d["context"]!["capabilities"]!["experience"]=false;
            d["abilities"]![0]!["description"]=new string('x',4096);
            var other=(JsonObject)d.DeepClone();
            other["abilities"]![0]!["description"]=new string('y',4096);
            var first=Frames(Bytes(d),"0.4.14");
            var second=Frames(Bytes(other),"0.4.14");
            if(first.Count!=2 || second.Count!=2 || first[0]["adler32"]!.GetValue<string>()==second[0]["adler32"]!.GetValue<string>())
                throw new Exception("distinct equal-length two-part fixture required");
            var mixed=new List<JsonObject>{
                ProductionFrameCodec.DecodeFrame(Wire(first[0]),Session,2),
                ProductionFrameCodec.DecodeFrame(Wire(second[1]),Session,2)};
            try {ProductionFrameCodec.Assemble(mixed);}
            catch(ReaderFailure e) when(e.Message=="production-mixed-publication") {return;}
            throw new Exception("different publications accepted under shared session/sequence");
        });
        Accept("production native snapshot carrier preserves contract context", () =>
        {
            var body=Frames(Bytes(Document()))[0];var (request,snapshot)=NativeChecks.Fixture(Wire(body));
            var capture=NativeSnapshotSource.Decode(Bytes(snapshot),Bytes(request),Session,2);
            if(capture.Fixture || capture.Context is null || capture.Abilities.Count!=1 || capture.Evidence["publicationContract"]!.GetValue<string>()!="RREC2")throw new Exception("native production carrier");
        });
        BadDoc("production duplicate counts incoherent", d=>d["counts"]!["duplicates"]=500);
        BadDoc("production excess fallback rejected", d=>d["counts"]!["fallbackCalls"]=2);
        BadDoc("production scalar fallback count required", d=>d["counts"]!["batchDetailAvailable"]=false);
        BadDoc("production missing count rejected", d=>d["counts"]!.AsObject().Remove("ignored"));
        BadDoc("production fractional count rejected", d=>d["counts"]!["rawEntries"]=1.5);
        BadDoc("production incomplete list rejected", d=>d["counts"]!["enumerationComplete"]=false);
        BadDoc("production count record mismatch rejected", d=>d["counts"]!["uniqueCount"]=2);
        BadDoc("production missing player rejected", d=>d["context"]!.AsObject().Remove("player"));
        BadDoc("production empty player name rejected", d=>d["context"]!["player"]!["name"]=" ");
        BadDoc("production missing player capability rejected", d=>d["context"]!["capabilities"]!["player"]=false);
        BadDoc("production negative clock rejected", d=>d["context"]!["realTime"]=-1);
        BadDoc("production clock multiplication overflow rejected", d=>d["context"]!["frameTime"]=9007199255d);
        BadDoc("production boolean role rejected", d=>d["context"]!["roleSlot"]=false);
        BadDoc("production unknown context field rejected", d=>d["context"]!["command"]="never");
        BadDoc("production wrong document version rejected", d=>d["addonVersion"]="0.4.11");
        BadDoc("production wrong document sequence rejected", d=>d["sequence"]=1);
        BadDoc("production unknown document field rejected", d=>d["unknown"]=true);
        BadDoc("production null context scalar rejected", d=>d["context"]!["scope"]=null);
        BadDoc("production stats array rejected", d=>d["context"]!["stats"]=new JsonArray());
        BadDoc("production role nested object rejected", d=>d["context"]!["roleNames"]=new JsonObject{["1"]=new JsonObject()});
        BadDoc("production player unknown field rejected", d=>d["context"]!["player"]!["extra"]=false);
        BadDoc("production capability nested object rejected", d=>d["context"]!["capabilities"]!["stats"]=new JsonObject());
        BadDoc("production capability unknown field rejected", d=>d["context"]!["capabilities"]!["extra"]=true);
        BadDoc("production stats dropped count is not boolean", d=>d["context"]!["statsTruncated"]=false);
        BadDoc("production stats dropped count nonnegative", d=>d["context"]!["statsTruncated"]=-1);
        Accept("production stats dropped count retained", ()=>{var d=Document();d["context"]!["statsTruncated"]=2;var p=Decode(d);if(p.Context["statsTruncated"]!.GetValue<int>()!=2)throw new Exception("stats count");});
        BadDoc("production scope must be string", d=>d["context"]!["scope"]=false);
        BadDoc("production client version nested rejected", d=>d["context"]!["clientVersion"]=new JsonObject{["nested"]=new JsonObject()});
        BadDoc("production scalar map string byte limit rejected", d=>d["context"]!["stats"]=new JsonObject{["fixture"]=new string('é',129)});
        BadDoc("production string UTF8 byte limit rejected", d=>d["abilities"]![0]!["description"]=new string('é',2049));
        BadDoc("production nested scalar rejected", d=>d["abilities"]![0]!["name"]=new JsonObject());
        BadDoc("production duplicate ID rejected", d=>d["abilities"]!.AsArray().Add(d["abilities"]![0]!.DeepClone()));
        BadBody("production unknown frame field rejected", b=>b["command"]="never");
        BadBody("production frame version rejected", b=>b["addonVersion"]="0.4.11");
        BadBody("production frame session rejected", b=>b["session"]=new string('f',32));
        BadBody("production frame stale sequence rejected", b=>b["sequence"]=1);
        BadBody("production part zero rejected", b=>b["part"]=0);
        BadBody("production count shape rejected", b=>b["parts"]=16);
        BadBody("production payload budget rejected", b=>b["payloadBytes"]=65537);
        BadBody("production checksum uppercase rejected", b=>b["adler32"]="ABCDEF01");
        BadBody("production noncanonical base64 rejected", b=>b["data"]=" "+b["data"]!.GetValue<string>());
        Reject("production header session exact", ()=>ProductionFrameCodec.DecodeFrame(Wire(Frames(Bytes(Document()))[0]),new string('f',32),2));
        Reject("production header sequence exact", ()=>ProductionFrameCodec.DecodeFrame(Wire(Frames(Bytes(Document()))[0]),Session,1));
        Reject("production suffix truncation rejected", ()=>ProductionFrameCodec.DecodeFrame(Wire(Frames(Bytes(Document()))[0])[..^1],Session,2));
        Reject("production trailing byte rejected", ()=>ProductionFrameCodec.DecodeFrame(Wire(Frames(Bytes(Document()))[0]).Concat(new byte[]{0}).ToArray(),Session,2));
        Accept("production bounded context tail explicit", ()=>ProductionFrameCodec.DecodeFrame(Wire(Frames(Bytes(Document()))[0]).Concat(new byte[]{0}).ToArray(),Session,2,true));
        Reject("production checksum mismatch rejected", ()=> { var b=Frames(Bytes(Document()));b[0]["adler32"]="00000000";ProductionFrameCodec.Assemble(b); });
        Reject("production missing part rejected", ()=> {var d=Document();d["abilities"]![0]!["description"]=new string('x',4096);var b=Frames(Bytes(d));ProductionFrameCodec.Assemble([b[0]]);});
        Reject("production duplicate part rejected", ()=> {var d=Document();d["abilities"]![0]!["description"]=new string('x',4096);var b=Frames(Bytes(d));ProductionFrameCodec.Assemble([b[0],(JsonObject)b[0].DeepClone()]);});
        Reject("production invalid UTF8 rejected before JSON", ()=> {var raw=Bytes(Document());var where=Array.IndexOf(raw,(byte)0xC3);raw[where]=0xFF;ProductionFrameCodec.Assemble(Frames(raw));});
        Reject("production duplicate JSON property rejected", ()=> {var text=Encoding.UTF8.GetString(Bytes(Document()));ProductionFrameCodec.Assemble(Frames(Encoding.UTF8.GetBytes(text[..^1]+",\"source\":\"rift-api\"}")));});
        return passed;
    }
    private static byte[] Bytes(JsonObject d)=>Encoding.UTF8.GetBytes(d.ToJsonString(JsonOptions));
    private static List<JsonObject> Frames(byte[] payload,string addonVersion="0.4.12")
    {
        var result=new List<JsonObject>();var parts=(payload.Length+4095)/4096;
        for(var part=1;part<=parts;part++)result.Add(new JsonObject
        {
            ["schemaVersion"]=2,["producer"]="RRECollector",["addonVersion"]=addonVersion,["session"]=Session,["sequence"]=2,
            ["part"]=part,["parts"]=parts,["encoding"]="base64",["payloadBytes"]=payload.Length,
            ["adler32"]=ProductionFrameCodec.Adler32(payload),["data"]=Convert.ToBase64String(payload.AsSpan((part-1)*4096,Math.Min(4096,payload.Length-(part-1)*4096)))
        });
        return result;
    }
    private static byte[] Wire(JsonObject body)
    {
        var b=Encoding.ASCII.GetBytes(body.ToJsonString());
        return Encoding.ASCII.GetBytes($"RREC2|{Session}|{2:X16}|{b.Length:X8}|").Concat(b).Concat("|ENDRREC2"u8.ToArray()).ToArray();
    }
    private static JsonObject Document(string addonVersion="0.4.12")=>new()
    {
        ["schemaVersion"]=1,["producer"]="RRECollector",["addonVersion"]=addonVersion,["session"]=Session,["sequence"]=2,["source"]="rift-api",
        ["counts"]=new JsonObject{["apiAvailable"]=true,["batchDetailAvailable"]=true,["enumerationComplete"]=true,["rawEntries"]=1,["uniqueCount"]=1,["detailCount"]=1,["detailFailures"]=0,["duplicates"]=0,["ignored"]=0,["truncated"]=0,["fallbackCalls"]=0},
        ["context"]=new JsonObject{["player"]=new JsonObject{["id"]="uFIXTURE",["name"]="Fixture",["calling"]="rogue",["level"]=43},["roleSlot"]=1,["frameTime"]=1.5,["realTime"]=2.5,["capabilities"]=new JsonObject{["player"]=true}},
        ["abilities"]=new JsonArray(new JsonObject{["lookupId"]="A0000000100000000",["name"]="Éclair 水 😀",["passive"]=false,["cooldown"]=0,["target"]="uTARGET"})
    };
}
