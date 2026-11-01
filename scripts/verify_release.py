#!/usr/bin/env python3
"""Verify an existing release manifest; fail clearly if no manifest was packaged.

This is file integrity relative to a known manifest, not a signature, provenance
attestation or proof that Terraform and AWS services have been tested.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def verify(root: Path, manifest: Path) -> tuple[list[str], int]:
    errors = []
    count = 0
    if not manifest.is_file():
        return [f"Release manifest not found: {manifest}. Generate and review one as part of packaging; no integrity PASS can be issued."], 0
    for number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            expected, relative = line.split("  ", 1)
        except ValueError:
            errors.append(f"Line {number}: malformed checksum entry")
            continue
        if len(expected) != 64 or any(ch not in "0123456789abcdefABCDEF" for ch in expected):
            errors.append(f"Line {number}: invalid SHA-256 digest")
            continue
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            errors.append(f"Line {number}: missing or unsafe path: {relative}")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected.lower():
            errors.append(f"Line {number}: SHA-256 mismatch: {relative}")
            continue
        count += 1
    if not count and not errors:
        errors.append("Empty release manifest cannot establish file integrity")
    return errors, count

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "MANIFEST.sha256")
    args = parser.parse_args()
    errors, count = verify(ROOT, args.manifest.resolve())
    if errors:
        for message in errors:
            print("FAIL:", message, file=sys.stderr)
        return 1
    print(f"PASS: {count} file SHA-256 checks. This manifest is not a digital signature.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
