// Normalize only repository TEXT checked out with CRLF instead of Git's LF bytes.
// Do not use for live captures, executable files, SavedVariables, or deployed addons:
// those must retain their exact raw-byte SHA-256 identity.
export function canonicalRepositoryTextBytes(bytes) {
  if (!(bytes instanceof Uint8Array)) throw new TypeError("Repository text must be bytes");
  const output = Buffer.allocUnsafe(bytes.byteLength);
  let length = 0;
  for (let i = 0; i < bytes.byteLength; i++) {
    if (bytes[i] === 13 && bytes[i + 1] === 10) continue;
    output[length++] = bytes[i];
  }
  return output.subarray(0, length);
}
