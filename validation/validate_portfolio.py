from pathlib import Path
import json, py_compile
R=Path(__file__).resolve().parents[1]
required=[
"README.md",
"projects/01-network-core/README.md",
"projects/01-network-core/docs/Threat-Model.md",
"projects/02-iam-guardrails/README.md",
"projects/02-iam-guardrails/docs/scp-pack/protect-security-services.json",
"projects/03-security-logging-detection/README.md",
"projects/03-security-logging-detection/lambda/index.py",
"projects/04-secure-serverless-api/README.md",
"projects/04-secure-serverless-api/lambda/handler.py",
]
missing=[x for x in required if not (R/x).exists()]
assert not missing, missing
json.loads((R/"projects/02-iam-guardrails/docs/scp-pack/protect-security-services.json").read_text())
json.loads((R/"projects/02-iam-guardrails/docs/scp-pack/protect-s3-public-access.json").read_text())
py_compile.compile(str(R/"projects/03-security-logging-detection/lambda/index.py"),doraise=True)
py_compile.compile(str(R/"projects/04-secure-serverless-api/lambda/handler.py"),doraise=True)
for p in R.rglob("*"):
    if p.is_file() and p.name != "validate_portfolio.py" and p.suffix.lower() in {".md",".py",".tf",".json",".yml",".yaml",".csv"}:
        txt=p.read_text(encoding="utf-8",errors="ignore").lower()
        for term in ["lorem "+"ipsum","<place"+"holder>","insert "+"here"]:
            assert term not in txt,(p,term)
print("PASS: required portfolio artifacts")
print("PASS: Python syntax")
print("PASS: JSON policy syntax")
print("PASS: unfinished-content scan")
