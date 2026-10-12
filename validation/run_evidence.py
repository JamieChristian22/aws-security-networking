#!/usr/bin/env python3
"""Run credential-free checks and record real exit codes, timestamps and source hashes."""
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    reports=ROOT/'reports';reports.mkdir(exist_ok=True)
    py=sys.executable
    commands=[
        ('pytest',[py,'-m','pytest','-q','--junitxml=reports/junit.xml','--cov=projects/03-security-logging-detection/lambda','--cov=projects/04-secure-serverless-api/lambda','--cov-branch','--cov-fail-under=100','--cov-report=term-missing','--cov-report=json:reports/coverage.json']),
        ('mutations',[py,'validation/mutation_checks.py','--output','reports/mutations.json']),
        ('bandit',[py,'-m','bandit','-q','-r','projects','-f','json','-o','reports/bandit.json']),
        ('repository-checks',[py,'validation/validate_portfolio.py']),
    ]
    record={'scope':'Offline execution only; no Terraform provider execution or live AWS','python':platform.python_version(),'platform':platform.platform(),'checks':[]}
    record['source_sha256']={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for folder in ('projects','tests','validation') for f in sorted((ROOT/folder).rglob('*')) if f.is_file() and f.suffix in ('.py','.json','.hcl') and not {'.terraform','__pycache__'}.intersection(f.parts)}
    freeze=subprocess.run([py,'-m','pip','freeze'],capture_output=True,text=True,check=True)
    (reports/'environment.txt').write_text(freeze.stdout)
    for name,command in commands:
        start=datetime.now(timezone.utc).isoformat()
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        (reports/(name+'.txt')).write_text(result.stdout+result.stderr)
        if name=='repository-checks' and result.returncode==0:
            (reports/'repository-checks.json').write_text(result.stdout)
        record['checks'].append({'name':name,'argv':command,'started_at_utc':start,'ended_at_utc':datetime.now(timezone.utc).isoformat(),'exit_code':result.returncode})
        print(name, 'PASS' if result.returncode==0 else 'FAIL',flush=True)
    (reports/'execution.json').write_text(json.dumps(record,indent=2)+'\n')
    return int(any(c['exit_code'] for c in record['checks']))
if __name__=='__main__':sys.exit(main())
