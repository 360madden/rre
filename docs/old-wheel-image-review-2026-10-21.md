# VE-002 — Direct review of the recorded old-wheel screenshot pair

**Reviewed:** October 21, 2026, America/New_York  
**Scope:** Saved RIFT image/action evidence only. This is a Manager-led visual inspection, **not** a new game/VM action, a new capture, independent source-code QA, or a separately connected vision-provider assessment.  
**Model:** GPT-6. **Reasoning-effort metadata:** unavailable.

## Finding: inconclusive, with an important baseline timing confound

The original report's **inconclusive** conclusion remains the supported outcome. The two saved images show the same RIFT cobblestone courtyard, near-centered character, and stable HUD layout. At the displayed scale there is no unmistakable camera-scale jump. Direct native-resolution crops of all four originally selected ground-texture regions show slight pattern shifts and lighting/shading differences; the scene also contains independently changing actors/effects. A small radial zoom is **plausible**, but neither successful zoom nor absence of zoom is established.

The recorded input action was **one wheel notch**, with no key or button held. It reported `deliverySucceeded=true` but **`responseVerified=false`**; this confirms input insertion, not that RIFT accepted a zoom operation. The binding recorded the same game process/start and client dimensions in both frames.

**Timing reconstructed from the original capture and action metadata:**

| Event | Recorded guest-clock UTC |
|---|---|
| Before screenshot | 2026-10-20 13:10:51.065101 |
| Wheel event inserted | 2026-10-20 13:11:16.0968545 |
| After screenshot | 2026-10-20 13:11:17.0541948 |

The before image is approximately **25.032 seconds before** input. The after image is **0.957 seconds after** input; the entire image interval is **25.989 seconds**. The large pre-action gap allows independent actor motion, animation and scene-lighting changes. Host/guest clock synchronization is not established, but the sequence within these matching guest-clock records is internally ordered. The old pair is therefore not a tightly controlled causal before/after zoom experiment.

## Original fixed-policy image diagnostic — unchanged

The image matcher had **three qualified patches and one unqualified patch**, under the original `maxMse=100` policy:

| Original center (1211×686 frame) | Matched displacement (pixels) | MSE | Quality |
|---|---:|---:|---|
| (400, 350) | (-4, 0) | 144.286 | **Poor match; unqualified** |
| (800, 350) | (+3, 0) | 10.327 | Qualified |
| (420, 550) | (-5, +6) | 30.184 | Qualified |
| (780, 550) | (+5, +6) | 11.408 | Qualified |

Three displacements have directions compatible with *small* outward radial change, but the missing fourth quality-qualified sample prevents the already-specified radial-out predicate from passing. Scene animation and localized brightness remain alternative explanations. **No thresholds, patches, policy, saved results or published source hashes were edited.**

## Evidence checked and preserved

Original immutable publication:

`artifacts/visual-evidence-release-20261020/recorded-old-wheel-baseline/`

- Original before BMP SHA-256: `7d54573e10ccea632ece29ae933f6686b37f605b03e25fb3b3b4e3f1e32eb385`.
- Original after BMP SHA-256: `c154b72ef61734e8b1471c122bbc16f57d383f572ce77c902760c11f3ceb1dfe`.
- Original action-result SHA-256: `f6c076472162013f6a14509b555c511b77a90087ce4274465aff51d244ffc3f0`.
- Original host action journal SHA-256: `ccf1b207c1b0708d53ceea44b66fcb7befff0e80de696877d511e05305fe78c3`.
- Original report SHA-256: `1784e4d74a7665eb5cbfa2482e818af7a2944a0c615bc5e11b189828fc49698e`.
- Publication verifier `rre-20261021-wheel-original-bundle-verify-01`: **exit 0**, full 13-file package validated. This establishes file-set integrity, not source authenticity or gameplay response.
- Independent metadata-timing check `rre-20261021-wheel-action-frame-timing-01`: **exit 0**, before/action/after ordering and input/source hashes confirmed.

A **new, non-overwriting** review packet with one downscaled side-by-side overview, two pairs of full-resolution sample-region contact crops, and a separate JSON/last-written publication receipt was produced at:

`artifacts/visual-old-wheel-review-20261021-01/`

Its `review.json` has SHA-256 `678273e497214a2f15a603c1442a9b0506cabaed399e19b061df5d19e0dddead`, and `complete.json` has SHA-256 `5d83a062c953b2d27108612d305c6d240926961058f223c1d20a6abaf1f2196c`. Derived JPEGs are **lossy viewing aids**; the two original 1211×686 BMPs and all recorded action/guest metadata remain untouched. The previews were actually delivered as pixels to the ChatGPT Manager's current visual inspection, rather than merely described as filenames. This is **not** evidence that a separate independent image-capable model, service, or renderer received the pixels, and it does not complete WA-005 source-code QA.

## Decision and next gate

**VE-002 review outcome: inspected and documented; zoom outcome remains INCONCLUSIVE.** The previous blanket *no visible zoom* interpretation is not independently corroborated, but the three small outward candidates do not establish successful wheel-based zoom either.

For a future separately approved camera experiment, acquire a fresh frame immediately before input, another immediately afterward, and a settled frame, with fixed stationary-world landmarks, exact VM/game/scene association and an independent camera-only measurement. **Do not replay the old input, adjust thresholds to manufacture a verdict, or claim a camera calibration from screenshots alone.**

The outstanding **WA-005 independent inspector code QA**, **WA-006 multi-object/hit-owner/camera qualification**, **WA-007 previously blocked native acquisition**, and **M3-001 true type-7 handler/producer** gates remain unchanged. No live RIFT control or process attachment was performed in this review.
