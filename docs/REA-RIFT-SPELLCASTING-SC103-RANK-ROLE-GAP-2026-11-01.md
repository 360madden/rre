# SC-103 — RIFT ability ID, rank and Role ambiguity

**November 1, 2026. Status: BLOCKED after source-bounded offline research**, with useful identity facts preserved. **SC1 phase is NOT complete.** REA used only old saved ability catalogs. RIFT research continues to target the locally installed physical-PC executable; the earlier capture remains historical old-build evidence and is not a current-game snapshot.

## Exact sources and reproducible comparison

[Source-pinned identity comparison](REA-RIFT-SPELLCASTING-SC103-IDENTITY-GAP-2026-11-01.json), SHA-256 `31e5f5093066b4c9b5a66e4f7d902ae4e1e0a5e82c2842205d31e40932642805`. Two RR2 original sources:

- `artifacts/casting-20261025-01/ranged-evidence-03/evidence.json` SHA-256 `1bd8694f91abb17704cd7a769b4cb63f2f334b5d00853b220f040a627c63e695`;
- `artifacts/casting-20261025-01/ranged-evidence-04/evidence.json` SHA-256 `9e81dccdf53640c5ae8f874b6bad16d38f75faeee06be7999032e9695d934630`.

Historical game build SHA-256 `7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd`. Physical PC's currently installed executable separately rehashed November 1 as `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`. This report does not claim that its native spellbook matches the old data.

**Direct comparison:** both saved arrays return **55 identical lookup IDs**. **54 of the 55 detailed API records are exactly identical**, comparing all stored keys and values. The one changed record is **Righteous Charge** `A01BB8C035B6A96DD`: its `outOfRange` field is explicitly `true` in the earlier capture and **absent** in the later one. Absence is **unknown**, not proof that it became false. There is **no evidence of a changed role or learned/ranked ability between these two captures**.

## Same display name is not the same ability identity

| Duplicate display name | Different modern lookup IDs | What is observed | What cannot yet be inferred |
| --- | --- | --- | --- |
| **Building Fury** | **3** | Three distinct IDs, all explicitly `passive=true`, with identical description: bonus Attack Power contribution to finishers based on Attack Points | Cannot prove rank 1/2/3, role origin, required soul points or level from identical text |
| **Changing Role** | **4** | Four distinct IDs with the same Role-changing description, `castingTime=2` and reported `cooldown=2`; one explicitly `unusable=true` | Cannot map the IDs to role slots/active role, or infer which specific restriction made one unusable |

Across all 55 records, the queried keys `rank`, `level`, `requiredLevel`, `role`, `calling`, `soul`, `mastery` and `variant` occur **zero times**. The normal `name` and modern `idNew` appear 55 times; descriptions appear 47 times. The absence of rank/role fields is a **limitation of this particular captured API detail surface**, not proof the RIFT client lacks these concepts internally.

The `target` field for Changing Role currently carries the selected practice dummy's identity; it is **not** a trustworthy role-slot label or a proof that the spell targets that enemy. Do not treat it as a mapping from an ability ID to active Role.

## Research decision and next evidence trigger

The **distinct identity and name-collision investigation is complete**, but **SC-103 rank/Role assignment is blocked** because neither capture is a qualified different-role/rank state and no native spellbook/soul/trainer UI with the exact character level/Role/points has been matched to these IDs. Filling in ranks by enumeration order or similar hex prefixes would be fabrication.

**Resume only when:** we have source-hash-bound local-PC RIFT spellbook/soul UI and recorded character level, selected Role, points and matching `Inspect.Ability.New.List/Detail` snapshots, preferably before/after an actual Role change. Any game operation/capture remains separately evidenced; none was performed here.

This leaves **SC1 active**. The next currently ready procedural task is **SC-603**, to preserve the source set and handoff. SC3 GCD, SC4 native execution and SC5 conditional channel/interrupt cases remain independent research questions. No REA game input, process attach, binary modification, VM access or RR2/Workbridge code edits occurred.

**Parallel Workbridge receipts:** `rea_sc103_l1_duplicates_20261101`, `rea_sc103_l2_schema_20261101`, `rea_sc103_l3_stability_20261101`, `rea_sc103_l4_role_switch_20261101`, `rea_sc103_l5_passive_20261101` — all passed. These are five separate analysis jobs coordinated by one AI, not five launched independent reasoning agents.
