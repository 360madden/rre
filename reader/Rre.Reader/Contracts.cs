using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

namespace Rre.Reader;

public sealed class ReaderFailure(string code) : Exception(code);
public sealed record SourceCapture(JsonArray Abilities, JsonObject? Context, JsonObject Evidence, long Sequence, bool Fixture);
public interface IObservationSource
{
    Task<SourceCapture> ReadAsync(CancellationToken cancellationToken = default);
}

public static class DataRules
{
    public const int MaxRecords = 512;
    public const int MaxFrameBytes = 8192;
    public const int MaxParts = 16;
    public static readonly Regex Id = new("\\AA[0-9A-F]{16}\\z", RegexOptions.CultureInvariant);
    public static readonly Regex Session = new("\\A[0-9a-f]{32}\\z", RegexOptions.CultureInvariant);
    public static string Sha(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
    public static void Require(bool condition, string code) { if (!condition) throw new ReaderFailure(code); }
    public static JsonNode Parse(byte[] bytes)
    {
        using var doc = JsonDocument.Parse(bytes, new JsonDocumentOptions { MaxDepth = 48 });
        Check(doc.RootElement);
        return JsonNode.Parse(doc.RootElement.GetRawText()) ?? throw new ReaderFailure("json-null");
    }
    private static void Check(JsonElement element)
    {
        if (element.ValueKind == JsonValueKind.Object)
        {
            var keys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var property in element.EnumerateObject())
            {
                Require(keys.Add(property.Name), "duplicate-json-property");
                Check(property.Value);
            }
        }
        else if (element.ValueKind == JsonValueKind.Array)
            foreach (var value in element.EnumerateArray()) Check(value);
        else if (element.ValueKind == JsonValueKind.Number)
            Require(element.TryGetDouble(out var number) && double.IsFinite(number), "nonfinite-number");
    }
    public static JsonObject Object(JsonNode? node, string code) => node as JsonObject ?? throw new ReaderFailure(code);
    public static string Text(JsonNode? node, string code)
        => node is JsonValue value && value.TryGetValue<string>(out var text) ? text : throw new ReaderFailure(code);
    public static long Integer(JsonNode? node, string code)
    {
        if (node is JsonValue value)
        {
            if (value.TryGetValue<long>(out var number)) return number;
            if (value.TryGetValue<int>(out var small)) return small;
        }
        throw new ReaderFailure(code);
    }
    public static bool Boolean(JsonNode? node, string code)
        => node is JsonValue value && value.TryGetValue<bool>(out var flag) ? flag : throw new ReaderFailure(code);
    public static void ExactKeys(JsonObject obj, params string[] keys)
        => Require(obj.Select(p => p.Key).ToHashSet(StringComparer.Ordinal).SetEquals(keys), "unexpected-schema-keys");
    private static readonly HashSet<string> AbilityFields = new(StringComparer.Ordinal)
    {
        "lookupId", "id", "idNew", "name", "description", "target", "castingTime", "channeled", "cooldown",
        "currentCooldownBegin", "currentCooldownDuration", "currentCooldownRemaining", "currentCooldownExpired",
        "currentCooldownPaused", "unusable", "outOfRange", "rangeMin", "rangeMax", "costPower", "costMana",
        "costEnergy", "costCharge", "costSpirit", "costPlanarCharge", "positioned", "passive", "continuous",
        "autoattack", "weapon", "stealthRequired", "gainCharge", "racial", "icon", "focusMin", "focusMax"
    };
    public static JsonArray Abilities(JsonNode? node)
    {
        var array = node as JsonArray ?? throw new ReaderFailure("abilities-not-array");
        Require(array.Count is > 0 and <= MaxRecords, "ability-count-limit");
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var item in array)
        {
            var record = Object(item, "ability-not-object");
            var id = Text(record["lookupId"], "ability-id-type");
            Require(Id.IsMatch(id) && ids.Add(id), "invalid-or-duplicate-ability-id");
            foreach (var (key, value) in record)
            {
                Require(AbilityFields.Contains(key), "unknown-ability-field");
                Require(value is JsonValue, "ability-field-not-scalar");
                var scalar = (JsonValue)value!;
                if (scalar.GetValueKind() == JsonValueKind.String)
                    Require(Text(scalar, "ability-field-string").Length <= 4096, "ability-string-limit");
                else if (scalar.GetValueKind() == JsonValueKind.Number)
                    Require(scalar.TryGetValue<double>(out var number) && double.IsFinite(number), "ability-field-number");
                else Require(scalar.GetValueKind() is JsonValueKind.True or JsonValueKind.False, "ability-field-not-scalar");
            }
        }
        return (JsonArray)array.DeepClone();
    }
    public static async Task<byte[]> ReadFileAsync(string path, int limit, CancellationToken ct = default)
    {
        await using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
        var bytes = new byte[limit + 1];
        var length = 0;
        while (length < bytes.Length)
        {
            var n = await stream.ReadAsync(bytes.AsMemory(length), ct);
            if (n == 0) break;
            length += n;
        }
        Require(length is > 0 && length <= limit, "input-byte-limit");
        return bytes[..length];
    }
}

public static class ObservationModules
{
    public static JsonObject Build(SourceCapture capture, string module)
    {
        DataRules.Require(module is "all" or "abilities" or "context", "unknown-module");
        DataRules.Require(capture.Sequence is > 0 and <= 9_007_199_254_740_991, "observation-sequence-limit");
        DataRules.Abilities(capture.Abilities);
        var modules = new JsonObject();
        if (module is "all" or "abilities") modules["abilities"] = new JsonObject
        {
            ["status"] = "available", ["classification"] = "API-listed capture; learnable/usable/bound unknown",
            ["count"] = capture.Abilities.Count, ["complete"] = true, ["records"] = capture.Abilities.DeepClone(),
            ["missingFieldPolicy"] = "Missing optional fields are unknown; no default false/zero is inserted."
        };
        if (module is "all" or "context") modules["context"] = new JsonObject
        {
            ["status"] = capture.Context is null ? "unavailable" : "available", ["value"] = capture.Context?.DeepClone()
        };
        return new JsonObject
        {
            ["schemaVersion"] = 1, ["reader"] = "Rre.Reader", ["readerVersion"] = "0.1.1",
            ["observedAtUtc"] = DateTimeOffset.UtcNow.ToString("O"), ["sequence"] = capture.Sequence,
            ["source"] = capture.Evidence.DeepClone(), ["modules"] = modules,
            ["qualification"] = new JsonObject
            {
                ["offlineStructureVerified"] = true, ["complete"] = module == "abilities" || capture.Context is not null, ["live"] = false,
                ["fixture"] = capture.Fixture, ["freshnessVerified"] = false, ["processBuildVerified"] = false,
                ["atomicSnapshotVerified"] = false, ["restartQualified"] = false,
                ["limit"] = "Persisted/replayed data only. Host observation time is not game capture time."
            }
        };
    }
}
