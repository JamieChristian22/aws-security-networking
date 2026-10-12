#!/usr/bin/env python3
"""Offline packaging, link, evidence-status and syntax checks; not an AWS validator."""
import ast
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'.git','.terraform','__pycache__','.pytest_cache','.venv','.hypothesis'}

def files():
    return [p for p in ROOT.rglob('*') if p.is_file() and not EXCLUDED.intersection(p.relative_to(ROOT).parts)]

def main():
    errors=[];paths=files();counts={'json':0,'python':0,'links':0,'live_cases':0}
    for p in paths:
        rel=p.relative_to(ROOT)
        if p.name.endswith('.tfstate') or '.tfstate.' in p.name or p.suffix=='.tfplan' or p.name=='terraform.tfvars':
            errors.append(f'Private deployment artifact must not be published: {rel}')
        if p.suffix=='.json':
            try:json.loads(p.read_text());counts['json']+=1
            except Exception as exc:errors.append(f'{rel}: JSON error {exc}')
        if p.suffix=='.py':
            try:ast.parse(p.read_text(),filename=str(rel));counts['python']+=1
            except SyntaxError as exc:errors.append(f'{rel}: Python syntax {exc}')
        if p.suffix=='.md':
            text=p.read_text()
            for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
                target=target.split('#')[0].strip().split(' "')[0]
                if not target or '://' in target or target.startswith('mailto:'):continue
                resolved=(p.parent/unquote(target)).resolve();counts['links']+=1
                if not resolved.exists():errors.append(f'{rel}: broken local link {target}')
    roots=sorted((ROOT/'projects').glob('*/iac/terraform'))
    if len(roots)!=4:errors.append('Expected four canonical roots')
    for root in roots:
        for name in ('terraform.tf.json','provider.tf.json','variable.tf.json','resource.tf.json','.terraform.lock.hcl','tests/controls.tftest.hcl'):
            if not (root/name).exists():errors.append(f'{root.relative_to(ROOT)} missing {name}')
        ledger=root.parents[1]/'evidence/ACCEPTANCE.csv'
        if not ledger.exists():errors.append(f'Missing {ledger}');continue
        for row in csv.DictReader(ledger.open()):
            counts['live_cases']+=1
            if row['Status'] not in {'NOT_RUN','BLOCKED','FAIL','PASS_LIVE'}:errors.append('Invalid live status '+row['ControlID'])
            if row['Status']=='PASS_LIVE' and not all(row.get(k) for k in ('Actual','ExecutedAtUTC','EvidencePath','Reviewer')):errors.append('Unsupported live PASS '+row['ControlID'])
    if errors:
        print('\n'.join(errors));return 1
    print(json.dumps({'status':'PASS_OFFLINE','checks':counts,'scope':'Syntax, local links, canonical structure and evidence ledger consistency only'},indent=2));return 0
if __name__=='__main__':sys.exit(main())
