"""Release integrity verification must fail closed on missing or invalid manifests."""
import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("verify_release", ROOT / "scripts/verify_release.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def test_missing_release_manifest_is_explicit_failure(tmp_path):
    errors, checked = module.verify(tmp_path, tmp_path / "MANIFEST.sha256")
    assert checked == 0
    assert len(errors) == 1 and "not found" in errors[0]

def test_release_manifest_matches_known_content(tmp_path):
    target = tmp_path / "sample.txt"
    target.write_text("approved synthetic release", encoding="utf-8")
    manifest = tmp_path / "MANIFEST.sha256"
    manifest.write_text(hashlib.sha256(target.read_bytes()).hexdigest() + "  sample.txt\n")
    errors, checked = module.verify(tmp_path, manifest)
    assert not errors and checked == 1
    target.write_text("tampered", encoding="utf-8")
    errors, checked = module.verify(tmp_path, manifest)
    assert errors and checked == 0 and "mismatch" in errors[0]

def test_path_traversal_and_malformed_manifest_fail(tmp_path):
    manifest = tmp_path / "MANIFEST.sha256"
    manifest.write_text("badline\n" + "0" * 64 + "  ../outside.txt\n")
    errors, checked = module.verify(tmp_path, manifest)
    assert checked == 0
    assert any("malformed" in e for e in errors)
    assert any("unsafe" in e for e in errors)

def test_missing_lockfile_is_not_offline_provider_claim():
    source = (ROOT / "validation/validate_portfolio.py").read_text(encoding="utf-8")
    assert "provider_lockfiles_pending" in source
    assert "provider lockfiles are reported but not validated offline" in source
