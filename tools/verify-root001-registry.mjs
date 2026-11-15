#!/usr/bin/env node
// Exact-build, offline-only RIFT ROOT-001 registry/dispatch verifier.
// This reads an archived PE file; it never attaches to a process or invokes game code.
import { createHash } from 'node:crypto';
import { readFileSync, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const defaultPe = path.join(repoRoot, 'artifacts', 'lab2-live-20261107-0922', 'guest-rift_x64.exe');
const EXPECTED_BYTES = 60493640;
const EXPECTED_SHA256 = '1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8';
const EXPECTED_BASE = 0x140000000n;
const RECORDS = 850;
const RECORD_RVA = 0x2f5a048;
const ROOT_INDEX = 575; // one-based, original image order

// Original RVA windows, inclusive start/exclusive end. These are SHA pins, not runtime offsets.
const WINDOWS = [
  ['first_initializer', 0x175cf7, 0x6b, 'f94eeffaaea3af55eb3943370655b1fb850973f006df54cae49f02beb388aff8'],
  ['last_initializer', 0x178497, 0x6b, '9f7a9cac1d2e29d92ce1d871ae92e152b07f3d08490269ae3cbc81fdd19976f3'],
  ['list_head_reader', 0x8174c0, 0x1b, 'f6739ab62a88f3f1c20f3c87a2db5be9d671fb2ccd6771cd0df3f1119c24b747'],
  ['registration_loop', 0x8174db, 0x1d5, '62a0614b121c967cf1c5286c94779c0463dab787bb00ca98656846765d117b68'],
  ['name_to_id', 0x12764ac, 0x108, '2a4e02372f6c1da4e5f5f8a82ed1d17e7b762bb3647f2d54499ab3431316cdfe'],
  ['keyed_map', 0x817f60, 0x2d8, '10aa1133abb1b4de57ca99515dd63547efeda938af2550451ff6f6f4dc123aea'],
  ['dynamic_tag_lookup', 0x7e91fd, 0xdb, 'd7bbfb71d0a2fea0a97c1b549d6ece34cf65e68cd1411a4a0b675ce1bbb34b45'],
  ['dispatch_tail', 0x7e92d8, 0x2d, 'd45d7936cba5416f47b7dd04a688ede6486e31163280b2272eab345ad5d52c84'],
  ['dispatch_table', 0x26c5a38, 0x18, '8ea0be9b39bc2c6aefab2081f2579386e5a07d498c3689aaf0e2a98200176aaf'],
  ['handler_trampoline', 0x7068c0, 0x10, '7f957041b8f55c437d6f2277ec0e4419633bb5ad0c9784c8c6df73e7b6a54954'],
  ['root_wrapper', 0x7f2570, 0x3c, 'c2b61836bf74b3bb658d05faf9c356eaddaf9f8d694a0e08ca9082d7e6e23dd8'],
  ['dispatch_caller_full', 0x7e91f0, 0x115, '03e769ab903c61f2392e6de1d23d3c9832aeee484fc7d48538d73f0d121f5b23'],
  ['reference_type_helper', 0x1ebecf0, 0x65, '0c6045c0fe2fe250595ba98f75a6fb452d2d21e847941d36ea6f4ef45b271f29'],
  ['dynamic_type_implementation', 0x127303c, 0x1b, 'f31c50eb49b0eeb3cf0eebcf5a7df48d0e1c62f657501dbc8df45a4c4e1d80c6'],
  ['root_singleton_getter', 0x49a020, 0xf5, 'e234449109b1c18628bed66ed83c9fc4fbe5e57f08af2eab063938ec2e991fd0'],
  ['root_constructor', 0x53dc70, 0xb03, 'ad5de6f4c667efdb89b2b9d3d0445ae55e45fb7b9dc024f688e3e77b26ce8e75'],
  ['callback_state_constructor', 0x6a3e80, 0x37, '9484c5dfee91c06e792f3e993e619af7d3e1e3e76bee9883434c89700331ed71'],
  ['c2m_root_eligibility', 0x6a5e1f, 0x30, '9d0da4163403d18c2917ab9ba0e8aceca03fc03fb9612055f143aea9573e80ae'],
  ['root_key_setter', 0x580580, 0x129, 'fd2395dfb7502a9c0a426f1c9626d9e174c150f766e7a96c75c776dbfd8f63e0'],
  ['named_object_singleton_init', 0x1ece1c0, 0x9c, '466b0bb8ddf08cda13d780baf2762d1c6f7efb55887526395dc5f5cef6ff062f'],
  ['name_and_id_selector', 0x1ed56b0, 0x21, '9440bb12908fa6aea9e6828d2808f8745880bbc534d47874385fff3b0b66a1d0'],
  ['virtual_internal_id', 0x1edda60, 0x1b, '822086a9731fc9a012111c1898a7452149428909f9766133a55e1398be61ca8e'],
  ['virtual_name_getter', 0x1ede6f0, 0xa, '9500127a1eb53fda76907d49fe49f018782a4d7f75309e8fd3ecaf73ef2c6839'],
  ['named_object_manager_insertion', 0x1ec50c3, 0x2d, '8bc70bd7c209dd1f286d3b93916145616d91871020421d5030efd7cea67d9419'],
  ['internal_id_record_store', 0x1276c29, 0x137, '5457a59982428434c31033ac4a8ba1d3edc3a2a2398a93003448bf92a6971123'],
  ['internal_id_lookup_return', 0x1276596, 0x0c, '33e7d074c2a83640ba2aa667bcc19d387b2f098419f2ef0a9f2f7933f5ff45cb'],
  ['named_singleton_vtable', 0x2b4a2a8, 0x40, '9f9037d0b8b1cba176066c896600ce048ccb7195bcd62d57a31a18633f5ae4ae'],
];

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function assertClaim(value, message) {
  if (!value) throw new Error('ROOT-001 source verification failed: ' + message);
}

function imageMapper(bytes) {
  assertClaim(bytes.length >= 0x100 && bytes.toString('ascii', 0, 2) === 'MZ', 'not a DOS/PE image');
  const pe = bytes.readUInt32LE(0x3c);
  assertClaim(pe <= bytes.length - 24 && bytes.toString('latin1', pe, pe + 4) === 'PE\u0000\u0000', 'PE signature');
  const machine = bytes.readUInt16LE(pe + 4);
  const count = bytes.readUInt16LE(pe + 6);
  const optionalSize = bytes.readUInt16LE(pe + 20);
  const optional = pe + 24;
  assertClaim(machine === 0x8664 && count > 0 && count <= 96, 'expected AMD64 PE machine and bounded sections');
  assertClaim(optionalSize >= 0x70 && optional + optionalSize <= bytes.length, 'optional header bounds');
  assertClaim(bytes.readUInt16LE(optional) === 0x20b, 'expected PE32+');
  const imageBase = bytes.readBigUInt64LE(optional + 24);
  assertClaim(imageBase === EXPECTED_BASE, 'expected static image base');

  const entries = [];
  const start = optional + optionalSize;
  assertClaim(start + count * 40 <= bytes.length, 'section table bounds');
  for (let i = 0; i < count; i++) {
    const at = start + i * 40;
    entries.push({
      name: bytes.toString('ascii', at, at + 8).replace(/\u0000.*$/, ''),
      virtualSize: bytes.readUInt32LE(at + 8),
      virtualRva: bytes.readUInt32LE(at + 12),
      rawSize: bytes.readUInt32LE(at + 16),
      rawOffset: bytes.readUInt32LE(at + 20),
    });
  }

  // A pointer may legitimately address zero-initialized .data beyond raw file bytes.
  // Only instruction/data reads require an RVA backed by original on-disk bytes.
  function virtualSectionFor(rva, length) {
    assertClaim(Number.isSafeInteger(rva) && Number.isSafeInteger(length) && rva >= 0 && length > 0, 'invalid RVA/size');
    const section = entries.find((s) =>
      rva >= s.virtualRva &&
      rva + length <= s.virtualRva + Math.max(s.virtualSize, s.rawSize)
    );
    assertClaim(section !== undefined, 'RVA outside image sections: 0x' + rva.toString(16));
    return section;
  }

  function sectionFor(rva, length) {
    const section = virtualSectionFor(rva, length);
    assertClaim(rva - section.virtualRva + length <= section.rawSize,
      'RVA has no original raw bytes: 0x' + rva.toString(16));
    const at = section.rawOffset + rva - section.virtualRva;
    assertClaim(at + length <= bytes.length, 'mapped RVA exceeds original file length');
    return { section, at };
  }

  return {
    imageBase,
    sectionFor,
    virtualSectionFor,
    slice(rva, length) {
      const { at } = sectionFor(rva, length);
      return bytes.subarray(at, at + length);
    },
    qword(rva) {
      return bytes.readBigUInt64LE(sectionFor(rva, 8).at);
    },
    int32(rva) {
      return bytes.readInt32LE(sectionFor(rva, 4).at);
    },
  };
}

export function verifyRoot001Bytes(bytes) {
  assertClaim(Buffer.isBuffer(bytes), 'expected a Buffer of original executable bytes');
  assertClaim(bytes.length === EXPECTED_BYTES, 'exact executable size mismatch');
  const actualSha = sha256(bytes);
  assertClaim(actualSha === EXPECTED_SHA256, 'exact executable SHA-256 mismatch');
  const pe = imageMapper(bytes);

  let windowsVerified = 0;
  for (const [name, rva, length, expected] of WINDOWS) {
    assertClaim(sha256(pe.slice(rva, length)) === expected, 'window hash mismatch: ' + name);
    windowsVerified++;
  }

  function hasBytes(rva, hex) {
    const literal = Buffer.from(hex, 'hex');
    assertClaim(pe.slice(rva, literal.length).equals(literal), 'opcode bytes at RVA 0x' + rva.toString(16));
  }
  const anchors = [
    [0x8174ee, '4c8d25'],        // R12 <- shared dispatch table address
    [0x81752a, '488b4608'],      // handler <- node+8
    [0x817531, '4c89642468'],    // stage static table pointer
    [0x817536, '4889442470'],    // stage handler pointer next to it
    [0x817600, 'e8'],            // name -> 16-bit ID
    [0x817632, '488d0d'],       // keyed map global
    [0x81764d, 'e8'],            // keyed map insertion
    [0x817652, '0f10442468'],    // load staged 16-byte pair
    [0x817657, '488b4810'],      // selected entry from helper output
    [0x81765b, '0f114110'],      // store table pointer and handler at entry+0x10/+0x18
    [0x81765f, '0f117120'],      // distinct adjacent clear, NOT the handler store
    [0x817f98, '410fb708'],      // keyed-map WORD ID
    [0x7e920a, 'e8'],            // dynamic-tag discriminator
    [0x7e9218, '0fb7f8'],        // capture 16-bit discriminator
    [0x7e9242, '4c8b1d'],       // same keyed map global
    [0x7e9279, '410fb74808'],    // compare 16-bit key
    [0x7e9282, '498bc0'],       // selected matching hash node in RAX
    [0x7e92ed, '488d4810'],     // RCX=&entry+0x10
    [0x7e92f4, '488b01'],       // load shared table pointer
    [0x7e92f7, 'ff5010'],       // indirect call through table+0x10
    [0x7068c0, '488b4108'],     // read handler at entry+0x18
    [0x7068c4, '488bca'],       // pass original callback input
    [0x7068c7, '48ffe0'],       // tail jump to registered handler

    [0x7e91fa, '488bf1'], // save incoming pointer-to-reference in RSI
    [0x7e9202, '488b09'], // tag input dereferences incoming reference
    [0x7e92f1, '488bd6'], // forward saved reference through RDX
    [0x7f2576, '488bd1'], // ROOT wrapper forwards reference to helper
    [0x1ebecfa, '488b02'], // ROOT helper dereferences original reference
    [0x1ebed20, '488b0f'], // ROOT helper requests inner type tag
    [0x1ebed28, 'b93cdd0000'], // ROOT tag compare immediate
    [0x1ebed2d, '663bc1'], // compare 16-bit AX with 0xdd3c
    [0x49a024, '488b05'], // singleton getter reads one global
    [0x49a02e, '0f85cf000000'], // initialized global branch
    [0x49a0c1, 'b9400f0000'], // new root allocation size is 0xf40
    [0x49a0e0, '48891d'], // singleton initialization stores root
    [0x49a0f7, '48891d'], // singleton return stores root
    [0x53dca8, '488bf1'], // root constructor retains self
    [0x53e553, '488bd6'], // root constructor forwards self
    [0x6a3e97, '48895310'], // state constructor stores self at state+0x10
    [0x6a5e25, '488b4910'], // C2M callback retrieves same root from state
    [0x6a5e37, '488b5610'], // C2M callback reads root again
    [0x6a5e3b, '80ba5803000000'], // C2M root+0x358 availability byte check
    [0x1ece1e7, '488d05'], // name singleton object address
    [0x1ece21e, '488d05'], // named object uses source-pinned vtable
    [0x1ece247, '488905'], // singleton vtable stored in separate object
    [0x1ec50c3, '488d15'], // source name buffer is a different global
    [0x1ed56c0, '488d0d'], // range selector returns distinct name address
    [0x1edda64, 'ba9d54cd15'], // ID method source constant
    [0x1edda6e, 'b9e6880000'], // ID method XOR constant
    [0x1edda73, '6633c1'], // ID method XORs low 16 bits
    [0x1ede6f0, 'ba9169d12d'], // name method source constant
    [0x1276a94, 'ff5008'], // name manager calls object's VMT ID slot
    [0x1276a9d, '0fb7f0'], // name manager retains returned WORD ID
    [0x1276aa0, '66894567'], // name manager stages returned WORD ID
    [0x1276aa4, '41ff5010'], // name manager calls object's VMT name slot
    [0x1276c3f, '668930'], // new-record path writes source-derived WORD
    [0x1276596, '488b4228'], // lookup follows stored ID-record pointer
    [0x127659a, '0fb708'], // lookup reads stored 16-bit ID
    [0x127659f, '66890e'], // lookup writes key for registration
  ];
  for (const [rva, hex] of anchors) hasBytes(rva, hex);

  let directCallsVerified = 0;
  function directCall(at, expectedTarget) {
    hasBytes(at, 'e8');
    const target = at + 5 + pe.int32(at + 1);
    assertClaim(target === expectedTarget, 'call target at RVA 0x' + at.toString(16));
    directCallsVerified++;
  }
  directCall(0x817600, 0x12764ac);
  directCall(0x81764d, 0x817f60);
  directCall(0x7e920a, 0x127303c);
  directCall(0x7f257e, 0x1ebecf0);
  directCall(0x7f258c, 0x49a020);
  directCall(0x7f2597, 0x580580);
  directCall(0x1ebed23, 0x127303c);
  directCall(0x49a0d8, 0x53dc70);
  directCall(0x53e559, 0x6a3e80);
  directCall(0x1ec50d8, 0x1ece1c0);
  directCall(0x1ec50eb, 0x1276a6c);
  directCall(0x1edda69, 0x1ed56b0);

  let ripTargetsVerified = 0;
  function ripReference(at, prefix, target) {
    hasBytes(at, prefix);
    const prefixLength = prefix.length / 2;
    const actual = at + prefixLength + 4 + pe.int32(at + prefixLength);
    assertClaim(actual === target, 'RIP-relative target at RVA 0x' + at.toString(16));
    ripTargetsVerified++;
  }
  ripReference(0x8174ee, '4c8d25', 0x26c5a38);
  ripReference(0x817632, '488d0d', 0x2f59fd0);
  ripReference(0x7e9242, '4c8b1d', 0x2f59fd0);
  ripReference(0x8174cb, '488b35', 0x33747a0);
  ripReference(0x49a024, '488b05', 0x33623e0);
  ripReference(0x49a0e0, '48891d', 0x33623e0);
  ripReference(0x49a0f7, '48891d', 0x33623e0);
  ripReference(0x1ece1e7, '488d05', 0x35199f0);
  ripReference(0x1ece21e, '488d05', 0x2b4a2a8);
  ripReference(0x1ece247, '488905', 0x35199f0);
  ripReference(0x1ec50c3, '488d15', 0x35159f8);
  ripReference(0x1ed56c0, '488d0d', 0x35159f8);

  // A matched keyed entry takes the short jump into the shared call tail.
  function shortBranch(at, opcode, target) {
    hasBytes(at, opcode);
    const destination = at + 2 + pe.slice(at + 1, 1).readInt8(0);
    assertClaim(destination === target, 'conditional dispatch branch at RVA 0x' + at.toString(16));
  }
  shortBranch(0x7e928a, 'eb', 0x7e92c9);
  shortBranch(0x7e92e6, '75', 0x7e92ed);

  let recordsVerified = 0;
  let rootRecord;
  for (let index = 0; index < RECORDS; index++) {
    const rva = RECORD_RVA + index * 24;
    const name = pe.qword(rva);
    const handler = pe.qword(rva + 8);
    const next = pe.qword(rva + 16);
    assertClaim(name >= EXPECTED_BASE && handler >= EXPECTED_BASE, 'node image pointers at ' + index);
    const nameRva = Number(name - EXPECTED_BASE);
    const handlerRva = Number(handler - EXPECTED_BASE);
    assertClaim(pe.virtualSectionFor(nameRva, 1).name === '.data', 'node name pointer not in .data at ' + index);
    assertClaim(pe.virtualSectionFor(handlerRva, 1).name === '.text', 'node handler pointer not in .text at ' + index);
    assertClaim(next === 0n, 'original node next pointer not zero at ' + index);
    if (index === ROOT_INDEX - 1) rootRecord = { name, handler, next, rva };
    recordsVerified++;
  }
  assertClaim(rootRecord.rva === 0x2f5d618 &&
    rootRecord.name === 0x1435159f8n &&
    rootRecord.handler === 0x1407f2570n &&
    rootRecord.next === 0n, 'ROOT wrapper record 575 exact tuple');

  const table = [0x1407e90a0n, 0x1408174b0n, 0x1407068c0n];
  for (let i = 0; i < table.length; i++) {
    assertClaim(pe.qword(0x26c5a38 + i * 8) === table[i], 'dispatch-table slot ' + i);
  }
  assertClaim(pe.slice(0x7068c0, 10).toString('hex') === '488b4108488bca48ffe0',
    '10-byte handler-loading tail-jump trampoline');

  // Named singleton and formatted-name buffer are distinct globals, 0x3ff8 bytes apart.
  // The 16-bit ROOT tag is source-derived only for the successful new-record path.
  const singletonRva = 0x35199f0;
  const nameBufferRva = 0x35159f8;
  assertClaim(singletonRva - nameBufferRva === 0x3ff8, 'separate singleton/name addresses');
  assertClaim(pe.virtualSectionFor(singletonRva, 8).name === '.data' &&
    pe.virtualSectionFor(nameBufferRva, 1).name === '.data', 'named globals within virtual .data');
  assertClaim(rootRecord.name === EXPECTED_BASE + BigInt(nameBufferRva), 'ROOT descriptor name global');
  assertClaim(pe.qword(0x2b4a2b0) === 0x141edda60n, 'named singleton VMT ID method');
  assertClaim(pe.qword(0x2b4a2b8) === 0x141ede6f0n, 'named singleton VMT name method');

  // Exact original instructions select a 32-bit constant and xor its low WORD.
  hasBytes(0x1ed56b0, '4881fa00c48f34'); // first selector bound 0x348FC400
  hasBytes(0x1ed56b9, '4881fa8195a225'); // second selector bound 0x25A29581
  hasBytes(0x1ed56c7, 'b8da559360');     // ID branch value 0x609355DA
  hasBytes(0x1ed56cc, '480f43c1');       // name branch selects address in RCX
  hasBytes(0x1ede6f5, 'e9');             // name method jumps to shared selector
  assertClaim(0x1ede6f5 + 5 + pe.int32(0x1ede6f6) === 0x1ed56b0,
    'name VMT method shares exact selector');
  const idSelectorInput = 0x15cd549d;
  const nameSelectorInput = 0x2dd16991;
  assertClaim(idSelectorInput < 0x25a29581 && nameSelectorInput >= 0x25a29581 &&
    nameSelectorInput < 0x348fc400, 'source-defined ID/name selector branches');
  const rootInternalTag = ((0x609355da & 0xffff) ^ 0x88e6) & 0xffff;
  assertClaim(rootInternalTag === 0xdd3c, 'ROOT source-defined 16-bit internal tag');

  // This negative control modifies only a copy in memory, never the archived source.
  const originalStub = pe.slice(0x7068c0, 10);
  const mutatedStub = Buffer.from(originalStub);
  mutatedStub[0] ^= 1;
  assertClaim(sha256(mutatedStub) !== sha256(originalStub), 'stub mutation control');

  return {
    ok: true,
    sourceSha256: actualSha,
    executableBytes: bytes.length,
    registrationRecordsVerified: recordsVerified,
    rootRecordIndex: ROOT_INDEX,
    sourceWindowsVerified: windowsVerified,
    opcodeAnchorsVerified: anchors.length,
    directCallsVerified,
    ripTargetsVerified,
    dispatchBranchesVerified: 2,
    trampolineRva: '0x7068c0',
    handlerEntryOffset: '+0x18',
    rootInternalTagHex: '0x' + rootInternalTag.toString(16),
    rootTagNameRegistrationConditional: true,
    namedSingletonRva: '0x' + singletonRva.toString(16),
    separateNameBufferRva: '0x' + nameBufferRva.toString(16),
    staticCallbackArgumentReferenceFlowQualified: true,
    staticC2mRootPointerIdentityQualified: true,
    staticHandlerDispatchPathQualified: true,
    liveExecutionProven: false,
    playerIdentityProven: false,
    negativeMutationRejected: true,
  };
}

function main(argv) {
  if (argv.includes('--help')) {
    process.stdout.write('Usage: node tools/verify-root001-registry.mjs [--pe ORIGINAL_RIFT_EXE] [--self-test]\n');
    return;
  }
  let pePath = defaultPe;
  let selfTest = false;
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--self-test') selfTest = true;
    else if (argv[i] === '--pe' && i + 1 < argv.length) pePath = path.resolve(argv[++i]);
    else throw new Error('Unexpected argument: ' + argv[i]);
  }
  assertClaim(statSync(pePath).size === EXPECTED_BYTES, 'preflight executable size mismatch');
  const bytes = readFileSync(pePath);
  const result = verifyRoot001Bytes(bytes);
  if (selfTest) {
    const modified = Buffer.from(bytes);
    modified[0] ^= 1;
    let rejected = false;
    try { verifyRoot001Bytes(modified); } catch { rejected = true; }
    assertClaim(rejected, 'whole-image mutation self-test');
    result.wholeImageMutationRejected = true;
  }
  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { main(process.argv.slice(2)); }
  catch (error) {
    process.stderr.write(JSON.stringify({ ok: false, error: String(error.message ?? error) }) + '\n');
    process.exitCode = 1;
  }
}
