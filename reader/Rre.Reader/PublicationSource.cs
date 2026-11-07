using System.Text;
using System.Text.Json.Nodes;

namespace Rre.Reader;

/// <summary>Explicit offline frame export, useful for publisher interoperability checks.</summary>
public sealed class PublicationSource(string input, string session, long sequence) : IObservationSource
{
    public async Task<SourceCapture> ReadAsync(CancellationToken cancellationToken = default)
    {
        var bytes = await DataRules.ReadFileAsync(input, 256 * 1024, cancellationToken);
        var root = DataRules.Object(DataRules.Parse(bytes), "publication-artifact");
        DataRules.ExactKeys(root, "schemaVersion", "evidenceKind", "origin", "frames");
        DataRules.Require(DataRules.Integer(root["schemaVersion"], "publication-artifact-schema") == 1
            && DataRules.Text(root["evidenceKind"], "publication-artifact-kind") == "rrec2-publication-artifact/1", "publication-artifact-contract");
        var origin = DataRules.Text(root["origin"], "publication-origin");
        DataRules.Require(!string.IsNullOrWhiteSpace(origin) && origin.Length <= 256, "publication-origin-limit");
        var rawFrames = root["frames"] as JsonArray ?? throw new ReaderFailure("publication-artifact-frames");
        DataRules.Require(rawFrames.Count is > 0 and <= 16, "publication-frame-count");
        var frames = new List<JsonObject>();
        foreach (var item in rawFrames)
        {
            var text = DataRules.Text(item, "publication-frame-string");
            DataRules.Require(text.Length <= 8192 && text.All(c => c < 128), "publication-frame-ascii-limit");
            frames.Add(ProductionFrameCodec.DecodeFrame(Encoding.ASCII.GetBytes(text), session, sequence));
        }
        var publication = ProductionFrameCodec.Assemble(frames);
        return new(publication.Abilities, publication.Context, new JsonObject
        {
            ["kind"] = "publication-artifact-replay", ["path"] = Path.GetFullPath(input), ["sha256"] = DataRules.Sha(bytes),
            ["bytes"] = bytes.Length, ["producer"] = "RRECollector", ["producerVersion"] = ProductionFrameCodec.AddonVersion,
            ["publicationContract"] = "RREC2", ["declaredOrigin"] = origin, ["partCount"] = frames.Count,
            ["payloadSha256"] = publication.PayloadSha256, ["payloadBytes"] = publication.PayloadBytes,
            ["counts"] = publication.Counts.DeepClone(), ["expectedSession"] = session,
            ["runtimeProducerVerified"] = false,
            ["limit"] = "Explicit offline frame export. Declared origin and valid contract do not prove game execution or authenticity."
        }, sequence, false);
    }
}
