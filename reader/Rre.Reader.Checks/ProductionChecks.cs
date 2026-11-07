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
        ProductionPublication Decode(JsonObject doc) => ProductionFrameCodec.Assemble(Frames(Bytes(doc)).Select(b => ProductionFrameCodec.DecodeFrame(Wire(b), Session, 2)).ToList());
        void BadDoc(string name, Action<JsonObject> mutate) { Reject(name, () => { var d = Document(); mutate(d); Decode(d); }); }
        void BadBody(string name, Action<JsonObject> mutate) { Reject(name, () => { var b = Frames(Bytes(Document()))[0]; mutate(b); ProductionFrameCodec.DecodeFrame(Wire(b), Session, 2); }); }
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
    private static List<JsonObject> Frames(byte[] payload)
    {
        var result=new List<JsonObject>();var parts=(payload.Length+4095)/4096;
        for(var part=1;part<=parts;part++)result.Add(new JsonObject
        {
            ["schemaVersion"]=2,["producer"]="RRECollector",["addonVersion"]="0.4.12",["session"]=Session,["sequence"]=2,
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
    private static JsonObject Document()=>new()
    {
        ["schemaVersion"]=1,["producer"]="RRECollector",["addonVersion"]="0.4.12",["session"]=Session,["sequence"]=2,["source"]="rift-api",
        ["counts"]=new JsonObject{["apiAvailable"]=true,["batchDetailAvailable"]=true,["enumerationComplete"]=true,["rawEntries"]=1,["uniqueCount"]=1,["detailCount"]=1,["detailFailures"]=0,["duplicates"]=0,["ignored"]=0,["truncated"]=0,["fallbackCalls"]=0},
        ["context"]=new JsonObject{["player"]=new JsonObject{["id"]="uFIXTURE",["name"]="Fixture",["calling"]="rogue",["level"]=43},["roleSlot"]=1,["frameTime"]=1.5,["realTime"]=2.5,["capabilities"]=new JsonObject{["player"]=true}},
        ["abilities"]=new JsonArray(new JsonObject{["lookupId"]="A0000000100000000",["name"]="Éclair 水 😀",["passive"]=false,["cooldown"]=0,["target"]="uTARGET"})
    };
}
