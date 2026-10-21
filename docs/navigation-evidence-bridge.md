# NAV-005 — Saved RR2 capture/action association bridge

October 21, 2026. This is a read-only offline classifier, **not** a navigation trial producer.

`tools/navigation_evidence_bridge.py` verifies that the original saved BMP bytes match the metadata's SHA-256, compares game process/start, window, executable identity and client dimensions across one capture/action pair, and classifies the recorded action as keyboard, mouse button or wheel. It flags a right-button camera action, missing reviewed click point, uncertain delivery, and a capture outside the proposed immediate-before interval.

The existing October 20 RR2 `button-only-before` capture and `button-only-result.json` are a concrete demonstration: original image bytes and target identity agree, **but the button was right mouse**, the frame preceded the action too long for the proposed bound, and the record has no reviewed destination point, continuous player samples or cancellation evidence. Therefore no NAV-003 navigation trace is produced or authorized.

For a file-only audit in PowerShell under `C:\work\rre`:

```powershell
& .\.venv\Scripts\python.exe -B tools/navigation_evidence_bridge.py `
  --capture C:\work\riftreader2\artifacts\native-control-followup-20261020\button-only-before\capture.json `
  --action C:\work\riftreader2\artifacts\native-control-followup-20261020\button-only-result.json `
  --image C:\work\riftreader2\artifacts\native-control-followup-20261020\button-only-before\image.bmp
```

Add `--output artifacts/nav005-unique-report.json` to save a new, nonoverwriting report. This program does not run a screenshot viewer or independently interpret the image contents; matching hashes prove only file integrity. It does not use control APIs, modify RR2 or infer current input approval.

The new `tools/tests_navigation/test_navigation_evidence_bridge.py` covers nine cases, including the actual retained camera-control pair. NAV-002 still needs a genuine reviewed ground destination, synchronized player samples and real cancellation observation. Do not manufacture these from an old camera trial.
