#!/usr/bin/env node
// Read-only RIFT known-ability section reconciliation; never infers role slot or unlock.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {fileURLToPath} from "node:url";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const CROSSWALK="docs/REA-RIFT-SPELLCASTING-SC103-EXACT-ID-CROSSWALK-2026-11-02.json";
const CROSSWALK_SHA="00c1cc8896591bd2c7dfedf0a831f689179fbfb0ac5369dcc63cfcf8b5ec79f5";
const UI_REPORT="docs/REA-RIFT-SPELLCASTING-SC102-UI-SPELLDUMP-2026-11-02.md";
const UI_SHA="67f0d6387c0332a096be61c2defdc69797ef05921692445fa2b61b4da7d709ab";
const refs={
 General:[["2026-11-01_194717.jpg","bf6112e247498280e7a30e370819e146cce0afcfa5c7afa7707d63891ef09a97"]],
 Role:[["2026-11-01_194747.jpg","b83df11be25c5b5dedab89364efabb1ba25cc59012b57abffd0cf6a327703db1"]],
 "Ascended Powers":[["2026-11-01_194748.jpg","fc3c25be59c87bb154b6892b433f6cc5e389ab9bfd0bf9080c421019657f0905"]],
 "Patron Abilities":[
 ["2026-11-01_194756.jpg","ad3c26302cb9a7765762d00fa2709693fe3cbbd4397d2cbc30a6634e94a85ff5"],
 ["2026-11-01_194801.jpg","a855f2d5b184532e68d27b82df8c8d85cf800c87e732f4c88358df3ff2ae40e6"],
 ["2026-11-01_194803.jpg","15e1ef5fc4fdb6cb68f2375372a426a80209ce495eaa6fcde06beed2457ee22c"]
 ]
};
const nameGroups={
 General:["Legacy of the Shade","Motivational Roar","Recycle","Soul Recall","Toggle Auto Attack","Toggle Ranged Attack","Track Fish"],
 Role:["Changing Role"],
 "Ascended Powers":["Ascended Resurrection","Break Free","Fury of the Ascended","Nexus Infusion","Planar Lure"],
 "Patron Abilities":["Bonus Dungeon Charges","Bonus Warfront Charges","Experience Bonus Suppression",
 "Patron's Artifact Tracking","Patron's Fast Pass","Patron's Mailbox","Patron's Radiance",
 "Summon Banker","Summon Cleric Trainer","Summon Guild Banker","Summon Mage Trainer",
 "Summon Primalist Trainer","Summon Rogue Trainer","Summon Warrior Trainer"]
};
const id=/^A[0-9A-F]{16}$/;
function check(yes,why){if(!yes)throw new Error(why);}
function sha(b){return crypto.createHash("sha256").update(b).digest("hex");}
function checkedBytes(p,expected){
 const b=fs.readFileSync(path.join(root,p));
 check(sha(b)===expected,"Source evidence changed: "+p);return b;
}
export function buildSectionMap(x){
 check(x.schemaVersion===1&&x.knownCaptureComplete===true&&
   x.counts?.knownApi===69&&x.counts?.staticCandidates===96&&
   x.counts?.staticKnown===39&&x.counts?.knownOutsideStatic===30,
 "Unexpected accepted catalog scope");
 const named=new Map();
 for(const [section,names] of Object.entries(nameGroups)){
  for(const n of names){check(!named.has(n),"Duplicate classification: "+n);named.set(n,section);}
 }
 const known=[],allIds=new Set();
 for(const r of x.staticCandidates){
  if(!r.listedInSavedCurrent)continue;
  check(id.test(r.id)&&!allIds.has(r.id)&&r.currentDetail?.lookupId===r.id,"Invalid static known ID");
  allIds.add(r.id);
  known.push({id:r.id,name:r.name,section:r.soul,
   association:"exact static soul ID; matching spellbook tab exists",
   roleSlot:null,sourceCategory:r.category});
 }
 for(const r of x.knownOutsideStatic){
  const name=r.currentDetail?.name;
  check(id.test(r.id)&&!allIds.has(r.id)&&named.has(name),"Unclassified outside ID: "+r.id+" / "+name);
  allIds.add(r.id);
  const section=named.get(name);
  known.push({id:r.id,name,section,roleSlot:null,
   association:section==="Role"?
    "role-changing API family / four UI role entries; exact ID-to-slot mapping unknown":
    "exact display name aligned to saved UI section; screenshot contains no stable ID"});
 }
 check(known.length===69&&allIds.size===69,"Known API ID count not 69");
 const sections={};
 for(const name of ["Paladin","VoidKnight","Paragon","General","Role","Ascended Powers","Patron Abilities"]){
  sections[name]=known.filter(r=>r.section===name).length;
 }
 const wanted={Paladin:28,VoidKnight:7,Paragon:4,General:7,Role:4,
  "Ascended Powers":5,"Patron Abilities":14};
 for(const [k,v] of Object.entries(wanted))check(sections[k]===v,"Unexpected section count: "+k);
 check(known.filter(r=>r.name==="Changing Role").length===4 &&
  known.filter(r=>r.name==="Changing Role").every(r=>r.roleSlot===null),
 "Changing Role homonyms cannot be slot-mapped");
 known.sort((a,b)=>a.section.localeCompare(b.section)||
  a.name.localeCompare(b.name)||a.id.localeCompare(b.id));
 return {schemaVersion:1,taskId:"RC-11 / SC-103",
  evidenceScope:"current-known 69 source-section reconciliation; not role-slot/learnability proof",
  origin:{
   currentKnownCrosswalk:{path:CROSSWALK,sha256:CROSSWALK_SHA},
   spellbookScreenshotAudit:{path:UI_REPORT,sha256:UI_SHA},
   screenshotFiles:Object.entries(refs).flatMap(([section,files])=>
    files.map(([filename,sha256])=>({section,filename,sha256,
    method:"source-hash checked host original; no stable ability ID visible"})))
  },
  counts:{knownApi:69,staticSoulExactId:39,outsideStaticNameAssociated:30,
   currentlyNotKnownStaticCandidates:57,bySection:sections},
  knownSections:known,
  limitations:[
   "UI screenshots show category/name, not the modern exact ID; non-soul section attribution is a name association",
   "Four Changing Role IDs cannot be assigned to four role-slot names or ordering",
   "Source soul ID does not by itself identify rank, variant, required points or learned eligibility",
   "57 absent static IDs remain unknown, not explicitly locked or unlearnable",
   "No character/gameplay input, SavedVariables recapture or current GCD measurement"
  ]};
}
export function buildFromPinned(){
 const bytes=checkedBytes(CROSSWALK,CROSSWALK_SHA);
 checkedBytes(UI_REPORT,UI_SHA);
 return buildSectionMap(JSON.parse(bytes.toString("utf8")));
}
const invoked=process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){try{process.stdout.write(JSON.stringify(buildFromPinned(),null,2)+"\n");}
catch(e){process.stderr.write("Section reconciliation failed: "+e.message+"\n");process.exitCode=1;}}
