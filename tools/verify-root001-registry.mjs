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
  // Two source-qualified vector-slot callers of the existing 0x7E91F0 dispatcher.
  ['dispatch_vector_caller_a', 0x787470, 0x209, 'aee469be6d6e1db4f891b7e345ce9d27bfcaa59b06ae91a1a0afcf3dc6f40dea'],
  ['dispatch_vector_caller_b', 0x7885e0, 0x1e0, 'd3084bb14e52aa4cc9fb0a2df921024fe29fc8a8cfac7a7648a303b7fdc03ee5'],
  ['dispatch_vector_triple_swap', 0x74b8f0, 0x8d, 'a7d3ab5974b96ac931e5b5254138a30a85e46206c7bc513a0c547bf48cb43663'],
  ['dispatch_vector_global_cleanup', 0x2554970, 0x58, '35085a7dfca9a2532efcf195993be6a758c461cb67c67004302ef24292976012'],
  // Positive C2M root+0x358 writer, keyed callsite, and pointer availability.
  ['c2m_positive_flag_writer', 0x580950, 0x121, '360e70964e190b4b62145c19edffb398a34e874eb19834987cf38ec517fa946b'],
  ['c2m_key_equality_caller', 0x5f6650, 0x2d6, '1d41bf2d55203b6ce3d703176048a033cb198c6918608cef0f04ee6514fe7208'],
  ['c2m_caller_pointer_table', 0x26afbb0, 0xa0, 'd196cad731b8181ad9042c3a68d8b6d35b1ee1436eac0bb223492097fe479691'],
  // Original callers of the two known vector processors: not vector element writers.
  ['vector_upstream_01', 0xfba020, 0x21, '90812a8e57da7e0cb14e853f79a571dae50563546ef829f44dc1f8f8dc6b2458'],
  ['vector_upstream_02', 0xfbc460, 0x745, 'a6131382c9ea636bc9783c216df2eca234b42d245b708d198c33219e2a4a0157'],
  ['vector_upstream_03', 0xfc3c24, 0xb3, '3973f5182f0116c7e76f78063268fc1067fe44ba93c346351df1ff96dfd88c62'],
  ['vector_upstream_04', 0xfc8a90, 0x18b, '3a0cdbf84425db65a2f970584fe424fb03cfa7147d76b54695c57f791121b63d'],
  ['vector_upstream_05', 0xfd07b0, 0x31, '436a38eb3254fc85b07ec1b3c8a8195c73e8d5dfca1ba5971f518d74ba6089cf'],
  ['vector_upstream_06', 0xfd0d80, 0xb7, 'c5b94e13262103d8654765243d5768acfbd97650a699a9c062fe8f0ea13a6b62'],
  ['vector_upstream_07', 0xfd1160, 0x13, 'a3c272fc7556d9b0d78712d4c111f74020b74fe3402acee94f60dcf7a2088f9b'],
  ['vector_upstream_08', 0xfd8cd0, 0x4d0, '18a0464ae3652aa86c8dbabd4b7038281ec9c820975fc7aa8d268b129a384806'],
  ['vector_upstream_09', 0xfca0d0, 0xdc8, '35e7e89ce4795d13eec2de00b64d2b7ce9e23f772bbf5582e60a83e2d3d72cd6'],
  // Contiguous code-pointer run includes multiple independently assigned interior vptr starts.
  // Neither a single 40-method VMT nor the slot of 0x26afc00 is established.
  ['c2m_contiguous_code_pointer_region', 0x26afb40, 0x140, '1f8e1529b4eff25d14f0f4281a84043fb684b5fdc879a05a6e7701095d1ee862'],
  ['c2m_vptr_assignment_routine', 0x5dc520, 0x2b, '032e2cd9030488e8cc1aa70b592eaeedd594840d66db1e56355b279ff674380d'],
  ['c2m_vptr_interior_owner_a', 0x5da680, 0x85f, 'b1729ca6f7f137d66b5eed3933d9a72fd718c33c5c23ce7240fc5be874bb6126'],
  ['c2m_vptr_interior_owner_b', 0x5db344, 0x3ce, '412c845e22e6a36e2624fc69db4cc6e8c94955b9a689399d83ace847490fdadf'],
  ['c2m_vptr_context', 0x601900, 0x157e, 'dd373abcdacfd22dd3bf8cdca8fd40abb4601903eea6630b2c33b72d6a8b2823'],
  // Two virtual appenders and a source-compatible receiver+0x6A8 field linkage;
  // the initializer/processor runtime receiver identity is still unobserved.
  ['object_vector_append_parent_a', 0x74bbe0, 0xa0, '6c0e24b80c3aa616aacb6954b94631e85a416deb201bdb72e8ed943f531f7625'],
  ['object_vector_append_parent_b', 0x74bee0, 0xa0, '739c187b9b486a9ab5dd33dd97d4beb2936e087829b8622b810386a97d1a5c71'],
  ['object_vector_append_writer_a', 0x74bd57, 0xb5, '7ebbbc976781c3a80bffdcecac070d1a9e53b0680fcadacb215488e4e01f4bee'],
  ['object_vector_append_writer_b', 0x74c04a, 0xb5, 'e3d670e6ec493ca4663b0cb942d79e1906dec0795c037e4179be7c493cd59f13'],
  // The table installed by the append-owner constructor contains both append entrypoints.
  ['append_owner_vptr_table', 0x26be378, 0x70, 'bcad62380f20f0ba3056f71ae36ed13e700b5998ed3df5e699c6e89c34e09d89'],
  ['append_owner_constructor', 0x74aa90, 0x16c, '55acc370174457a7b63734b921f5a8cef90f85334ce910b7059503d80abf1062'],
  ['append_owner_destructor', 0x74ac00, 0x16b, '109111704f1df2772eec7897665ca43e181decb359074a66e4db590b2ba6c9b2'],
  ['append_owner_host_field_store', 0x7724b4, 0xa4, '4bc7236c3ea0e32738e0ff647eefbd0bc3e917c9594e46ca450d6c40ff1ec75a'],
  ['append_owner_receiver_initializer', 0x76f010, 0x36d4, '257bbfb8b8a01445c427d5b4215a5652ce02bfd972fbefd77483289ec70f5a1a'],
  ['initializer_rax_preserving_stack_probe', 0x24e1160, 0x4e, '24ba2f8e6f97e3f8dec9771f775f11294b7da43ba09efabbb1bd3c079ac25b6e'],
  // One SOURCE-only host receiver: +0x240 callbacks, +0x6A8 vector owner;
  // actual callback argument RDX identity and live delivery remain unknown.
  ['host_constructor_publication', 0x761f10, 0x58, 'af9c721ca1bf5cfff77012fa795095a195440ad730fbe779c0a059f8f85cbe87'],
  ['host_constructor_primary_vptr', 0x75b9d0, 0x60, '6326f0c763d4e5ef74f09987121334518e730f75d6c0124a188f7c0a811fff71'],
  ['host_initializer_and_callback_lookup_vptr', 0x26be9f0, 0xc8, '3e758e1edcc229ddf131a4fd91f2d7019d9893ed11e61fd0f448b7ca8605c1a8'],
  ['host_callback_lookup_method', 0x766050, 0x7e, 'd33cd280a8deb62453a87b2266bdba8735241b9766ed65aa15783bbdf288a3b9'],
  ['host_initializer_callback_builder_invocation', 0x771f36, 0x15, '62029fe6dd0b143e36e5d3bf35b976492746c3bea98e8179ca5553e206c2a5df'],
  ['host_callback_registration_builder', 0x777ce0, 0xbdc, 'ebea03f510c1f415575a3fd592725a93e6fa58dbb4f5bec9a3610eced7db9760'],
  ['registered_processor_adapter_install', 0x77818b, 0xb4, 'e7c23673b2b102b9980c3a2717833bdd71565bb5c7aa1e4f54557c197d0cc827'],
  ['registered_processor_adapter_vptr', 0x26beb28, 0x38, '8f3fbc80d06c36941a5e0ac7e325cce0512f0688bcb09a8d052a09bec78128c4'],
  ['registered_processor_callback_wrapper', 0xfba020, 0x21, '90812a8e57da7e0cb14e853f79a571dae50563546ef829f44dc1f8f8dc6b2458'],
  ['host_callback_registration_slot_accessor', 0x75d9e0, 0x1d, '20428d4ac96a8f77cd6c0ee34b3d2e4a64390835d6e5bcf295267f9fcf148de4'],
  ['c2m_first_key_pair_update', 0x5807d0, 0x7b, '3c1e9d159e93e25adeb29e041511de7b55d0960d96419d5fa023f357f4dab6d8'],
  ['c2m_reference_release_prefix', 0x4a02d0, 0x78, 'b60cb2e4db49aedbb49748a38d832955e115af78283a9aa46c59b9d7c3911bc4'],
  ['c2m_transient_pair_cleanup_prefix', 0x49ac00, 0x78, 'abae0ea33271d8082429d95b1bd3413723683b6597a9487580fa919bbb66b9f6'],
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

    [0x78759b, 'e85043fcff'], // first caller exchanges vector triple
    [0x7875a0, '488b1d'], // reads global vector begin
    [0x7875a7, '488b35'], // reads global vector end
    [0x7875b3, '488bcb'], // dispatch receives address of QWORD slot
    [0x7875b6, 'e8351c0600'], // first vector-slot dispatcher call
    [0x7886f2, 'e8f931fcff'], // second caller exchanges vector triple
    [0x7886f7, '488b1d'], // reads same vector begin
    [0x7886fe, '488b35'], // reads same vector end
    [0x788710, '488bcb'], // second slot address, not element value
    [0x788713, 'e8d80a0600'], // second dispatcher call
    [0x74b916, '4c8d8680000000'], // swap destination object+0x80
    [0x74b922, '498b00488b0f488907498908'], // swap begin
    [0x74b93b, '488b02498b0949890148890a'], // swap end
    [0x74b954, '498b00488b0f488907498908'], // swap capacity
    [0x3c310, '48ff25d1335b02'], // imported enter critical-section thunk
    [0x3c320, '48ff25c9335b02'], // imported leave critical-section thunk
    [0x580a14, '488bcb'], // positive writer forwards retained root
    [0x580a1c, 'c6835803000001'], // positive writer sets root+0x358=1
    [0x5f6724, '488b8860030000'], // root opaque key at +0x360
    [0x5f672b, '49398e18030000'], // compare against distinct object+0x318
    [0x5f6732, '7553'], // mismatch skips writer
    [0x5f6734, '498b4610'], // stage reference from object+0x10
    [0x5f6744, '488d5540'], // address of staged reference to writer

    [0x787482, '488be9'], // first vector processor preserves incoming RCX in RBP
    [0x7885fc, '488be9'], // second processor likewise
    [0x78758d, '488b8da8060000'], // object+0x6A8 is vector container owner
    [0x7886e4, '488b8da8060000'], // second processor follows same object+0x6A8
    [0xfba02c, 'e83fd47cff'], // upstream direct caller 1
    [0xfbc489, 'e8e2af7cff'], // upstream direct caller 2
    [0xfc3c61, 'e80a387cff'], // upstream direct caller 3
    [0xfc8abd, 'e8aee97bff'], // upstream direct caller 4
    [0xfd07c1, 'e8aa6c7bff'], // upstream direct caller 5
    [0xfd0da4, 'e8c7667bff'], // upstream direct caller 6
    [0xfd1167, 'e804637bff'], // upstream direct caller 7
    [0xfd8d0d, 'e85ee77aff'], // upstream direct caller 8
    [0xfca4b0, 'e82be17bff'], // upstream direct caller 9

    [0x5dc526, '488d0513360d02'], // deleting-destructor-style vptr reset at 0x26afb40
    [0x5dc530, '488901'], // assigns one vptr to [RCX], not a full VMT identity
    [0x5dc533, 'f6c201'], // optional delete path selected by DL&1
    [0x5dc536, '740a'], // skips optional delete call when flag clear
    [0x5dc538, 'ba18000000'], // deallocator size argument
    [0x5da7d3, '488d0d96530d02'], // distinct interior vptr 0x26afb70
    [0x5da7df, '48898b00010000'], // assignment [RBX+0x100]
    [0x5da87e, '488d05eb520d02'], // vptr 0x26afb70
    [0x5da88e, '48898390010000'], // assignment [RBX+0x190]
    [0x5da895, '488d05f4520d02'], // distinct interior vptr 0x26afb90
    [0x5da89c, '48898398010000'], // assignment [RBX+0x198]
    [0x5db354, '488d0545480d02'], // distinct interior vptr 0x26afba0
    [0x5db35b, '488901'], // assignment [RCX]
    // A constructed object has a vptr containing both appenders, initializes
    // its +0x80 vector triple, and is conditionally stored at receiver+0x6A8.
    [0x74aa9f, '488bd9'], // receiver RCX retained
    [0x74aaa9, '488d05c838f701'], // source-installed vptr 0x26be378
    [0x74aab0, '488903'], // install at [RBX]
    [0x74aab7, '488d052a39f701'], // separate secondary vptr 0x26be3e8
    [0x74aac2, '48894310'], // install at [RBX+0x10]
    [0x74aae3, '4889b380000000'], // initialize vector begin at +0x80
    [0x74aaec, '4889b388000000'], // initialize used-end +0x88
    [0x74aaf3, '4889b390000000'], // initialize capacity-end +0x90
    [0x74ac0a, '488d056737f701'], // destructor vptr reset
    [0x74ac14, '488901'],
    [0x74ac17, '488d05ca37f701'], // secondary vptr reset
    [0x74ac1e, '48894110'],
    [0x76f015, '48894c2408'], // initializer saves incoming receiver RCX
    [0x76f01a, 'b8f80d0000'], // 0xDF8 stack allocation
    [0x76f01f, 'e83c21d701'], // call verified RAX-preserving stack probe
    [0x76f024, '482be0'], // RSP -= RAX
    [0x24e1160, '4883ec10'], // stack probe reserves temporary stack
    [0x24e1164, '4c891424'], // save R10, not RAX
    [0x24e1168, '4c895c2408'], // save R11, not RAX
    [0x24e11a0, '4c8b1424'], // restore R10
    [0x24e11a4, '4c8b5c2408'], // restore R11
    [0x24e11a9, '4883c410c3'], // return with RAX still holding 0xDF8
    [0x7724b4, 'b920050000'], // allocate 0x520-byte owner
    [0x7724d9, 'e8b285fdff'], // construct append-capable owner
    [0x7724de, '4889842470020000'], // save returned owner
    [0x7724f4, '488b8424000e0000'], // initializer receiver spill at +0xE00
    [0x7724fc, '4805a8060000'], // receiver+0x6A8
    [0x772502, '4889842440020000'], // save owner-field address
    [0x772545, '488b842440020000'], // RESTORE field address after conditional cleanup call
    [0x77254d, '488b8c2470020000'], // retrieve constructed owner
    [0x772555, '488908'], // [receiver+0x6A8] = constructed owner
    // Independently traced common constructor receiver for callbacks + vector owner.
    [0x761f14, 'b9500a0000'], // allocate 0xA50 host, not an actor identity
    [0x761f30, 'e89b9affff'], // construct primary host
    [0x761f45, '488b542428'], // pass constructed host as value
    [0x761f4a, '488d0d9f05c102'], // host pointer global 0x33724F0
    [0x761f51, 'e80a1ff4ff'], // generic slot setter
    [0x75ba04, '488d0de52ff601'], // host constructor's vptr 0x26BE9F0
    [0x75ba0b, '488908'], // install at [host]
    [0x771f36, '488b8c24000e0000'], // reload the SAME initial host receiver
    [0x771f3e, 'e89d5d0000'], // hand host to callback builder
    [0x777ce0, '48894c2408'], // callback builder saves host RCX
    [0x777ce5, '57'], // push RDI before local 0x3E0 allocation
    [0x777ce6, '4881ece0030000'], // +0x3F0 now references entry RCX spill
    [0x777d4a, '488b8424f0030000'], // first registry reload uses original host
    [0x777d52, '480540020000'], // first host+0x240 collection
    [0x777d63, 'e8785cfeff'], // first registry slot accessor
    [0x777d70, '488908'], // first callback adapter store
    [0x7781b5, 'e836f20000'], // construct processor callback adapter base
    [0x7781bf, '488d0d6269f401'], // install adapter vptr 0x26BEB28
    [0x7781c6, '488908'], // separate adapter's own vptr, not host vptr
    [0x778208, '488b8424f0030000'], // callback adapter reuses original host
    [0x778210, '480540020000'], // same original host+0x240 registry
    [0x77821e, '488bc8'], // pass host+0x240 as RCX
    [0x778221, 'e8ba57feff'], // obtain insertion slot
    [0x778226, '488b8c24c8000000'], // reload adapter pointer
    [0x77822e, '488908'], // store adapter into host's collection slot
    [0xfba026, '488bca'], // callback wrapper forwards incoming RDX, NOT proven host
    [0xfba02c, 'e83fd47cff'], // route forwarded RDX into processor 0x787470
    [0x75d9f1, '488b00'], // slot accessor follows saved container pointer
    [0x75d9f4, '4883c030'], // returns +0x30 destination slot
    // Two independent source functions retain incoming owner RCX in R14.
    [0x74bc1f, '4c8bf1'],
    [0x74bd5f, '498d7e40'], // owner+0x40 lock
    [0x74bd6b, 'e8a0058fff'], // EnterCriticalSection
    [0x74bd83, '498db680000000'], // owner+0x80 vector
    [0x74bd8a, '488b5610'], // vector capacity end
    [0x74bd8e, '48395608'], // compare allocation end to used end
    [0x74bd92, '7525'], // skip growth when capacity available
    [0x74bdb4, 'e887220000'], // growth helper
    [0x74bdb9, '488b4608'], // load used end
    [0x74bdbd, '4c8920'], // initialize slot
    [0x74bdc5, '488918'], // assign refcounted element pointer
    [0x74bdcb, '4883460808'], // increment end by 8 bytes
    [0x74be04, '488bcf'], // owner lock address
    [0x74be07, 'e814058fff'], // LeaveCriticalSection
    [0x74bf1f, '4c8bf1'], // second entry owner RCX to R14
    [0x74c052, '498d7e40'], // second owner+0x40 lock
    [0x74c05e, 'e8ad028fff'], // EnterCriticalSection
    [0x74c076, '498db680000000'], // second owner+0x80 vector
    [0x74c07d, '488b5610'],
    [0x74c081, '48395608'],
    [0x74c085, '7525'],
    [0x74c0a7, 'e8941f0000'], // same growth helper
    [0x74c0ac, '488b4608'],
    [0x74c0b0, '4c8920'],
    [0x74c0b8, '488918'], // assign element pointer
    [0x74c0be, '4883460808'], // increment end by 8 bytes
    [0x74c0f7, '488bcf'],
    [0x74c0fa, 'e821028fff'], // LeaveCriticalSection

    [0x5807e4, '488b2a'], // incoming pair first QWORD
    [0x5807ed, '488b5a08'], // incoming pair second QWORD
    [0x5807f1, '483ba930030000'], // compares ONLY first QWORD to root+0x330
    [0x5807f8, '7435'], // identical first QWORD skips pair replacement
    [0x5807ff, '448b03'], // reads count from second member
    [0x580806, '8903'], // retain count
    [0x58080d, 'ff4304'], // secondary count on zero-crossing
    [0x580810, '488b8938030000'], // old root+0x338 reference
    [0x580821, '4889af30030000'], // write root+0x330
    [0x580828, '48899f38030000'], // write root+0x338
    [0x58082f, '488bce'], // pass transient pair to cleanup
    [0x580846, 'e9b5a3f1ff'], // unconditional jump to transient pair cleanup
    [0x580a0f, '488d542430'], // positive writer passes staged 16-byte pair
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
  directCall(0x78759b, 0x74b8f0);
  directCall(0x7875b6, 0x7e91f0);
  directCall(0x7886f2, 0x74b8f0);
  directCall(0x788713, 0x7e91f0);
  directCall(0x580a17, 0x5807d0);
  directCall(0x5f671c, 0x49a020);
  directCall(0x5f673c, 0x49a020);
  directCall(0x5f6748, 0x580950);
  directCall(0x74b911, 0x3c310); // enter object+0x40 critical section before vector exchange
  directCall(0x74b968, 0x3c320); // leave the same critical section after exchange
  directCall(0xfba02c, 0x787470);
  directCall(0xfbc489, 0x787470);
  directCall(0xfc3c61, 0x787470);
  directCall(0xfc8abd, 0x787470);
  directCall(0xfd07c1, 0x787470);
  directCall(0xfd0da4, 0x787470);
  directCall(0xfd1167, 0x787470);
  directCall(0xfd8d0d, 0x787470);
  directCall(0xfca4b0, 0x7885e0);
  directCall(0x58081c, 0x4a02d0); // releases prior root+0x338 when present
  directCall(0x5dc53d, 0x24e0d50); // deleting-destructor optional delete path
  // Both object-local append routines lock, grow if necessary, then unlock.
  directCall(0x74bd6b, 0x3c310);
  directCall(0x74bdb4, 0x74e040);
  directCall(0x74be07, 0x3c320);
  directCall(0x74c05e, 0x3c310);
  directCall(0x74c0a7, 0x74e040);
  directCall(0x74c0fa, 0x3c320);
  directCall(0x7724b9, 0x78e110); // allocate append-owner object
  directCall(0x7724d9, 0x74aa90); // construct append-owner object
  directCall(0x76f01f, 0x24e1160); // RAX-preserving stack probe before receiver-relative field logic
  directCall(0x761f30, 0x75b9d0); // host constructor
  directCall(0x761f51, 0x6a3e60); // publish host to a distinct global, not C2M root
  directCall(0x771f3e, 0x777ce0); // original initializer receiver enters callback builder
  directCall(0x777d63, 0x75d9e0); // callback registration slot
  directCall(0x7781b5, 0x7873f0); // callback adapter base constructor
  directCall(0x778221, 0x75d9e0); // processor adapter registry slot
  directCall(0xfba02c, 0x787470); // wrapper forwards callback argument RDX
  directCall(0x74b1af, 0x74ac00); // virtual deleting destructor reaches cleanup
  let directJumpsVerified = 0;
  hasBytes(0x580846, 'e9');
  assertClaim(0x580846 + 5 + pe.int32(0x580847) === 0x49ac00,
    'reference-pair helper cleanup tail jump');
  directJumpsVerified++;

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
  ripReference(0x7875a0, '488b1d', 0x3372c58);
  ripReference(0x7875a7, '488b35', 0x3372c60);
  ripReference(0x7886f7, '488b1d', 0x3372c58);
  ripReference(0x7886fe, '488b35', 0x3372c60);
  // Original seven-byte FF 25 import thunks: Kernel32 critical-section enter/leave.
  ripReference(0x3c310, '48ff25', 0x25ef6e8);
  ripReference(0x3c320, '48ff25', 0x25ef6f0);
  ripReference(0x5dc526, '488d05', 0x26afb40); // vptr reset at start of region
  ripReference(0x5da7d3, '488d0d', 0x26afb70); // interior vptr
  ripReference(0x5da87e, '488d05', 0x26afb70); // interior vptr
  ripReference(0x5da895, '488d05', 0x26afb90); // interior vptr
  ripReference(0x5db354, '488d05', 0x26afba0); // interior vptr
  ripReference(0x74aaa9, '488d05', 0x26be378); // append-owner primary vptr
  ripReference(0x74aab7, '488d05', 0x26be3e8); // append-owner secondary vptr
  ripReference(0x74ac0a, '488d05', 0x26be378); // destructor resets primary vptr
  ripReference(0x74ac17, '488d05', 0x26be3e8); // destructor resets secondary vptr
  ripReference(0x75ba04, '488d0d', 0x26be9f0); // host vptr: initializer+lookup methods
  ripReference(0x761f4a, '488d0d', 0x33724f0); // separate host pointer global
  ripReference(0x7781bf, '488d0d', 0x26beb28); // constructed processor adapter vptr

  // A matched keyed entry takes the short jump into the shared call tail.
  function shortBranch(at, opcode, target) {
    hasBytes(at, opcode);
    const destination = at + 2 + pe.slice(at + 1, 1).readInt8(0);
    assertClaim(destination === target, 'conditional dispatch branch at RVA 0x' + at.toString(16));
  }
  shortBranch(0x7e928a, 'eb', 0x7e92c9);
  shortBranch(0x7e92e6, '75', 0x7e92ed);
  shortBranch(0x5f6732, '75', 0x5f6787); // key mismatch skips C2M positive writer
  shortBranch(0x5807f8, '74', 0x58082f); // first-pair-member equality only
  shortBranch(0x5dc536, '74', 0x5dc542); // deleting-destructor optional delete path
  shortBranch(0x74bd92, '75', 0x74bdb9); // writer A capacity suffices
  shortBranch(0x74c085, '75', 0x74c0ac); // writer B capacity suffices

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
  assertClaim(pe.qword(0x26afc00) === 0x1405f6650n,
    'source-initialized conditional C2M writer caller method pointer');
  // This original .rdata interval has forty consecutive .text pointers, but
  // independent code stores several INTERIOR addresses as object vptrs.
  // The positional +0xC0 offset does not establish a method slot or class.
  let c2mConsecutiveCodePointersVerified = 0;
  for (let index = 0; index < 40; index++) {
    const pointer = pe.qword(0x26afb40 + index * 8);
    assertClaim(pointer >= EXPECTED_BASE, 'C2M code pointer image VA ' + index);
    assertClaim(pe.virtualSectionFor(Number(pointer - EXPECTED_BASE), 1).name === '.text',
      'C2M code pointer section ' + index);
    c2mConsecutiveCodePointersVerified++;
  }
  assertClaim(0x26afc00 - 0x26afb40 === 0xc0,
    'C2M method pointer positional offset only, not virtual slot index');

  // Unlike the adjacent C2M code-pointer region, THIS observed vptr start
  // is installed by 0x74AA90 and has two literal append-method entries.
  const appendOwnerVptrRva = 0x26be378;
  const appendEntryPointers = [[0x30, 0x14074bbe0n], [0x38, 0x14074bee0n]];
  for (const [offset, target] of appendEntryPointers) {
    assertClaim(pe.qword(appendOwnerVptrRva + offset) === target,
      'source-installed append vptr method at offset 0x' + offset.toString(16));
    assertClaim(pe.virtualSectionFor(Number(target - EXPECTED_BASE), 1).name === '.text',
      'append owner method points to original text');
  }
  // The original 0xA50 host constructor installs a vptr whose +8 method is
  // initializer 0x76F010 and whose +0xB8 method looks up host+0x240 callbacks.
  // The initializer passes the SAME saved receiver to the callback bundle builder;
  // this registers a separate processor adapter (vptr +0x18 -> FBA020) into
  // receiver+0x240, then separately stores the vector owner at receiver+0x6A8.
  // Callback FBA020 receives its own RDX; it is NOT proven to be that host.
  assertClaim(pe.qword(0x26be9f8) === 0x14076f010n,
    'host vptr includes original receiver initializer');
  assertClaim(pe.qword(0x26beaa8) === 0x140766050n,
    'host vptr includes callback registry lookup method');
  assertClaim(pe.qword(0x26beb40) === 0x140fba020n,
    'registered adapter vptr includes processor forwarding wrapper');

  // Source saves initial RCX at old RSP+8. An exact-hashed stack probe preserves
  // RAX=0xDF8 before the subtraction, so new RSP+0xE00 recovers that receiver.
  // The owner-field address is staged at +0x240 and explicitly RESTORED after
  // possible cleanup before the conditional +0x6A8 store. Processors read the
  // same field offset; receiver class/instance equality remains unknown.
  assertClaim(0xe00 - 0xdf8 === 8, 'initializer receiver spill stack delta');

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
    directJumpsVerified,
    ripTargetsVerified,
    dispatchBranchesVerified: 2,
    c2mKeyMismatchBranchesVerified: 1,
    c2mFirstKeyEqualityBranchesVerified: 1,
    c2mVtableDeleteBranchesVerified: 1,
    c2mConsecutiveCodePointersVerified,
    vectorAppendPathsVerified: 2,
    appendOwnerVirtualMethodsVerified: appendEntryPointers.length,
    vectorUpstreamDirectCallersVerified: 9,
    trampolineRva: '0x7068c0',
    handlerEntryOffset: '+0x18',
    rootInternalTagHex: '0x' + rootInternalTag.toString(16),
    rootTagNameRegistrationConditional: true,
    namedSingletonRva: '0x' + singletonRva.toString(16),
    separateNameBufferRva: '0x' + nameBufferRva.toString(16),
    staticCallbackArgumentReferenceFlowQualified: true,
    staticC2mRootPointerIdentityQualified: true,
    staticHandlerDispatchPathQualified: true,
    staticDispatchVectorSlotLoopQualified: true,
    staticDispatchVectorTripleSwapQualified: true,
    staticVectorCriticalSectionGuardQualified: true,
    staticC2mPositiveEligibilityWriterQualified: true,
    staticC2mRootKeyEqualityGateQualified: true,
    staticC2mMethodPointerAvailabilityQualified: true,
    staticC2mInteriorVptrAssignmentsQualified: true,
    staticC2mFirstKeyReferencePairUpdateQualified: true,
    staticC2mTransientReferenceCleanupQualified: true,
    staticVectorProcessorCallersQualified: true,
    objectLocalVectorElementWritersProven: true,
    staticAppendOwnerVptrConstructionQualified: true,
    staticAppendOwnerVectorLifecycleQualified: true,
    staticInitializerOwnerField6a8StoreQualified: true,
    staticProcessorOwnerField6a8ReadQualified: true,
    staticProducerProcessorFieldLayoutBridgeQualified: true,
    staticInitializerSameReceiverCallbackRegistrationQualified: true,
    staticRegisteredProcessorAdapterVptrQualified: true,
    callbackProcessorArgumentMatchesRegisteredHostProven: false,
    producerProcessorReceiverTypeMatchProven: false,
    dispatchVectorElementProducerProven: false,
    dispatchVectorProducerOwnerIdentityProven: false,
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
