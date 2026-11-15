import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { EXPECTED_FILES, verifyDeltaMarkdown, verifyDeltaOnDisk } from "./verify-sc604-evidence-delta.mjs";
import { canonicalRepositoryTextBytes } from "./repository-text-eol.mjs";

const bytes = name => Buffer.from("SC604 synthetic evidence for " + name, "utf8");
const sha = name => createHash("sha256").update(bytes(name)).digest("hex");
const row = (name, hash = sha(name)) =>
  `| [Source](${name}) — \`${hash}\` | Synthetic | Not live evidence |`;
const makeDoc = (names = EXPECTED_FILES) =>
  "# Synthetic supplement\n\n## Verified additions since the November 1 synthesis\n\n" +
  "| Source | What | Limit |\n| --- | --- | --- |\n" +
  names.map(name => row(name)).join("\n") +
  "\n\n## Remaining decision gates — keep independent\n";
const verify = (doc, read = bytes) => verifyDeltaMarkdown(doc, read);

test("canonical Git text retains raw bytes except CRLF checkout pairs", () => {
  const checkout = Buffer.from([0xef,0xbb,0xbf,0x61,13,10,0x62,13,0x63,0xff]);
  assert.deepEqual(canonicalRepositoryTextBytes(checkout),Buffer.from([0xef,0xbb,0xbf,0x61,10,0x62,13,0x63,0xff]));
  assert.deepEqual(canonicalRepositoryTextBytes(Buffer.from("already-LF\n")),Buffer.from("already-LF\n"));
  assert.throws(()=>canonicalRepositoryTextBytes("not bytes"),/must be bytes/);
});
test("injected source bytes remain strict even when checkout line endings differ", () => {
  const name=EXPECTED_FILES[0];
  const withCRLF=n=>n===name?Buffer.concat([bytes(n),Buffer.from("\r\n")]):bytes(n);
  assert.throws(()=>verify(makeDoc(),withCRLF),/source hash mismatch/);
});
test("current SC604 supplement verifies exactly six saved source bytes", () => {
  const result = verifyDeltaOnDisk();
  assert.equal(result.ok, true);
  assert.equal(result.sourcesVerified, 6);
  assert.deepEqual(new Set(result.sources.map(x => x.basename)), new Set(EXPECTED_FILES));
});
test("valid source rows may be reordered and CRLF-terminated", () => {
  const reordered = makeDoc([...EXPECTED_FILES].reverse()).replace(/\n/g, "\r\n");
  assert.equal(verify(reordered).sourcesVerified, 6);
});
test("changed digest rejects even when all six source paths exist", () => {
  const first = EXPECTED_FILES[0];
  const wrong = (sha(first)[0] === "a" ? "b" : "a") + sha(first).slice(1);
  assert.throws(() => verify(makeDoc().replace(row(first), row(first, wrong))), /hash mismatch/);
});
test("missing, extra and duplicated source rows reject", () => {
  assert.throws(() => verify(makeDoc(EXPECTED_FILES.slice(1))), /count mismatch/);
  assert.throws(() => verify(makeDoc([...EXPECTED_FILES, EXPECTED_FILES[0]])), /count mismatch/);
  assert.throws(() => verify(makeDoc([...EXPECTED_FILES.slice(0, 5), EXPECTED_FILES[0]])), /Duplicate/);
});
test("traversal, absolute Windows path and URL reject before reading bytes", () => {
  for (const bad of ["../secret.md", "C:\\private\\secret.md", "https://example.com/source.md"]) {
    let reads = 0;
    const doc = makeDoc([bad, ...EXPECTED_FILES.slice(1)]);
    assert.throws(() => verify(doc, name => { reads++; return bytes(name); }), /Unknown SC604 source path/);
    assert.equal(reads, 0);
  }
});
test("uppercase, shortened, non-hex and unbackticked digests reject", () => {
  const first = EXPECTED_FILES[0], current = row(first);
  for (const bad of [sha(first).toUpperCase(), sha(first).slice(1), "z".repeat(64)]) {
    assert.throws(() => verify(makeDoc().replace(current, row(first, bad))), /Malformed SC604 source digest/);
  }
  assert.throws(() => verify(makeDoc().replace(current, current.replaceAll("`", ""))), /Malformed SC604 source row/);
});
test("a missing source or non-byte source fails closed", () => {
  const missing = EXPECTED_FILES[0];
  assert.throws(() => verify(makeDoc(), name => {
    if (name === missing) throw new Error("Unavailable source");
    return bytes(name);
  }), /Unavailable source/);
  assert.throws(() => verify(makeDoc(), () => "not bytes"), /Invalid SC604 source bytes/);
});
test("extra or replaced malformed pipe rows cannot be silently ignored", () => {
  const doc = makeDoc(), first = EXPECTED_FILES[0];
  const extra = doc.replace("\n\n## Remaining", "\n|[Extra](../private.md) — \`bad\` | Invalid | Row |\n\n## Remaining");
  assert.throws(() => verify(extra), /source count mismatch/);
  const noSpace = doc.replace(row(first), row(first).replace("| [", "|["));
  assert.throws(() => verify(noSpace), /Malformed SC604 source row/);
  const twoSpaces = doc.replace(row(first), row(first).replace("| [", "|  ["));
  assert.throws(() => verify(twoSpaces), /Malformed SC604 source row/);
});
test("missing heading or table end fails closed", () => {
  assert.throws(() => verify(makeDoc().replace("## Verified additions", "## New additions")), /table missing/);
  assert.throws(() => verify(makeDoc().replace("## Remaining", "### Remaining")), /not bounded/);
});
