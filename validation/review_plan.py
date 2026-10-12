#!/usr/bin/env python3
"""Review selected risks in terraform show -json output. Never deploys or logs values."""
import argparse
import json
import sys
from pathlib import Path

TRUE_FIELDS = {
    'aws_s3_bucket_public_access_block': ('block_public_acls','block_public_policy','ignore_public_acls','restrict_public_buckets'),
    'aws_cloudtrail': ('enable_logging','is_multi_region_trail','enable_log_file_validation'),
    'aws_kms_key': ('enable_key_rotation',),
    'aws_dynamodb_table': ('deletion_protection_enabled',),
}
BLOCK_FIELDS = {
    'aws_dynamodb_table': (('point_in_time_recovery','enabled'),('server_side_encryption','enabled')),
    'aws_opensearch_domain': (('encrypt_at_rest','enabled'),('node_to_node_encryption','enabled'),('domain_endpoint_options','enforce_https')),
}
def review(plan):
    if not isinstance(plan,dict) or str(plan.get('format_version','')).split('.')[0]!='1':
        raise ValueError('Expected Terraform plan JSON format major version 1')
    changes=plan.get('resource_changes')
    if not isinstance(changes,list) or not changes:
        raise ValueError('No resource changes to review; empty plans require a separate no-change review')
    issues=[]; reviewed=[]
    def flag(address,code,message):issues.append({'address':address,'code':code,'message':message})
    for item in changes:
        if not isinstance(item,dict) or not all(isinstance(item.get(k),str) for k in ('address','type','mode')):
            raise ValueError('Malformed resource change metadata')
        address=item['address'];kind=item['type'];change=item.get('change')
        if not isinstance(change,dict) or not isinstance(change.get('actions'),list) or not change['actions']:
            raise ValueError('Malformed resource actions')
        actions=change['actions']
        if any(a not in {'create','read','update','delete','no-op','forget'} for a in actions):
            raise ValueError('Unsupported resource action')
        if 'delete' in actions or 'forget' in actions:
            flag(address,'DESTRUCTIVE','Deletion, replacement or state removal requires separate approval')
        if item['mode']=='data':continue
        if item['mode']!='managed':raise ValueError('Unsupported resource mode')
        if actions==['delete'] or actions==['forget']:continue
        after=change.get('after');unknown=change.get('after_unknown',{})
        if not isinstance(after,dict) or not isinstance(unknown,dict):
            raise ValueError('Missing planned resource values')
        reviewed.append(address)
        for key in TRUE_FIELDS.get(kind,()):
            if unknown.get(key) or after.get(key) is not True:flag(address,'PROTECTION',key+' must be known and enabled')
        for block,key in BLOCK_FIELDS.get(kind,()):
            values=after.get(block)
            if unknown.get(block) or not isinstance(values,list) or not values or any(not isinstance(v,dict) or v.get(key) is not True for v in values):
                flag(address,'PROTECTION',block+'.'+key+' must be known and enabled')
        if kind=='aws_subnet' and (unknown.get('map_public_ip_on_launch') or after.get('map_public_ip_on_launch') is not False):
            flag(address,'PUBLIC_IP','Subnet automatic public addressing must be disabled')
        if kind=='aws_security_group':
            if unknown.get('ingress'):flag(address,'UNKNOWN_INGRESS','Ingress must be fully resolved for review')
            rules=after.get('ingress',[])
            if not isinstance(rules,list):raise ValueError('Malformed ingress collection')
            for rule in rules:
                if not isinstance(rule,dict):raise ValueError('Malformed ingress rule')
                if any(c in ('0.0.0.0/0','::/0') for c in (rule.get('cidr_blocks') or [])+(rule.get('ipv6_cidr_blocks') or [])):
                    flag(address,'PUBLIC_INGRESS','Unrestricted IPv4 or IPv6 ingress requires separate review')
        if kind in ('aws_security_group_rule','aws_vpc_security_group_ingress_rule'):
            if kind=='aws_vpc_security_group_ingress_rule' or after.get('type')=='ingress':
                if unknown:flag(address,'UNKNOWN_RULE','Standalone ingress has unresolved fields')
                cidrs=(after.get('cidr_blocks') or [])+(after.get('ipv6_cidr_blocks') or [])+[after.get('cidr_ipv4'),after.get('cidr_ipv6')]
                if any(c in ('0.0.0.0/0','::/0') for c in cidrs):flag(address,'PUBLIC_INGRESS','Unrestricted standalone ingress requires separate review')
        if kind=='aws_api_gateway_method' and (unknown.get('authorization') or after.get('authorization') in (None,'NONE')):
            flag(address,'AUTH','API method authentication must be resolved and enabled')
        if kind=='aws_cognito_user_pool' and (unknown.get('mfa_configuration') or after.get('mfa_configuration')!='ON'):
            flag(address,'MFA','User-pool MFA must be required')
    return {'status':'REVIEW_REQUIRED' if issues else 'PASS_SELECTED_CHECKS','scope':'Selected plan risks only; not AWS authorization, provider validation or deployment approval','managed_resources_reviewed':len(reviewed),'issues':issues}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('plan',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    try:result=review(json.loads(args.plan.read_text()))
    except (ValueError,OSError,TypeError,KeyError):
        result={'status':'INVALID_INPUT','issues':[],'message':'Plan could not be reviewed; details omitted to avoid disclosing plan contents'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status']);return 0 if result['status']=='PASS_SELECTED_CHECKS' else 1
if __name__=='__main__':sys.exit(main())
