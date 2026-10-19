"""M3-001: byte-verify the saved exact-build Havok job-owner leads.

Reads existing RRE artifacts, original Rift PE, and V7 manifests. No process access,
game controls, installations, target writes or new pathfinding algorithm.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import struct
import sys
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
BASE = 0x140000000
BUILD = Path(r"C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe")
EXPECTED = "7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"
TAGS = {
    "type3-producer": ("e7c1d5f6bb5fa8de82177b4bea905003832c126bb7b2d2957eba1d7a58451ff2", "884f891a2a35a6a46a06e46e4222f40c4e051651b9117339118ac0fac091432d"),
    "type1-producer": ("2f3fee7a0e75b00b5ef9813345e1d80eba1b15700737e2a2cf3b9de13d84f8f8", "21ad2c4fcf96b43b85b12ebaf24fa25413a6113c707dbc55158530385aad064e"),
    "producer-address-refs": ("110599d207b374387f22be5be32ba38b9845cc7a80dbe91313df3b7db98ae3ea", "c830c1eee61b97179266f60ce391b66b49faebbfb2d4f1bdfbbcb1273cf450bd"),
    "wrapper-owner-refs": ("37b66c46ed9342df8b2f62f75d69acdb3d431a1c7718b13cdcb90c4bd22d360c", "f88ef04f1a2300261a3e15cd39b6a2b2dc1208243f3f891c218db1ded53e816e"),
    "physics-owner-table-refs": ("0b6ce9df4188a8caeb6e46067154db0df8e8976fdef463577e876bd1f5647de5", "bf4fa3387ed10d19fb2aa25a3559566205885919af185eaa68f6f9e18af1c8ff"),
    "simulation-ctor": ("6797a62620e95b7a4ace279bdc23c06ac33c1e8d023f22f433b7f26739a9eca7", "05b5a61bb03f6b70266607baad79835e74bac88ea8a9c8eb4a3b2550ac8e8e8e"),
}
def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()
def check(predicate: bool, message: str) -> None:
    if not predicate:
        raise ValueError(message)


def saved_digest(b: bytes, expected: str) -> str:
    """Preserve original raw SHA; distinguish Git checkout EOL representation."""
    if sha(b) == expected:
        return "exact-raw"
    canonical = b.replace(b"\r\n", b"\n")
    if sha(canonical) == expected:
        return "checkout-crlf-to-original-lf"
    crlf = canonical.replace(b"\n", b"\r\n")
    if sha(crlf) == expected:
        return "checkout-lf-to-original-crlf"
    raise ValueError("Source artifact differs beyond permitted LF/CRLF conversion")


def verify() -> None:
    import pefile, capstone
    from capstone.x86_const import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP
    raw = BUILD.read_bytes()
    check(sha(raw) == EXPECTED, "Native executable identity changed")
    pe = pefile.PE(data=raw, fast_load=True)
    try:
        check(int(pe.OPTIONAL_HEADER.ImageBase) == BASE and pe.FILE_HEADER.Machine == 0x8664, "Wrong PE identity")
        captured = {}
        decoded = {}
        artifacts = []
        for tag,(artifact_hash,manifest_hash) in TAGS.items():
            prefix = ROOT / "tools" / "agents" / "pathfinding" / f"m3-001-{tag}-20261019"
            a_bytes = (prefix.with_suffix(".json")).read_bytes()
            m_bytes = (Path(str(prefix)+"-manifest.json")).read_bytes()
            artifact_eol = saved_digest(a_bytes, artifact_hash)
            manifest_eol = saved_digest(m_bytes, manifest_hash)
            artifact, manifest = json.loads(a_bytes), json.loads(m_bytes)
            check(artifact["sha256"] == EXPECTED and manifest["source"]["sha256"] == EXPECTED, "Mixed build: "+tag)
            check(manifest["status"] == "completed" and manifest["invocation"]["exitCode"] == 0, "Incomplete V7 query: "+tag)
            check(manifest["coverage"]["boundedCaptureComplete"] is True, "Incomplete bounded capture: "+tag)
            check(manifest["artifact"]["sha256"] == artifact_hash, "Artifact/manifest mismatch: "+tag)
            check(manifest["parserDiagnostics"]["count"] == 825, "Parser-warning provenance inconsistent: "+tag)
            check(manifest["source"]["unchangedDuringRun"] is True, "Source mutated while scanning: "+tag)
            captured[tag] = artifact
            artifacts.append({"tag":tag,"artifactSha256":artifact_hash,"manifestSha256":manifest_hash,
                              "artifactCheckout":artifact_eol,"manifestCheckout":manifest_eol,
                              "windows":len(artifact.get("functions",[])),"references":len(artifact.get("references",[]))})
            if "functions" in artifact:
                md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
                for function in artifact["functions"]:
                    start,end = int(function["beginRva"],16), int(function["endRvaExclusive"],16)
                    blob = pe.get_data(start,min(16384,end-start))
                    check(sha(blob) == function["windowSha256"], "Code window mismatched: "+tag)
                    instructions=list(md.disasm(blob, BASE+start))
                    check(len(instructions)==len(function["instructions"]), "Instruction count mismatch: "+tag)
                    for insn,row in zip(instructions,function["instructions"]):
                        check(row["rva"]==hex(insn.address-BASE) and row["bytes"]==insn.bytes.hex(),
                              "Instruction offset/bytes mismatch: "+tag)
                        decoded[insn.address-BASE]=insn
                for call in artifact.get("callerReferences",[]):
                    if call["instructionBoundaryVerifiedFromPeRange"]:
                        rva=int(call["siteRva"],16);dest=int(call["targetRva"],16)
                        insn=decoded.get(rva)
                        check(insn is not None and insn.mnemonic=="call", "Caller evidence not retained: "+tag)
                        check(insn.op_str==hex(BASE+dest), "Wrong direct-call target: "+tag)
        # Validate exact MSVC RTTI/vftable bytes; do not infer runtime object type from an arbitrary displacement.
        ptr=struct.unpack("<Q", pe.get_data(0x2725560,8))[0]
        locator_rva=ptr-BASE
        check(locator_rva==0x2d75a80, "Unexpected hkpMultiThreadedSimulation locator pointer")
        sig,off,ctor_disp,typedesc,inheritance,self_rva=struct.unpack("<6I",pe.get_data(locator_rva,24))
        check(sig==1 and off==0 and self_rva==locator_rva, "RTTI COL shape mismatch")
        name=pe.get_data(typedesc+16,100).split(b"\0",1)[0].decode("ascii")
        check(name==".?AVhkpMultiThreadedSimulation@@", "Unexpected RTTI class")
        table=0x2725568
        method_slot=0x27255f8
        check((method_slot-table)//8==18, "Unexpected native virtual method slot index")
        method=struct.unpack("<Q",pe.get_data(method_slot,8))[0]
        check(method==BASE+0x8a8d8, "RVA 0x8a8d8 was not in the claimed vftable")
        # The table is followed by a label and the next RTTI locator.
        check(pe.get_data(0x2725610,len(b"TtRecollide PSI\0"))==b"TtRecollide PSI\0", "Neighbor string boundary changed")
        other=struct.unpack("<Q",pe.get_data(0x2725620,8))[0]-BASE
        second=struct.unpack("<6I",pe.get_data(other,24))
        check(second[0]==1 and second[5]==other, "Next vftable metadata no longer valid")
        next_name=pe.get_data(second[3]+16,100).split(b"\0",1)[0].decode("ascii")
        check(next_name==".?AVhkpReportContactMgr@@", "Next owner name mismatch")

        def expect(rva: int, mnemonic: str, substring: str) -> None:
            x=decoded.get(rva)
            check(x is not None and x.mnemonic==mnemonic and substring in x.op_str,
                  "Native instruction qualification mismatch at "+hex(rva))
        expect(0x89ae1,"lea","r11")
        expect(0x89aec,"mov","[r13]")
        expect(0x89cb7,"lea","rax")
        expect(0x89cc1,"mov","[rcx]")
        expect(0x89bd7,"and","[r13 + 0x160]")
        expect(0x8a9df,"mov","[rsi + 0x160]")
        expect(0x8a9e6,"call","0x1400f3fa4")
        expect(0x8f21c,"call","0x14008ecb4")
        expect(0x8f223,"call","0x14008ea08")
        expect(0x7b0a3,"call","0x140089abc")
        refs=captured["physics-owner-table-refs"]["references"]
        check({int(r["siteRva"],16) for r in refs}=={0x89ae1,0x89cb7}, "Unexpected simulation vftable installation sites")
        check(all(r.get("instructionBoundaryVerifiedFromPeRange") for r in refs),
              "Unqualified code-to-table reference")
        stored=captured["producer-address-refs"]["references"]
        check(len(stored)==1 and stored[0]["siteRva"]==hex(method_slot) and stored[0]["targetRva"]=="0x8a8d8",
              "Type1 method pointer reference mismatch")
        type3=captured["type3-producer"]["callerReferences"]
        check(len(type3)==1 and type3[0]["siteRva"]=="0x8f21c" and type3[0]["targetRva"]=="0x8ecb4",
              "Type3 wrapper call not qualified")
        print(json.dumps({
            "status":"PASS","buildSha256":EXPECTED,"artifacts":artifacts,
            "ownerRttiName":name,"ownerCOLRva":hex(locator_rva),"simulationVtable":hex(table),
            "type1VtableSlot":18,"type1SlotRva":hex(method_slot),"type1FunctionRva":"0x8a8d8",
            "vtableInstallInstructions":["0x89ae1","0x89cb7"],
            "simulationQueueFieldReset":"0x89bd7: [r13+0x160] <- 0",
            "type1QueueFieldRead":"0x8a9df: [rsi+0x160]",
            "type1CallsGenericDispatcher":"0x8a9e6 -> 0xf3fa4",
            "type3Caller":"0x8f21c -> 0x8ecb4",
            "qualifiedNativeHandlerType7":False,
            "limitations":["Identifies a physics-simulation owner, not an active type-7 handler.",
                           "Runtime ownership and indirect/tail-call reachability remain unresolved.",
                           "MSVC RTTI/vtable interpretation is grounded in exact bytes, not runtime object capture."]
        }))
    finally:
        pe.close()
if __name__=="__main__":
    verify()
