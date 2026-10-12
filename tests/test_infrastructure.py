"""Structural regression checks. These do not evaluate AWS authorization or reachability."""
import json
from pathlib import Path
import pytest
R=Path(__file__).resolve().parents[1]/'projects'
ROOTS=sorted(R.glob('*/iac/terraform'))
def resources(index): return json.loads((ROOTS[index]/'resource.tf.json').read_text())['resource']
def test_one_root_per_project():
    assert len(ROOTS)==4
    assert not list(R.glob('*/iac/terraform/envs'))
@pytest.mark.parametrize('root',ROOTS)
def test_account_and_provider_guards(root):
    v=json.loads((root/'variable.tf.json').read_text())['variable']
    p=json.loads((root/'provider.tf.json').read_text())['provider']['aws']
    assert 'validation' in v['account_id'] and p['allowed_account_ids']==['${var.account_id}']
    assert json.loads((root/'terraform.tf.json').read_text())['terraform']['required_providers']['aws']['version']=='5.100.0'
def test_network_inspection_both_directions():
    r=resources(0)
    assert r['aws_route']['tgw_to_firewall']['vpc_endpoint_id']=='${local.endpoint_by_az[var.azs[count.index]]}'
    assert r['aws_route']['nat_return']['vpc_endpoint_id']=='${local.endpoint_by_az[var.azs[each.value.az]]}'
    assert r['aws_route']['firewall_return']['transit_gateway_id']=='${aws_ec2_transit_gateway.core.id}'
    assert r['aws_ec2_transit_gateway_vpc_attachment']['inspection']['appliance_mode_support']=='enable'
    assert r['aws_nat_gateway']['egress']['count']==2
    assert r['aws_subnet']['tgw']!=r['aws_subnet']['firewall']
def test_spoke_segmentation_is_explicit():
    r=resources(0)
    assert r['aws_ec2_transit_gateway_route']['block_east_west']['blackhole'] is True
    assert r['aws_ec2_transit_gateway']['core']['default_route_table_propagation']=='disable'
    assert 'aws_ec2_transit_gateway_route_table_propagation' not in r

def test_boundary_allows_and_denies():
    r=resources(1);p=r['aws_iam_policy']['boundary']['policy']
    assert '"Effect": "Allow"' in p and '"Effect": "Deny"' in p
    assert 'iam:*' in p
    for name in ('auditor','responder','deployer'):
        assert r['aws_iam_role'][name]['permissions_boundary']=='${aws_iam_policy.boundary.arn}'
    trust=r['aws_iam_role']['breakglass']['assume_role_policy']
    assert 'aws:MultiFactorAuthPresent' in trust and 'aws:MultiFactorAuthAge' in trust
    assert r['aws_organizations_policy_attachment']['guardrail']['count']=='${var.scp_target_id == "" ? 0 : 1}'
@pytest.mark.parametrize('idx',[1,2])
def test_trail_bucket_policy_and_validation(idx):
    r=resources(idx)
    assert r['aws_cloudtrail']['audit']['enable_log_file_validation']
    assert r['aws_cloudtrail']['audit']['is_multi_region_trail']
    policy=r['aws_s3_bucket_policy']['audit']['policy']
    assert 'aws:SourceArn' in policy and 'aws:SecureTransport' in policy
    assert 'aws_s3_bucket_policy.audit' in r['aws_cloudtrail']['audit']['depends_on']
def test_private_search_and_signed_principal_scope():
    r=resources(2);s=r['aws_opensearch_domain']['search']
    assert 'vpc_options' in s and s['domain_endpoint_options']['enforce_https']
    assert s['node_to_node_encryption']['enabled'] and s['encrypt_at_rest']['enabled']
    assert '0.0.0.0/0' not in s['access_policies'] and '"AWS": "*"' not in s['access_policies']
    assert 'securityhub-*/_doc/*' in s['access_policies']
    assert r['aws_lambda_function_event_invoke_config']['ingest']['maximum_retry_attempts']==2
    assert 'dead_letter_config' in r['aws_cloudwatch_event_target']['ingest']
def test_api_connected_and_bounded():
    r=resources(3)
    assert r['aws_lambda_function']['api']['handler']=='handler.handler'
    assert r['aws_lambda_function']['api']['environment']['variables']['TABLE_NAME']=='${aws_dynamodb_table.requests.name}'
    assert r['aws_api_gateway_method']['post']['authorization']=='COGNITO_USER_POOLS'
    assert r['aws_cognito_user_pool']['users']['mfa_configuration']=='ON'
    assert r['aws_dynamodb_table']['requests']['deletion_protection_enabled']
    assert r['aws_dynamodb_table']['requests']['point_in_time_recovery']['enabled']
    assert 'dynamodb:PutItem' in r['aws_iam_role_policy']['api_data']['policy']
    assert r['aws_vpc_endpoint']['dynamodb']['route_table_ids']==['${aws_route_table.private.id}']
    assert 'aws_wafv2_web_acl_association' in r

def test_no_public_subnets_or_ssh_rules():
    for i in range(4):
        r=resources(i)
        for subnet in r.get('aws_subnet',{}).values():assert subnet.get('map_public_ip_on_launch') is False
        for sg in r.get('aws_security_group',{}).values():
            for rule in sg.get('ingress',[]):assert rule.get('from_port')!=22
