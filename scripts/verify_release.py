#!/usr/bin/env python3
"""Verify delivered files against the unsigned release manifest."""
import hashlib
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[1]
errors=[];count=0
for line in (R/'MANIFEST.sha256').read_text().splitlines():
    expected,relative=line.split('  ',1)
    p=(R/relative).resolve()
    if not p.is_relative_to(R) or not p.is_file():errors.append(relative+': missing/invalid path');continue
    if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:errors.append(relative+': checksum mismatch')
    count+=1
if errors:print('\n'.join(errors));sys.exit(1)
print(f'PASS: {count} file checksums. This manifest is not a digital signature.')
