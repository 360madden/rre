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
