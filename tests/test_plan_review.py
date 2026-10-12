"""Negative tests for selected plan-risk checks; fixtures are synthetic, not AWS plans."""
import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('review_plan',Path(__file__).resolve().parents[1]/'validation/review_plan.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def plan(kind,after,actions=None,unknown=None):
    return {'format_version':'1.2','resource_changes':[{'address':kind+'.example','type':kind,'mode':'managed','change':{'actions':actions or ['create'],'after':after,'after_unknown':unknown or {}}}]}
def test_safe_bucket():
    r=m.review(plan('aws_s3_bucket_public_access_block',{k:True for k in m.TRUE_FIELDS['aws_s3_bucket_public_access_block']}));assert r['status']=='PASS_SELECTED_CHECKS'
@pytest.mark.parametrize('kind,field',[(k,f) for k,fs in m.TRUE_FIELDS.items() for f in fs])
def test_disabled_protections(kind,field):
    values={k:True for k in m.TRUE_FIELDS[kind]};values[field]=False
    assert any(x['code']=='PROTECTION' for x in m.review(plan(kind,values))['issues'])
@pytest.mark.parametrize('actions',[['delete'],['delete','create'],['create','delete'],['forget']])
def test_destructive_actions(actions):
    assert any(x['code']=='DESTRUCTIVE' for x in m.review(plan('aws_vpc',{},actions))['issues'])
@pytest.mark.parametrize('value',[None,{},[],{'format_version':'2.0'}, {'format_version':'1.2','resource_changes':[]}])
def test_bad_or_empty_input_is_not_pass(value):
    with pytest.raises(ValueError):m.review(value)
@pytest.mark.parametrize('family,cidr',[('cidr_blocks','0.0.0.0/0'),('ipv6_cidr_blocks','::/0')])
def test_world_ingress(family,cidr):
    assert m.review(plan('aws_security_group',{'ingress':[{family:[cidr]}]}))['status']=='REVIEW_REQUIRED'
@pytest.mark.parametrize('kind',list(m.BLOCK_FIELDS))
def test_encryption_unknown_fails_closed(kind):
    after={b:[{k:True}] for b,k in m.BLOCK_FIELDS[kind]}
    block=m.BLOCK_FIELDS[kind][0][0]
    assert m.review(plan(kind,after,unknown={block:True}))['status']=='REVIEW_REQUIRED'
@pytest.mark.parametrize('kind,after',[
 ('aws_subnet',{'map_public_ip_on_launch':True}),
 ('aws_api_gateway_method',{'authorization':'NONE'}),
 ('aws_cognito_user_pool',{'mfa_configuration':'OPTIONAL'}),
 ('aws_security_group_rule',{'type':'ingress','cidr_blocks':['0.0.0.0/0']}),
 ('aws_vpc_security_group_ingress_rule',{'cidr_ipv6':'::/0'}),
])
def test_unsafe_exposure(kind,after):assert m.review(plan(kind,after))['status']=='REVIEW_REQUIRED'
def test_sensitive_values_not_echoed():
    r=m.review(plan('aws_vpc',{'secret':'never-print-this'}));assert 'never-print-this' not in str(r)
def test_unknown_inline_ingress_blocks_review():
    assert m.review(plan('aws_security_group',{},unknown={'ingress':True}))['status']=='REVIEW_REQUIRED'
