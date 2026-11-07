using System.Globalization;
using System.Text;
using System.Text.Json.Nodes;

namespace Rre.Reader;

/// <summary>Offline replay of original Reader scan JSON. No process access or acquisition.</summary>
public sealed class MemoryScanSource(string input, string session, long sequence) : IObservationSource
{
    public async Task<SourceCapture> ReadAsync(CancellationToken cancellationToken = default)
    {
        DataRules.Require(DataRules.Session.IsMatch(session) && sequence is > 0 and <= 9_007_199_254_740_991, "expected-session-sequence");
        var bytes = await DataRules.ReadFileAsync(input, 8 * 1024 * 1024, cancellationToken);
        var root = DataRules.Object(DataRules.Parse(bytes), "scan-object");
        DataRules.Require(DataRules.Text(root["Encoding"], "scan-encoding") == "ascii", "scan-encoding");
        var hits = root["Hits"] as JsonArray ?? throw new ReaderFailure("scan-hits");
        DataRules.Require(hits.Count is > 0 and <= 16 && DataRules.Integer(root["HitCount"], "scan-hit-count") == hits.Count, "scan-hit-count");
        var maxHits = DataRules.Integer(root["MaxHits"], "scan-max-hits");
        DataRules.Require(maxHits is > 0 and <= 128 && hits.Count < maxHits, "scan-hit-budget-ambiguous");
        DataRules.Require(DataRules.Text(root["SearchText"], "scan-search") == "RREC1|" + session + "|", "scan-search-binding");
        var frames = new List<JsonObject>();
        foreach (var hit in hits)
        {
            var h = DataRules.Object(hit, "scan-hit-object");
            DataRules.Require(DataRules.Text(h["Encoding"], "hit-encoding") == "ascii", "hit-encoding");
            var context = DataRules.Object(h["Context"], "scan-context-missing");
            var hex = DataRules.Text(context["BytesHex"], "context-hex");
            DataRules.Require(hex.Length is > 0 and <= 98304, "context-byte-limit");
            DataRules.Require(hex.Length % 3 == 2, "context-hex-format");
            for (var i = 0; i < hex.Length; i++)
                DataRules.Require(i % 3 == 2 ? hex[i] == ' ' : hex[i] is >= '0' and <= '9' or >= 'A' and <= 'F', "context-hex-format");
            var compactHex = hex.Replace(" ", "", StringComparison.Ordinal);
            DataRules.Require(compactHex.Length is > 0 and <= 65536 && compactHex.Length % 2 == 0, "context-byte-limit");
            byte[] raw;
            try { raw = Convert.FromHexString(compactHex); }
            catch (FormatException) { throw new ReaderFailure("context-hex-format"); }
            DataRules.Require(DataRules.Integer(context["WindowLength"], "context-length") == raw.Length, "context-length-mismatch");
            var address = DataRules.Integer(h["Address"], "hit-address");
            var windowText = DataRules.Text(context["WindowStart"], "window-address");
            DataRules.Require(windowText.StartsWith("0x", StringComparison.OrdinalIgnoreCase)
                && long.TryParse(windowText.AsSpan(2), NumberStyles.AllowHexSpecifier, CultureInfo.InvariantCulture, out _), "window-address");
            var window = long.Parse(windowText.AsSpan(2), NumberStyles.AllowHexSpecifier, CultureInfo.InvariantCulture);
            DataRules.Require(window >= 0 && address > 0 && address >= window && address - window <= raw.Length, "hit-outside-window");
            var start = checked((int)(address - window));
            frames.Add(DecodeFrame(raw.AsSpan(start), session, sequence, allowContextTail: true));
        }
        var abilities = Assemble(frames);
        return new(abilities, null, new JsonObject
        {
            ["kind"] = "memory-scan-replay", ["path"] = Path.GetFullPath(input), ["sha256"] = DataRules.Sha(bytes),
            ["bytes"] = bytes.Length, ["producer"] = "RRE-feasibility-fixture", ["partCount"] = frames.Count,
            ["expectedSession"] = session, ["locatorIdentityVerified"] = false,
            ["limit"] = "Controlled fixture format only; no live RRE producer or target identity accepted."
        }, sequence, true);
    }
    public static JsonObject DecodeFrame(ReadOnlySpan<byte> bytes, string session, long sequence, bool allowContextTail = false)
    {
        DataRules.Require(DataRules.Session.IsMatch(session) && sequence is > 0 and <= 9_007_199_254_740_991, "expected-session-sequence");
        var prefix = Encoding.ASCII.GetBytes("RREC1|" + session + "|");
        var suffix = "|ENDRREC1"u8;
        DataRules.Require(bytes.StartsWith(prefix) && bytes.Length >= prefix.Length + 9, "frame-prefix");
        var lengthBytes = bytes.Slice(prefix.Length, 8);
        foreach (var b in lengthBytes) DataRules.Require(b is >= (byte)'0' and <= (byte)'9' or >= (byte)'A' and <= (byte)'F', "frame-length-digits");
        DataRules.Require(int.TryParse(Encoding.ASCII.GetString(lengthBytes), NumberStyles.HexNumber, CultureInfo.InvariantCulture, out var payloadLength), "frame-length");
        var begin = prefix.Length + 9;
        DataRules.Require(bytes[prefix.Length + 8] == (byte)'|' && payloadLength >= 2
            && payloadLength <= DataRules.MaxFrameBytes - begin - suffix.Length, "frame-length-limit");
        var end = begin + payloadLength;
        DataRules.Require(bytes.Length >= end + suffix.Length && bytes.Slice(end, suffix.Length).SequenceEqual(suffix), "frame-suffix-or-truncation");
        DataRules.Require(allowContextTail || bytes.Length == end + suffix.Length, "frame-trailing-data");
        foreach (var b in bytes[..(end + suffix.Length)]) DataRules.Require(b < 128, "frame-nonascii");
        var body = DataRules.Object(DataRules.Parse(bytes.Slice(begin, payloadLength).ToArray()), "frame-body");
        ValidateBody(body, session, sequence);
        return body;
    }
    private static void ValidateBody(JsonObject body, string session, long sequence)
    {
        DataRules.Require(DataRules.Session.IsMatch(session) && sequence is > 0 and <= 9_007_199_254_740_991, "expected-session-sequence");
        DataRules.ExactKeys(body, "schemaVersion", "producer", "session", "sequence", "part", "parts", "records");
        DataRules.Require(DataRules.Integer(body["schemaVersion"], "frame-schema") == 1
            && DataRules.Text(body["producer"], "frame-producer") == "RRE-feasibility-fixture", "frame-producer-schema");
        DataRules.Require(DataRules.Text(body["session"], "frame-session") == session
            && DataRules.Integer(body["sequence"], "frame-sequence") == sequence, "frame-session-sequence");
        var part = DataRules.Integer(body["part"], "part"); var parts = DataRules.Integer(body["parts"], "parts");
        DataRules.Require(parts is > 0 and <= DataRules.MaxParts && part > 0 && part <= parts, "frame-part-limit");
        DataRules.Abilities(body["records"]);
    }
    public static JsonArray Assemble(IReadOnlyList<JsonObject> frames)
    {
        DataRules.Require(frames.Count is > 0 and <= DataRules.MaxParts, "frame-count-limit");
        var first = frames[0];
        var total = DataRules.Integer(first["parts"], "parts");
        DataRules.Require(total == frames.Count, "missing-or-extra-parts");
        var ordered = new SortedDictionary<long, JsonObject>();
        foreach (var frame in frames)
        {
            ValidateBody(frame, DataRules.Text(first["session"], "session"), DataRules.Integer(first["sequence"], "sequence"));
            DataRules.Require(DataRules.Integer(frame["parts"], "parts") == total
                && DataRules.Integer(frame["sequence"], "sequence") == DataRules.Integer(first["sequence"], "sequence")
                && DataRules.Text(frame["session"], "session") == DataRules.Text(first["session"], "session")
                && DataRules.Text(frame["producer"], "producer") == "RRE-feasibility-fixture", "mixed-publication");
            var part = DataRules.Integer(frame["part"], "part");
            DataRules.Require(part > 0 && part <= total && ordered.TryAdd(part, frame), "duplicate-or-invalid-part");
        }
        var records = new JsonArray();
        foreach (var frame in ordered.Values)
            foreach (var row in frame["records"]!.AsArray()) records.Add(row?.DeepClone());
        return DataRules.Abilities(records);
    }
}
