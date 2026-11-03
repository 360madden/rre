# SC-306 and SC-503 — independent FreeBuff source-only review (2026-11-03)

**Owned lane:** single RRE physical-PC research manager, two independent disposable FreeBuff CLI reviewers.
**Decision:** Both real FreeBuff sessions completed successfully; **no new enum mapping or channel/interruption observation accepted**. SC-306 and SC-503 remain blocked on new qualified in-game evidence.

## Source-qualified starting questions

**SC-306:** Existing `SC-305` identifies exact physical RIFT PE SHA `1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8`, `ActionBars_AbilityQueue` and the settings object's 32-bit `+0xA4` field, with a *historical* raw value **1**. Current Full/Short/None label mapping remains unknown. The October 27 SC-306 source report found no matching conventional .cfg/.ini key and parked native plumbing after two inconclusive scans. New evidence would need a **source-qualified current RIFT Settings → Ability Queue selected label** paired with a source/time-aligned raw field observation, or actual label-to-value code in the matching original executable; guessing 0/1/2 ordering is invalid.

**SC-503:** Existing SC-303/304 historical data shows median RIFT frame-clock sample intervals `**105.469 ms / 107.422 ms**, with **zero sampled active Unit.Castbar records** in two Light's Decree traces, despite separately timestamped event callbacks. SC-502 properly attributes damage/dodge outcomes by exact modern ability/caster/target ID. Those are **older-build trial recordings**, not current-session channel/proc/interruption proof. A valid next test needs a safe, *currently usable* cast/channel candidate and source-bound start/tick/interrupt/end observations without cross-clock subtraction or forced health loss.

## Actual FreeBuff model review receipts

Two fixed source-copy lanes were added to the existing hash-pinned RRE FreeBuff ConPTY adapter and single-job parallel supervisor. They did not create another service or editor and did not change the installed RIFT addon.

| Lane | Workbridge receipt | UTC session | Result |
| --- | --- | --- | --- |
| SC-306 | `rre-freebuff-research-sc306-sc503-20261103-a1` (subworker `sc306`) | **18:03:23.446–18:03:42.635**; **19.190s** | FreeBuff exit 0, `REVIEW_END_41`, completed; the bounded screen-excerpt filter yielded **no usable new finding** |
| SC-503 | Same supervised job (subworker `sc503`) | **18:03:23.446–18:03:54.478**; **31.032s** | FreeBuff exit 0, `LIFECYCLE_DONE_53`, completed; excerpt flags the known `105ms` sampling/short-lived event ambiguity |

**Overlap:** **19.190s of actual child-process lifetime overlap**. Genuine simultaneous model token inference is not independently proven. Both disposable workspaces and owned child processes were cleaned up. Workbridge's 36 concurrent command slots are not a model-agent count. No account/session secrets, raw game IDs or out-of-scope files were supplied in the reviewers' temporary source copies.

FreeBuff SC-306 output was not sufficiently recovered to make a source-grounded positive or negative claim from the model text. The RRE manager instead retained the **existing** SC-306 no-go and performed a separate **bounded current saved-document key inspection** (job `rre-sc306-saved-settings-api-narrow-20261103-a1`; exit 0). It found zero `Inspect.Setting.*` doc keys and no exact `ActionBars_AbilityQueue` literal in that **one** saved RiftReader2Casting documentation collection; this is not a general absence proof or enum map.

The visible SC-503 `105ms sampling` caution is **already explicitly supported** by SC-303 lines 28–45 and SC-304 lines 19–55. It is not a new live interrupt trial or a decision-changing mechanism discovery. No SC task state was advanced, and no broad frozen binary or generic native helper scan was retried.

## Tooling lesson (bounded)

The first research review exposed a reporting deficiency: the existing bounded VT excerpt keyword filter recognized `NO_BLOCKERS` but not `NO_MAPPING`, queue, channel or interruption terms. `tools/freebuff-parallel-review.py` now retains these source-topic lines while still stripping obvious app UI/advertising and limiting output, with one small focused negative-case unit test. **This does not reconstruct an already discarded FreeBuff response.** Future reviews must use genuinely changed sources or new questions; do not rerun this identical wave merely to populate a filter.

## Exit and next evidence

- **SC-306:** current native queue-mode screenshot clearly showing **Full/Short/None** selection and qualified numeric field from the same character/build/settings epoch; no in-game settings changes by RRE.
- **SC-503:** bounded, RR2/operator-owned usable channel/proc/interruption trial with castbar/event timestamps in the **same frame-clock domain**, and full action identity/target/build. Old `105ms` samples alone cannot classify a missing castbar as an instant ability.
- **RC-30:** unrelated but newly refreshed SavedVariables provenance documented in `RRECOLLECTOR-RC30-POSTSTART-SAVED-2026-11-03.md`, with corrected **seven** pinned IDs and slot eight empty; still no Pin→Undo live confirmation.

**Restrictions:** no executable/process write, game input, addon change, VMware guest intervention, desktop capture lease bypass or other-repository edits. Existing parked SC-408 and SC-413 native traces were deliberately not reopened.
