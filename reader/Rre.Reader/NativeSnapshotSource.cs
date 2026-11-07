using System.Globalization;
using System.Text.Json.Nodes;

namespace Rre.Reader;

/// <summary>Replays an explicit native snapshot/request pair. Never opens a process.</summary>
public sealed class NativeSnapshotSource(string input, string requestFile, string session, long sequence) : IObservationSource
{
    public async Task<SourceCapture> ReadAsync(CancellationToken cancellationToken = default)
    {
        var snapshotBytes = await DataRules.ReadFileAsync(input, 8 * 1024 * 1024, cancellationToken);
        var requestBytes = await DataRules.ReadFileAsync(requestFile, 65536, cancellationToken);
        return Decode(snapshotBytes, requestBytes, session, sequence, Path.GetFullPath(input), Path.GetFullPath(requestFile));
    }
    public static SourceCapture Decode(byte[] snapshotBytes, byte[] requestBytes, string session, long sequence,
        string inputLabel = "in-memory-snapshot", string requestLabel = "in-memory-request")
    {
        DataRules.Require(snapshotBytes.Length is > 0 and <= 8 * 1024 * 1024 && requestBytes.Length is > 0 and <= 65536, "native-input-byte-limit");
        DataRules.Require(DataRules.Session.IsMatch(session) && sequence is > 0 and <= 9_007_199_254_740_991, "expected-session-sequence");
        var request = DataRules.Object(DataRules.Parse(requestBytes), "native-request-object");
        DataRules.ExactKeys(request, "schemaVersion", "evidenceKind", "target", "maxDurationMilliseconds", "ranges");
        DataRules.Require(DataRules.Integer(request["schemaVersion"], "request-schema") == 1
            && DataRules.Text(request["evidenceKind"], "request-kind") == "native-memory-snapshot-request/1", "native-request-contract");
        var duration = DataRules.Integer(request["maxDurationMilliseconds"], "request-duration");
        DataRules.Require(duration is > 0 and <= 30000, "native-request-duration");
        var target = DataRules.Object(request["target"], "native-target");
        DataRules.ExactKeys(target, "processId", "processStartUtcTicks", "executableSha256");
        var pid = DataRules.Integer(target["processId"], "target-pid");
        var ticks = DataRules.Integer(target["processStartUtcTicks"], "target-start");
        var executableSha = DataRules.Text(target["executableSha256"], "target-sha");
        DataRules.Require(pid is > 0 and <= int.MaxValue && ticks > 0 && IsSha(executableSha), "native-target-limit");
        var snapshot = DataRules.Object(DataRules.Parse(snapshotBytes), "native-snapshot-object");
        DataRules.ExactKeys(snapshot, "schemaVersion", "evidenceKind", "source", "identity", "startedAtUtc", "completedAtUtc", "status", "reason", "chunks", "limitations");
        DataRules.Require(DataRules.Integer(snapshot["schemaVersion"], "snapshot-schema") == 1
            && DataRules.Text(snapshot["evidenceKind"], "snapshot-kind") == "native-memory-snapshot/1"
            && DataRules.Text(snapshot["status"], "snapshot-status") == "complete" && snapshot["reason"] is null, "native-snapshot-incomplete");
        var source = DataRules.Object(snapshot["source"], "snapshot-source");
        DataRules.ExactKeys(source, "requestEvidenceKind", "requestSha256", "requestSha256Verification", "implementation");
        var requestSha = DataRules.Sha(requestBytes);
        DataRules.Require(DataRules.Text(source["requestEvidenceKind"], "request-source-kind") == "native-memory-snapshot-request/1"
            && DataRules.Text(source["requestSha256Verification"], "request-verification") == "producer-declared"
            && SameSha(DataRules.Text(source["requestSha256"], "request-source-sha"), requestSha), "native-request-sha-mismatch");
        var identity = DataRules.Object(snapshot["identity"], "snapshot-identity");
        DataRules.ExactKeys(identity, "processId", "processStartUtcTicks", "executablePath", "executableSha256", "moduleBaseAddress", "moduleSize");
        DataRules.Require(DataRules.Integer(identity["processId"], "snapshot-pid") == pid
            && DataRules.Integer(identity["processStartUtcTicks"], "snapshot-start") == ticks
            && SameSha(DataRules.Text(identity["executableSha256"], "snapshot-exe-sha"), executableSha), "native-target-mismatch");
        var executablePath = DataRules.Text(identity["executablePath"], "snapshot-executable-path");
        var moduleBase = DataRules.Integer(identity["moduleBaseAddress"], "snapshot-module-base");
        var moduleSize = DataRules.Integer(identity["moduleSize"], "snapshot-module-size");
        DataRules.Require(!string.IsNullOrWhiteSpace(executablePath) && executablePath.Length <= 32768
            && moduleBase is >= 0x10000 and < 0x800000000000 && moduleSize is > 0 and <= int.MaxValue
            && moduleBase + moduleSize < 0x800000000000 && ticks <= DateTime.MaxValue.Ticks, "native-module-identity-limit");
        var limitations = snapshot["limitations"] as JsonArray ?? throw new ReaderFailure("native-limitations");
        DataRules.Require(limitations.Count <= 32, "native-limitations-limit");
        foreach (var item in limitations) DataRules.Require(DataRules.Text(item, "native-limitation").Length <= 2048, "native-limitation-limit");
        var implementation = DataRules.Object(source["implementation"], "snapshot-implementation");
        DataRules.ExactKeys(implementation, "toolVersion", "deploymentKind", "assemblySha256", "bundleFileName", "bundleSha256");
        var toolVersion = DataRules.Text(implementation["toolVersion"], "snapshot-tool-version");
        DataRules.Require(!string.IsNullOrWhiteSpace(toolVersion) && toolVersion.Length <= 128, "native-tool-version-limit");
        DataRules.Require(DataRules.Text(implementation["deploymentKind"], "snapshot-deployment") == "single-file-bundle"
            && DataRules.Text(implementation["bundleFileName"], "snapshot-bundle") == "RiftReader2.Live.exe"
            && implementation["assemblySha256"] is null, "native-implementation-contract");
        var bundleSha = DataRules.Text(implementation["bundleSha256"], "snapshot-reader-sha");
        DataRules.Require(bundleSha.Equals("F4148B838AF694EF95FD46DE76859CE9DF55194A9FE8BE1DF74FC2F8F0BCE80F", StringComparison.OrdinalIgnoreCase)
            || bundleSha.Equals("B8A725E6A9CE663C36CB836681ED660261B07FDA4118A0167262E92131B2373E", StringComparison.OrdinalIgnoreCase), "native-reader-unqualified");
        var startedText = DataRules.Text(snapshot["startedAtUtc"], "snapshot-clock");
        var completedText = DataRules.Text(snapshot["completedAtUtc"], "snapshot-clock");
        DataRules.Require(DateTimeOffset.TryParse(startedText, CultureInfo.InvariantCulture, DateTimeStyles.RoundtripKind, out var started)
            && DateTimeOffset.TryParse(completedText, CultureInfo.InvariantCulture, DateTimeStyles.RoundtripKind, out var completed)
            && started >= new DateTimeOffset(ticks, TimeSpan.Zero) && completed >= started, "native-clock-order");
        var ranges = request["ranges"] as JsonArray ?? throw new ReaderFailure("native-ranges");
        DataRules.Require(ranges.Count is > 0 and <= DataRules.MaxParts, "native-range-count");
        var plans = new List<(ulong Start, int Length)>();
        foreach (var item in ranges)
        {
            var range = DataRules.Object(item, "native-range-object");
            DataRules.ExactKeys(range, "addressKind", "address", "byteLength");
            DataRules.Require(DataRules.Text(range["addressKind"], "address-kind") == "absolute-session-address", "native-address-kind");
            var address = Address(range["address"]); var length = DataRules.Integer(range["byteLength"], "range-length");
            DataRules.Require(length is > 0 and <= DataRules.MaxFrameBytes && address + (ulong)length < 0x800000000000, "native-range-limit");
            plans.Add((address, (int)length));
        }
        var sorted = plans.OrderBy(r => r.Start).ToArray();
        for (var i = 1; i < sorted.Length; i++)
            DataRules.Require(sorted[i].Start >= sorted[i - 1].Start + (ulong)sorted[i - 1].Length, "native-overlapping-ranges");
        var chunks = snapshot["chunks"] as JsonArray ?? throw new ReaderFailure("native-chunks");
        DataRules.Require(chunks.Count is > 0 and <= DataRules.MaxParts * 2, "native-chunk-count");
        var copied = new Dictionary<ulong, byte[]>();
        foreach (var item in chunks)
        {
            var chunk = DataRules.Object(item, "native-chunk-object");
            DataRules.ExactKeys(chunk, "address", "requestedByteLength", "status", "bytesRead", "bytesBase64", "bytesSha256", "win32ErrorCode", "reason");
            var address = Address(chunk["address"]);
            var count = DataRules.Integer(chunk["requestedByteLength"], "chunk-length");
            DataRules.Require(count is > 0 and <= 4096 && DataRules.Text(chunk["status"], "chunk-status") == "success"
                && chunk["win32ErrorCode"] is null && chunk["reason"] is null
                && DataRules.Integer(chunk["bytesRead"], "chunk-bytes-read") == count, "native-chunk-incomplete");
            var encoded = DataRules.Text(chunk["bytesBase64"], "chunk-base64");
            DataRules.Require(encoded.Length <= 5464, "native-chunk-base64-limit");
            var raw = Convert.FromBase64String(encoded);
            DataRules.Require(Convert.ToBase64String(raw) == encoded && raw.Length == count
                && SameSha(DataRules.Text(chunk["bytesSha256"], "chunk-sha"), DataRules.Sha(raw)), "native-chunk-hash-or-length");
            DataRules.Require(copied.TryAdd(address, raw), "native-duplicate-chunk");
        }
        var frames = new List<JsonObject>();
        bool? production = null;
        foreach (var plan in plans)
        {
            var bytes = new byte[plan.Length];
            for (var offset = 0; offset < plan.Length; offset += 4096)
            {
                var count = Math.Min(4096, plan.Length - offset);
                DataRules.Require(copied.Remove(plan.Start + (ulong)offset, out var part) && part.Length == count, "native-missing-or-misaligned-chunk");
                part!.CopyTo(bytes, offset);
            }
            var isProduction = bytes.AsSpan().StartsWith("RREC2|"u8);
            DataRules.Require(production is null || production == isProduction, "native-mixed-frame-contracts");
            production = isProduction;
            frames.Add(isProduction ? ProductionFrameCodec.DecodeFrame(bytes, session, sequence, allowContextTail: true)
                : MemoryScanSource.DecodeFrame(bytes, session, sequence, allowContextTail: true));
        }
        DataRules.Require(copied.Count == 0, "native-unrequested-chunk");
        var publication = production == true ? ProductionFrameCodec.Assemble(frames) : null;
        return new(publication?.Abilities ?? MemoryScanSource.Assemble(frames), publication?.Context, new JsonObject
        {
            ["kind"] = "native-snapshot-replay", ["path"] = inputLabel, ["sha256"] = DataRules.Sha(snapshotBytes),
            ["bytes"] = snapshotBytes.Length, ["requestPath"] = requestLabel, ["requestSha256"] = requestSha,
            ["producer"] = publication is null ? "RRE-feasibility-fixture" : "RRECollector", ["partCount"] = frames.Count,
            ["producerVersion"] = publication?.AddonVersion,
            ["publicationContract"] = publication is null ? "RREC1-fixture" : "RREC2",
            ["payloadSha256"] = publication?.PayloadSha256, ["payloadBytes"] = publication?.PayloadBytes,
            ["counts"] = publication?.Counts.DeepClone(), ["expectedSession"] = session,
            ["expectedProcessId"] = pid, ["expectedProcessStartUtcTicks"] = ticks.ToString(CultureInfo.InvariantCulture),
            ["expectedExecutableSha256"] = executableSha, ["producerDeclaredBundleSha256"] = bundleSha,
            ["capturedAtUtc"] = completedText, ["artifactIdentityMatchesRequest"] = true,
            ["limit"] = "Snapshot/request consistency is verified; producer declarations and replay do not prove current target or authenticity."
        }, sequence, publication is null);
    }
    private static ulong Address(JsonNode? node)
    {
        var text = DataRules.Text(node, "native-address");
        DataRules.Require(text.Length is >= 3 and <= 18 && text.StartsWith("0x", StringComparison.Ordinal)
            && ulong.TryParse(text.AsSpan(2), NumberStyles.AllowHexSpecifier, CultureInfo.InvariantCulture, out _), "native-address");
        var address = ulong.Parse(text.AsSpan(2), NumberStyles.AllowHexSpecifier, CultureInfo.InvariantCulture);
        DataRules.Require(address >= 0x10000 && address < 0x800000000000 && text == "0x" + address.ToString("X"), "native-address-limit");
        return address;
    }
    private static bool IsSha(string value) => value.Length == 64 && value.All(c => c is >= '0' and <= '9' or >= 'A' and <= 'F' or >= 'a' and <= 'f');
    private static bool SameSha(string a, string b) => IsSha(a) && IsSha(b) && a.Equals(b, StringComparison.OrdinalIgnoreCase);
}
