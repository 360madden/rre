#!/usr/bin/env python3
"""Fail-closed selector for one historical RIFT x64 PE used in offline tests.

The original-byte RVA/manifest assertions only apply to this exact build.
No installed-game fallback, process attachment, disassembly, or file mutation.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

ENV_NAME = "RRE_LEGACY_PE"
EXPECTED_SIZE = 59_963_840
EXPECTED_SHA256 = "7c356c9dde9e12fcbff3c08d953b0630b48b1510a0ffb36e4ec164606e7b17bd"


def qualify_legacy_pe(path: Path | str) -> dict[str, str | int]:
    """Return source provenance only after an exact size+SHA-256 check."""
    try:
        candidate = Path(path).resolve(strict=True)
        if not candidate.is_file():
            raise ValueError("Legacy PE fixture is not a regular file")
        size = candidate.stat().st_size
        if size != EXPECTED_SIZE:
            raise ValueError(f"Legacy PE fixture size mismatch: {size} != {EXPECTED_SIZE}")
        with candidate.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != EXPECTED_SHA256:
            raise ValueError("Legacy PE fixture SHA-256 mismatch")
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"Cannot read legacy PE fixture: {exc}") from exc
    return {"path": str(candidate), "size": size, "sha256": digest}


def resolve_legacy_pe() -> Path:
    """Require explicit fixture selection for historical native test paths."""
    supplied = os.environ.get(ENV_NAME, "")
    if not supplied.strip():
        raise ValueError(f"{ENV_NAME} must point to the exact original offline RIFT PE")
    return Path(str(qualify_legacy_pe(supplied)["path"]))
