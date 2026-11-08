using System.Globalization;
using System.Text;
using System.Text.Json.Nodes;

namespace Rre.Reader;

public sealed record ProductionPublication(JsonArray Abilities, JsonObject Context, JsonObject Counts, string PayloadSha256, int PayloadBytes, string AddonVersion);

/// <summary>Strict RREC2 decoding only. Does not acquire memory or prove source authenticity.</summary>
public static class ProductionFrameCodec
{
    public const string AddonVersion = "0.4.12";
    public const string MetadataAddonVersion = "0.4.13";
    public const string LatestAddonVersion = "0.4.14";
    private static bool SupportedVersion(string version) => version is AddonVersion or MetadataAddonVersion or LatestAddonVersion;
    private static readonly UTF8Encoding StrictUtf8 = new(false, true);
    public static JsonObject DecodeFrame(ReadOnlySpan<byte> bytes, string session, long sequence, bool allowContextTail = false)
    {
        DataRules.Require(DataRules.Session.IsMatch(session) && sequence is > 0 and <= 9_007_199_254_740_991, "expected-session-sequence");
        var prefix = Encoding.ASCII.GetBytes($"RREC2|{session}|{sequence:X16}|");
        DataRules.Require(bytes.StartsWith(prefix) && bytes.Length >= prefix.Length + 9, "production-frame-prefix");
        var digits = bytes.Slice(prefix.Length, 8);
        foreach (var b in digits) DataRules.Require(b is >= (byte)'0' and <= (byte)'9' or >= (byte)'A' and <= (byte)'F', "production-length-digits");
        DataRules.Require(int.TryParse(Encoding.ASCII.GetString(digits), NumberStyles.HexNumber, CultureInfo.InvariantCulture, out var length), "production-length");
        var begin = prefix.Length + 9;
        DataRules.Require(bytes[prefix.Length + 8] == (byte)'|' && length >= 2 && length <= 8192 - begin - 9, "production-length-limit");
        var end = begin + length;
        DataRules.Require(bytes.Length >= end + 9 && bytes.Slice(end, 9).SequenceEqual("|ENDRREC2"u8), "production-frame-suffix");
        DataRules.Require(allowContextTail || bytes.Length == end + 9, "production-trailing-data");
        foreach (var b in bytes[..(end + 9)]) DataRules.Require(b < 128, "production-frame-nonascii");
        var body = DataRules.Object(DataRules.Parse(bytes.Slice(begin, length).ToArray()), "production-frame-body");
        ValidateBody(body, session, sequence);
        return body;
    }
    private static byte[] ValidateBody(JsonObject body, string session, long sequence)
    {
        DataRules.ExactKeys(body, "schemaVersion", "producer", "addonVersion", "session", "sequence", "part", "parts", "encoding", "payloadBytes", "adler32", "data");
        DataRules.Require(DataRules.Integer(body["schemaVersion"], "production-schema") == 2
            && DataRules.Text(body["producer"], "production-producer") == "RRECollector"
            && SupportedVersion(DataRules.Text(body["addonVersion"], "production-version"))
            && DataRules.Text(body["encoding"], "production-encoding") == "base64", "production-contract");
        DataRules.Require(DataRules.Session.IsMatch(session) && sequence is > 0 and <= 9_007_199_254_740_991
            && DataRules.Text(body["session"], "production-session") == session
            && DataRules.Integer(body["sequence"], "production-sequence") == sequence, "production-session-sequence");
        var part = DataRules.Integer(body["part"], "production-part");
        var parts = DataRules.Integer(body["parts"], "production-parts");
        var payloadLength = DataRules.Integer(body["payloadBytes"], "production-payload-length");
        DataRules.Require(payloadLength is > 0 and <= 65536 && parts is > 0 and <= 16
            && parts == (payloadLength + 4095) / 4096 && part > 0 && part <= parts, "production-part-shape");
        var checksum = DataRules.Text(body["adler32"], "production-adler32");
        DataRules.Require(checksum.Length == 8 && checksum.All(c => c is >= '0' and <= '9' or >= 'a' and <= 'f'), "production-adler-format");
        var encoded = DataRules.Text(body["data"], "production-data");
        DataRules.Require(encoded.Length is > 0 and <= 5464, "production-base64-limit");
        var raw = Convert.FromBase64String(encoded);
        DataRules.Require(Convert.ToBase64String(raw) == encoded && raw.Length == (part == parts ? payloadLength - (parts - 1) * 4096 : 4096), "production-base64-or-part-length");
        return raw;
    }
    public static ProductionPublication Assemble(IReadOnlyList<JsonObject> frames)
    {
        DataRules.Require(frames.Count is > 0 and <= 16, "production-frame-count");
        var first = frames[0];
        var session = DataRules.Text(first["session"], "production-session");
        var sequence = DataRules.Integer(first["sequence"], "production-sequence");
        var payloadBytes = DataRules.Integer(first["payloadBytes"], "production-payload-length");
        var checksum = DataRules.Text(first["adler32"], "production-adler32");
        var addonVersion = DataRules.Text(first["addonVersion"], "production-version");
        var ordered = new SortedDictionary<long, byte[]>();
        foreach (var body in frames)
        {
            var raw = ValidateBody(body, session, sequence);
            DataRules.Require(DataRules.Integer(body["parts"], "production-parts") == frames.Count
                && DataRules.Integer(body["payloadBytes"], "production-payload-length") == payloadBytes
                && DataRules.Text(body["addonVersion"], "production-version") == addonVersion
                && DataRules.Text(body["adler32"], "production-adler32") == checksum, "production-mixed-publication");
            DataRules.Require(ordered.TryAdd(DataRules.Integer(body["part"], "production-part"), raw), "production-duplicate-part");
        }
        var payload = ordered.Values.SelectMany(b => b).ToArray();
        DataRules.Require(payload.Length == payloadBytes && Adler32(payload) == checksum, "production-payload-integrity");
        // JsonDocument can defer decoding string bytes; explicitly reject invalid UTF-8 first.
        try { StrictUtf8.GetString(payload); } catch (DecoderFallbackException) { throw new ReaderFailure("production-invalid-utf8"); }
        var document = DataRules.Object(DataRules.Parse(payload), "production-document");
        DataRules.ExactKeys(document, "schemaVersion", "producer", "addonVersion", "session", "sequence", "source", "counts", "context", "abilities");
        DataRules.Require(DataRules.Integer(document["schemaVersion"], "production-document-schema") == 1
            && DataRules.Text(document["producer"], "production-document-producer") == "RRECollector"
            && DataRules.Text(document["addonVersion"], "production-document-version") == addonVersion
            && DataRules.Text(document["source"], "production-document-source") == "rift-api"
            && DataRules.Text(document["session"], "production-document-session") == session
            && DataRules.Integer(document["sequence"], "production-document-sequence") == sequence, "production-document-binding");
        Structure(document, 0, new int[1]);
        var abilities = DataRules.Abilities(document["abilities"]);
        var counts = DataRules.Object(document["counts"], "production-counts");
        DataRules.ExactKeys(counts, "apiAvailable", "batchDetailAvailable", "enumerationComplete", "rawEntries", "uniqueCount", "detailCount", "detailFailures", "duplicates", "ignored", "truncated", "fallbackCalls");
        DataRules.Require(DataRules.Boolean(counts["apiAvailable"], "production-api") && DataRules.Boolean(counts["enumerationComplete"], "production-complete"), "production-list-incomplete");
        var batch = DataRules.Boolean(counts["batchDetailAvailable"], "production-batch");
        foreach (var key in new[] { "rawEntries", "uniqueCount", "detailCount", "detailFailures", "duplicates", "ignored", "truncated", "fallbackCalls" })
            DataRules.Require(DataRules.Integer(counts[key], "production-count") is >= 0 and <= 1024, "production-count-limit");
        long N(string key) => DataRules.Integer(counts[key], "production-count");
        DataRules.Require(N("uniqueCount") == abilities.Count && N("detailCount") == abilities.Count
            && N("rawEntries") == abilities.Count + N("duplicates") && N("fallbackCalls") <= abilities.Count
            && (batch || N("fallbackCalls") == abilities.Count)
            && N("detailFailures") == 0 && N("ignored") == 0 && N("truncated") == 0, "production-count-coherence");
        var context = DataRules.Object(document["context"], "production-context");
        var keys = new HashSet<string>(["player", "target", "roleSlot", "roleNames", "clientVersion", "frameTime", "realTime", "capabilities", "scope", "stats", "statsTruncated"], StringComparer.Ordinal);
        if (addonVersion == LatestAddonVersion) keys.Add("experience");
        DataRules.Require(context.All(kv => keys.Contains(kv.Key)), "production-context-field");
        var player = DataRules.Object(context["player"], "production-player");
        Nonempty(player["id"], 128); Nonempty(player["name"], 256); Nonempty(player["calling"], 128);
        DataRules.Require(Number(player["level"]) > 0 && Number(context["frameTime"]) >= 0 && Number(context["realTime"]) >= 0, "production-context-number");
        DataRules.Require(Number(context["frameTime"]) <= 9_007_199_254_740_991d / 1000000 && Number(context["realTime"]) <= 9_007_199_254_740_991d / 1000, "production-clock-limit");
        if (context["roleSlot"] is JsonValue role && role.GetValueKind() == System.Text.Json.JsonValueKind.String) Nonempty(role, 128);
        else Number(context["roleSlot"]);
        DataRules.Require(DataRules.Boolean(DataRules.Object(context["capabilities"], "production-capabilities")["player"], "production-player-capability"), "production-player-unavailable");
        ValidateContext(context, addonVersion);
        return new(abilities, (JsonObject)context.DeepClone(), (JsonObject)counts.DeepClone(), DataRules.Sha(payload), payload.Length, addonVersion);
    }
    private static void ValidateContext(JsonObject context, string addonVersion)
    {
        string[] unitFields = ["id", "name", "calling", "level", "role", "health", "healthMax", "power", "powerMax", "mana", "manaMax", "energy", "energyMax", "charge", "spirit", "combo", "combat", "coordX", "coordY", "coordZ"];
        if(addonVersion is MetadataAddonVersion or LatestAddonVersion) unitFields = [..unitFields, "race", "raceName", "zone"];
        ScalarMap(context["player"], unitFields.Length, 2048, unitFields);
        if(context.ContainsKey("target")) ScalarMap(context["target"], unitFields.Length, 2048, unitFields);
        var extended = addonVersion == LatestAddonVersion;
        var allowedCapabilities = extended
            ? new[] { "frameTime", "realTime", "clientVersion", "player", "target", "roleSlot", "roleList", "stats", "experience" }
            : new[] { "frameTime", "realTime", "clientVersion", "player", "target", "roleSlot", "roleList", "stats" };
        ScalarMap(context["capabilities"], extended ? 9 : 8, 256, allowedCapabilities, true);
        if (extended)
        {
            var capabilities = DataRules.Object(context["capabilities"], "production-capabilities");
            var available = DataRules.Boolean(capabilities["experience"], "production-experience-capability");
            DataRules.Require(available == context.ContainsKey("experience"), "production-experience-binding");
            if (available)
            {
                var experience = DataRules.Object(context["experience"], "production-experience-map");
                DataRules.Require(experience.Count <= 3, "production-experience-limit");
                foreach (var entry in experience)
                {
                    DataRules.Require(entry.Key is "accumulated" or "needed" or "rested", "production-experience-key");
                    Number(entry.Value);
                }
            }
        }
        if(context.ContainsKey("roleNames")) ScalarMap(context["roleNames"], 32, 256);
        if(context.ContainsKey("stats")) ScalarMap(context["stats"], 256, 256);
        if(context.ContainsKey("clientVersion"))
        {
            if(context["clientVersion"] is JsonObject) ScalarMap(context["clientVersion"],32,256);
            else Scalar(context["clientVersion"],256);
        }
        if(context.ContainsKey("scope")) DataRules.Require(StrictUtf8.GetByteCount(DataRules.Text(context["scope"],"production-scope"))<=4096,"production-scope-limit");
        if(context.ContainsKey("statsTruncated")) DataRules.Require(DataRules.Integer(context["statsTruncated"],"production-stats-truncated") is >=0 and <=9_007_199_254_740_991,"production-stats-truncated-limit");
    }
    private static void ScalarMap(JsonNode? node, int maximum, int stringMaximum, string[]? allowed = null, bool booleans = false)
    {
        var map=DataRules.Object(node,"production-context-map");
        DataRules.Require(map.Count<=maximum,"production-context-map-limit");
        foreach(var pair in map)
        {
            DataRules.Require(StrictUtf8.GetByteCount(pair.Key)<=128 && (allowed is null || allowed.Contains(pair.Key,StringComparer.Ordinal)),"production-context-map-key");
            if(booleans)DataRules.Boolean(pair.Value,"production-context-boolean");
            else Scalar(pair.Value,stringMaximum);
        }
    }
    private static void Scalar(JsonNode? node,int stringMaximum)
    {
        var value=node as JsonValue ?? throw new ReaderFailure("production-context-scalar");
        if(value.GetValueKind()==System.Text.Json.JsonValueKind.String)DataRules.Require(StrictUtf8.GetByteCount(value.GetValue<string>())<=stringMaximum,"production-context-scalar-limit");
        else if(value.GetValueKind()==System.Text.Json.JsonValueKind.Number)Number(value);
        else DataRules.Require(value.GetValueKind() is System.Text.Json.JsonValueKind.True or System.Text.Json.JsonValueKind.False,"production-context-scalar-kind");
    }
    private static void Nonempty(JsonNode? node, int maximum)
    {
        var text = DataRules.Text(node, "production-context-string");
        DataRules.Require(!string.IsNullOrWhiteSpace(text) && StrictUtf8.GetByteCount(text) <= maximum, "production-context-string-limit");
    }
    private static double Number(JsonNode? node)
    {
        DataRules.Require(node is JsonValue v && v.TryGetValue<double>(out var number) && double.IsFinite(number), "production-finite-number");
        return node!.GetValue<double>();
    }
    private static void Structure(JsonNode? node, int depth, int[] nodes)
    {
        DataRules.Require(++nodes[0] <= 10000 && depth <= 6 && node is not null, "production-structure-limit");
        if (node is JsonObject obj)
        {
            DataRules.Require(obj.Count <= 512, "production-object-count");
            foreach (var pair in obj) { DataRules.Require(StrictUtf8.GetByteCount(pair.Key) <= 128, "production-key-limit"); Structure(pair.Value, depth + 1, nodes); }
        }
        else if (node is JsonArray arr)
        {
            DataRules.Require(arr.Count <= 512, "production-array-count");
            foreach (var item in arr) Structure(item, depth + 1, nodes);
        }
        else if (node is JsonValue value && value.GetValueKind() == System.Text.Json.JsonValueKind.String)
            DataRules.Require(StrictUtf8.GetByteCount(value.GetValue<string>()) <= 4096, "production-string-limit");
    }
    public static string Adler32(ReadOnlySpan<byte> bytes)
    {
        uint a = 1, b = 0;
        foreach (var value in bytes) { a = (a + value) % 65521; b = (b + a) % 65521; }
        return ((b << 16) | a).ToString("x8", CultureInfo.InvariantCulture);
    }
}
