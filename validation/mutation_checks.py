#!/usr/bin/env python3
"""Eight targeted fault mutations in temporary copies; no source edits or AWS calls."""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
API='projects/04-secure-serverless-api/lambda/handler.py'
DETECT='projects/03-security-logging-detection/lambda/ingest_securityhub.py'
MUTATIONS=[
 ('conditional-write',API,'attribute_not_exists(request_id)','attribute_exists(request_id)','tests/test_application.py::test_create_and_replay'),
 ('tenant-scope',API,'hashlib.sha256((subject + ":" + key).encode())','hashlib.sha256(key.encode())','tests/test_application.py::test_users_cannot_collide'),
 ('replay-integrity',API,'existing.get("owner_sub") == subject and existing.get("payload_hash") == digest','existing.get("owner_sub") == subject','tests/test_application.py::test_create_and_replay'),
 ('auth-required',API,'if subject is None:','if False:','tests/test_application.py::test_missing_auth'),
 ('propagate-index-failure',DETECT,'        index(index_name, doc_id, json.dumps(record, sort_keys=True).encode())','        try:\n            index(index_name, doc_id, json.dumps(record, sort_keys=True).encode())\n        except Exception:\n            pass','tests/test_application.py::test_archive_before_index_and_retry'),
 ('sign-search-request',DETECT,'SigV4Auth(credentials.get_frozen_credentials(), "es", session.region_name).add_auth(request)','pass','tests/test_sdk_integration.py::test_sigv4_request_has_exact_signed_body_and_scope'),
 ('validate-search-host',DETECT,'if not isinstance(endpoint, str) or not ENDPOINT.fullmatch(endpoint):','if False:','tests/test_sdk_integration.py::test_invalid_search_destination_never_sends'),
 ('finding-account-scope',DETECT,'[finding["ProductArn"], finding["AwsAccountId"], finding["Id"], stamp]','[finding["ProductArn"], finding["Id"], stamp]','tests/test_robustness.py::test_cross_account_finding_ids_differ'),
]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'reports/mutations.json');args=parser.parse_args()
    results=[]
    with tempfile.TemporaryDirectory(prefix='portfolio-mutations-') as tmp:
        base=Path(tmp)/'baseline';base.mkdir()
        shutil.copytree(ROOT/'projects',base/'projects',ignore=shutil.ignore_patterns('__pycache__','.terraform','*.zip'))
        shutil.copytree(ROOT/'tests',base/'tests',ignore=shutil.ignore_patterns('__pycache__'))
        selectors=sorted({m[4] for m in MUTATIONS})
        run=subprocess.run([sys.executable,'-m','pytest','-q',*selectors],cwd=base,text=True,capture_output=True)
        if run.returncode:raise SystemExit('Baseline must pass before mutation testing:\n'+run.stdout+run.stderr)
        for name,relative,original,replacement,test in MUTATIONS:
            target=Path(tmp)/name;shutil.copytree(base,target,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
            file=target/relative;content=file.read_text()
            if content.count(original)!=1:raise SystemExit('Mutation anchor changed: '+name)
            file.write_text(content.replace(original,replacement))
            run=subprocess.run([sys.executable,'-m','pytest','-q',test],cwd=target,text=True,capture_output=True)
            # pytest exit 1 is an executed test failure; collection errors are not kills.
            results.append({'mutation':name,'test':test,'detected':run.returncode==1,'pytest_exit':run.returncode,'transcript':run.stdout+run.stderr})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({'scope':'Eight selected regressions; not a comprehensive mutation score','mutations':results,'detected':sum(r['detected'] for r in results),'total':len(results)},indent=2)+'\n')
    print(f"Detected {sum(r['detected'] for r in results)}/{len(results)} targeted defects")
    return 0 if all(r['detected'] for r in results) else 1
if __name__=='__main__':sys.exit(main())
