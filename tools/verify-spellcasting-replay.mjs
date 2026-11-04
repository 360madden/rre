import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {replay,buildReplay} from "./replay-spellcasting-evidence.mjs";

const source = name => JSON.parse(fs.readFileSync(new URL("../docs/" + name,import.meta.url),"utf8"));
const originals = () => [
 source("REA-RIFT-SPELLCASTING-SC604-INTERIM-MECHANISM-2026-11-01.json"),
 source("REA-RIFT-SPELLCASTING-SC103-WARRIOR-STATIC-ABILITIES-2026-11-02.json"),
 source("REA-RIFT-SPELLCASTING-SC103-EXACT-ID-CROSSWALK-2026-11-02.json"),
 source("REA-RIFT-SPELLCASTING-SC502-EVENT-ATTRIBUTION-2026-11-01.json")
];
test("source-hashed replay is deterministic and contains no raw unit identifiers",()=>{
 const a=replay(),b=replay();assert.deepEqual(a,b);
 assert.equal(a.abilityIndex.static.length,96);
 assert.equal(a.abilityIndex.knownOutsideStatic.length,30);
 assert.equal(a.abilityIndex.knownApi,69);
 assert.equal(a.outcomes.historicalRangedTrials[0].selectedTargetDodges,1);
 assert.equal(a.outcomes.historicalRangedTrials[1].selectedTargetDamage,402);
 assert.equal(a.outcomes.historicalRangedTrials[1].otherTargetAbilityDamage,726);
 assert.equal(a.sourceManifest.indexed.length,14);
 assert.doesNotMatch(JSON.stringify(a),/u[0-9A-F]{16}/);
 assert.doesNotMatch(JSON.stringify(a),/"playerId"|"targetId"|"selectedTargetId"|"stats"/);
});
test("mixed original-client and old-event build is rejected",()=>{
 const args=originals();args[3].sourceBuildSha256=args[0].latestOriginalLocalExecutableSha256;
 assert.throws(()=>buildReplay(...args),/Historical\/current build mixed/);
});
test("crosswalk identity mutation and outcome reinterpretation fail closed",()=>{
 const idMut=originals();idMut[2].staticCandidates[0].id="A0000000000000000";
 assert.throws(()=>buildReplay(...idMut),/Static\/crosswalk mismatch/);
 const outMut=originals();outMut[3].rangedTrials[1].classification.selectedTargetDamage=0;
 assert.throws(()=>buildReplay(...outMut),/Attribution mismatch/);
});

test("direct buildReplay rejects noncanonical source-index paths and malformed digests",()=>{
  const badPaths=["../private.txt","C:\\private\\account.txt","docs/../private.txt","docs//report.json","docs/./report.json"];
  for(const badPath of badPaths){
    const args=originals();Object.values(args[0].sourceIndex)[0].path=badPath;
    assert.throws(()=>buildReplay(...args),/Unsafe source-index entry/);
  }
  const badSha=originals();Object.values(badSha[0].sourceIndex)[0].sha256="not-a-sha256";
  assert.throws(()=>buildReplay(...badSha),/Unsafe source-index entry/);
  const disguised=originals();Object.values(disguised[0].sourceIndex)[0].sha256={toString:()=>"a".repeat(64),privateToken:"not-for-export"};
  assert.throws(()=>buildReplay(...disguised),/Unsafe source-index entry/);
  const dupPath=originals();const entries=Object.values(dupPath[0].sourceIndex);entries[1].path=entries[0].path;
  assert.throws(()=>buildReplay(...dupPath),/Unsafe source-index entry/);
});
