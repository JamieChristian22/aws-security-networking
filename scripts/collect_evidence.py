#!/usr/bin/env python3
"""Read-only AWS evidence capture. Never reads secret values or authentication tokens."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--account-id',required=True)
    parser.add_argument('--region',default='us-east-1')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--trail-name')
    parser.add_argument('--firewall-arn')
    parser.add_argument('--table-name')
    parser.add_argument('--domain-name')
    args=parser.parse_args()
    import boto3
    session=boto3.Session(region_name=args.region)
    identity=session.client('sts').get_caller_identity()
    if identity['Account']!=args.account_id:
        raise SystemExit('Account mismatch; no evidence collected.')
    args.output.mkdir(parents=True,exist_ok=False)
    calls=[('identity',lambda:identity)]
    if args.trail_name:calls.append(('trail-status',lambda:session.client('cloudtrail').get_trail_status(Name=args.trail_name)))
    if args.firewall_arn:calls.append(('firewall',lambda:session.client('network-firewall').describe_firewall(FirewallArn=args.firewall_arn)))
    if args.table_name:
        calls.extend([('table',lambda:session.client('dynamodb').describe_table(TableName=args.table_name)),('pitr',lambda:session.client('dynamodb').describe_continuous_backups(TableName=args.table_name))])
    if args.domain_name:calls.append(('search-domain',lambda:session.client('opensearch').describe_domain(DomainName=args.domain_name)))
    manifest=[];failed=False
    for name,call in calls:
        try:
            result=call();status='CAPTURED'
        except Exception as exc:
            result={'error_type':type(exc).__name__};status='ERROR';failed=True
        data=json.dumps({'captured_at':datetime.now(timezone.utc).isoformat(),'region':args.region,'status':status,'result':result},indent=2,default=str).encode()
        (args.output/(name+'.json')).write_bytes(data)
        manifest.append({'file':name+'.json','sha256':hashlib.sha256(data).hexdigest(),'status':status})
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Capture complete. Review and redact identifiers before publication. Capture is not a control PASS.')
    raise SystemExit(1 if failed else 0)
if __name__=='__main__':main()
