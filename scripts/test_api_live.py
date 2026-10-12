#!/usr/bin/env python3
"""Opt-in low-volume live writes. Uses only synthetic customer labels."""
import argparse
import json
import os
import uuid
from urllib.error import HTTPError
from urllib.request import Request,urlopen
from urllib.parse import urlparse

def main():
    p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--execute-sandbox-writes',action='store_true');a=p.parse_args()
    if not a.execute_sandbox_writes:raise SystemExit('Requires explicit --execute-sandbox-writes; creates a synthetic DynamoDB item.')
    host=urlparse(a.url)
    if host.scheme!='https' or not host.hostname or not host.hostname.endswith('.amazonaws.com') or '.execute-api.' not in host.hostname:raise SystemExit('Expected an HTTPS API Gateway hostname.')
    token=os.environ.get('API_ID_TOKEN')
    if not token:raise SystemExit('Set API_ID_TOKEN in the local environment. Never paste it into reports.')
    key=uuid.uuid4().hex
    def request(body,authenticated=True):
        headers={'Content-Type':'application/json','Idempotency-Key':key}
        if authenticated:headers['Authorization']=token
        req=Request(a.url,json.dumps(body).encode(),headers,method='POST')
        try:
            with urlopen(req,timeout=20) as result:return result.status
        except HTTPError as exc:return exc.code
    body={'customer_id':'synthetic-validation','action':'create'}
    tests=[('no_token',(401,403),lambda:request(body,False)),('create',(201,),lambda:request(body)),('replay',(200,),lambda:request(body)),('changed_payload',(409,),lambda:request({**body,'action':'update'})),('invalid_type',(400,),lambda:request({**body,'customer_id':5}))]
    failed=False
    for name,expected,call in tests:
        status=call();ok=status in expected;failed|=not ok
        print(json.dumps({'test':name,'expected':expected,'actual':status,'pass':ok}))
    raise SystemExit(1 if failed else 0)
if __name__=='__main__':main()
