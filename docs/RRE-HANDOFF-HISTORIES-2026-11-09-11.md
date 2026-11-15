# RRE dual-host session handoffs — November 9–11, 2026

**Reconciled:** November 15, 2026 (America/New_York). **Purpose:** retain both RRE research histories from AMD-DESKTOP and LEGION without mixing machine-specific evidence, timestamps, or historical stop/status directives.

During the merge, the local AMD-DESKTOP lineage (`1c28393952ef3be803af6b8a7ac251c1abcce720`) and the GitHub/LEGION lineage (`2b1c8d6`, fetched `origin/main`) each had independent handoffs for November 9, 10, and 11.

To preserve existing links from LEGION research reports, the original unsuffixed filenames retain the complete **LEGION** texts. The **AMD-DESKTOP** texts are preserved byte-for-byte in new machine-suffixed files, verified against the original Git blob IDs. Neither text supersedes the other.

| Date | AMD-DESKTOP original (preserved) | LEGION original (existing filename) | Primary evidence |
| --- | --- | --- | --- |
| Nov 9 | [AMD-DESKTOP](REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-09-AMD-DESKTOP.md) | [LEGION](REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-09.md) | AMD SC-625 / SC-306; LEGION localization and physical RIFT research |
| Nov 10 | [AMD-DESKTOP](REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-10-AMD-DESKTOP.md) | [LEGION](REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-10.md) | AMD SC-103 / SC-604 / queue evidence; LEGION collector releases and tests |
| Nov 11 | [AMD-DESKTOP](REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-11-AMD-DESKTOP.md) | [LEGION](REA-RIFT-SPELLCASTING-SESSION-HANDOFF-2026-11-11.md) | AMD ROOT-001 / RC-30; LEGION RC-75–88 and historical STOP receipt |

## Original Git blob verification

| Date | AMD-DESKTOP original blob = preserved file | LEGION original blob = restored canonical file |
| --- | --- | --- |
| Nov 9 | `79a9fd7b12b2753550896931d7bfc5a2bbac1190` | `40ecb02d26a066958ebc35b2648debbe027a00af` |
| Nov 10 | `f63542ec7a8aa9aadfd484993130df498fc9510f` | `24a06ff2f708a846203fc8fcca5d27613c83ee15` |
| Nov 11 | `ca7290d7d387b4a7bd732c37c183cd627e08ca5b` | `668ce634785f869f5cba2ae52f96d784d9e7c103` |

**Historical provenance:** The LEGION November 11 file begins with a STOP recorded on that day; this is part of the preserved historical session, not permission to alter present tasks. Use the latest dated AMD-DESKTOP session handoff (November 15) and current user instructions for new work.

**Related merge resolution:** The SC-306 evidence report retains AMD-DESKTOP's November 10–15 source-qualified additions and also incorporates the distinct November 9 LEGION bounded native investigations. The only observed UI/native queue mapping remains historical `1 → Short`; values `0` and `2` remain unresolved.
