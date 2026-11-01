"""Verify the interactive AWS control explorer against the canonical ledger."""
import csv
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo/security-controls.html"
REGISTER = ROOT / "docs/CONTROL_REGISTER.csv"

class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.labels = set()
        self.ids = set()
        self.external_scripts = []
    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if "id" in data:
            assert data["id"] not in self.ids
            self.ids.add(data["id"])
        if tag == "label" and "for" in data:
            self.labels.add(data["for"])
        if tag == "script" and "src" in data:
            self.external_scripts.append(data["src"])

def test_embedded_controls_exactly_match_committed_register():
    page = DEMO.read_text(encoding="utf-8")
    match = re.search(r'<script type="application/json" id="controls-data">(.*?)</script>', page, re.DOTALL)
    assert match, "Embedded source-backed control ledger must exist"
    payload = json.loads(match.group(1))
    with REGISTER.open(encoding="utf-8-sig", newline="") as file:
        truth = list(csv.DictReader(file))
    assert len(truth) == 28
    assert payload == truth
    assert len({row["ControlID"] for row in payload}) == len(payload)
    assert all(row["LiveStatus"] == "NOT_RUN" for row in payload)

def test_ledger_source_paths_are_real_and_control_ids_match():
    page = DEMO.read_text(encoding="utf-8")
    embedded = json.loads(re.search(r'<script type="application/json" id="controls-data">(.*?)</script>', page, re.DOTALL).group(1))
    for row in embedded:
        assert (ROOT / row["ImplementationPath"]).is_dir(), row["ControlID"]
        ledger = ROOT / row["EvidenceLedger"]
        assert ledger.is_file(), row["ControlID"]
        with ledger.open(newline="", encoding="utf-8") as f:
            records = list(csv.DictReader(f))
        matching = [r for r in records if r["ControlID"] == row["ControlID"]]
        assert len(matching) == 1
        assert matching[0]["Status"] == row["LiveStatus"]
    for filename in ("portfolio.svg", "01-network-core.svg", "02-iam-guardrails.svg",
                     "03-security-logging-detection.svg", "04-secure-serverless-api.svg"):
        assert (ROOT / "diagrams" / filename).is_file()

def test_demo_offline_accessibility_and_safe_dom():
    page = DEMO.read_text(encoding="utf-8")
    check = Inspector()
    check.feed(page)
    assert {"search", "project", "status"}.issubset(check.labels)
    assert {"search", "project", "status"}.issubset(check.ids)
    assert 'aria-live="polite"' in page
    assert "textContent" in page
    assert "replaceChildren" in page
    assert not check.external_scripts
    assert "innerHTML" not in page
    assert "fetch(" not in page
