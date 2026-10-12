"""In-process AWS service emulation and real SDK serialization/signing. Not live AWS."""
import copy
import json
from types import SimpleNamespace
from unittest.mock import Mock
from urllib.error import HTTPError
import boto3
from botocore.credentials import Credentials
from botocore.stub import Stubber
from moto import mock_aws
import pytest
from test_application import api,ingest,event,CTX,finding,sh_event

@mock_aws
def test_lambda_entrypoint_dynamodb_lifecycle(monkeypatch):
    db=boto3.resource('dynamodb',region_name='us-east-1')
    table=db.create_table(TableName='requests',KeySchema=[{'AttributeName':'request_id','KeyType':'HASH'}],AttributeDefinitions=[{'AttributeName':'request_id','AttributeType':'S'}],BillingMode='PAY_PER_REQUEST')
    monkeypatch.setenv('TABLE_NAME','requests')
    e=event();created=api.handler(e,CTX)
    assert created['statusCode']==201
    assert api.handler(e,CTX)['statusCode']==200
    changed=copy.deepcopy(e);changed['body']=json.dumps({'customer_id':'customer1','action':'update'})
    assert api.handler(changed,CTX)['statusCode']==409
    other=copy.deepcopy(e);other['requestContext']['authorizer']['claims']['sub']='user-2'
    assert api.handler(other,CTX)['statusCode']==201
    rows=table.scan()['Items'];assert len(rows)==2
    assert {x['owner_sub'] for x in rows}=={'user-1','user-2'}
    assert all('payload_hash' in x for x in rows)

@mock_aws
def test_ambiguous_commit_then_retry_is_not_duplicate():
    db=boto3.resource('dynamodb');table=db.create_table(TableName='requests',KeySchema=[{'AttributeName':'request_id','KeyType':'HASH'}],AttributeDefinitions=[{'AttributeName':'request_id','AttributeType':'S'}],BillingMode='PAY_PER_REQUEST')
    class CommitThenTimeout:
        def put_item(self,**kw):
            table.put_item(**kw)
            raise TimeoutError('response lost after commit')
    e=event()
    assert api.handle(e,CTX,CommitThenTimeout())['statusCode']==503
    assert api.handle(e,CTX,table)['statusCode']==200
    assert table.scan()['Count']==1

@mock_aws
def test_dynamodb_throttle_client_error():
    db=boto3.resource('dynamodb');table=db.Table('requests')
    with Stubber(table.meta.client) as stub:
        stub.add_client_error('put_item',service_error_code='ProvisionedThroughputExceededException',service_message='synthetic throttle',http_status_code=400)
        r=api.handle(event(),CTX,table)
        assert r['statusCode']==503
        assert 'synthetic' not in r['body']
        stub.assert_no_pending_responses()

@mock_aws
def test_ingestion_entrypoint_archives_real_sdk_payload(monkeypatch):
    s3=boto3.client('s3');s3.create_bucket(Bucket='test-findings-archive')
    s3.put_bucket_versioning(Bucket='test-findings-archive',VersioningConfiguration={'Status':'Enabled'})
    monkeypatch.setenv('ARCHIVE_BUCKET','test-findings-archive');monkeypatch.setenv('OPENSEARCH_ENDPOINT','vpc-test-abc.us-east-1.es.amazonaws.com')
    indexed=[]
    monkeypatch.setattr(ingest,'signed_put',lambda session,endpoint,index_name,doc_id,payload:indexed.append((index_name,doc_id,json.loads(payload))))
    assert ingest.handler(sh_event(),CTX)=={'indexed':1}
    assert ingest.handler(sh_event(),CTX)=={'indexed':1}
    objects=s3.list_objects_v2(Bucket='test-findings-archive')['Contents'];assert len(objects)==1
    obj=s3.get_object(Bucket='test-findings-archive',Key=objects[0]['Key'])
    assert obj['ServerSideEncryption']=='AES256'
    assert json.loads(obj['Body'].read())==finding()
    assert len(s3.list_object_versions(Bucket='test-findings-archive')['Versions'])==2
    assert indexed[0]==indexed[1]

@mock_aws
def test_index_failure_preserves_archive_and_replay_recovers(monkeypatch):
    s3=boto3.client('s3');s3.create_bucket(Bucket='test-findings-archive')
    monkeypatch.setenv('ARCHIVE_BUCKET','test-findings-archive');monkeypatch.setenv('OPENSEARCH_ENDPOINT','vpc-test-abc.us-east-1.es.amazonaws.com')
    def fail(*a):raise HTTPError('https://redacted',503,'synthetic outage',{},None)
    monkeypatch.setattr(ingest,'signed_put',fail)
    with pytest.raises(HTTPError):ingest.handler(sh_event(),CTX)
    assert s3.list_objects_v2(Bucket='test-findings-archive')['KeyCount']==1
    monkeypatch.setattr(ingest,'signed_put',lambda *a:None)
    assert ingest.handler(sh_event(),CTX)=={'indexed':1}

@mock_aws
def test_s3_access_denied_prevents_index(monkeypatch):
    s3=boto3.client('s3')
    monkeypatch.setenv('ARCHIVE_BUCKET','test-findings-archive');monkeypatch.setenv('OPENSEARCH_ENDPOINT','vpc-test-abc.us-east-1.es.amazonaws.com')
    session=Mock(region_name='us-east-1');session.client.return_value=s3
    monkeypatch.setattr(boto3,'Session',lambda:session)
    indexed=Mock();monkeypatch.setattr(ingest,'signed_put',indexed)
    with Stubber(s3) as stub:
        stub.add_client_error('put_object',service_error_code='AccessDenied',http_status_code=403)
        with pytest.raises(Exception) as err:ingest.handler(sh_event(),CTX)
        assert err.value.response['Error']['Code']=='AccessDenied'
    indexed.assert_not_called()

class Transport:
    def __init__(self,status=201):self.status=status;self.requests=[]
    def open(self,request,timeout):
        self.requests.append((request,timeout));return self
    def __enter__(self):return self
    def __exit__(self,*args):return False

def session(region='us-east-1',creds=True):
    return SimpleNamespace(region_name=region,get_credentials=lambda:Credentials('testing','testing','testing') if creds else None)

def test_sigv4_request_has_exact_signed_body_and_scope():
    transport=Transport();payload=b'{"severity":"HIGH"}'
    ingest.signed_put(session(),'vpc-test-abc.us-east-1.es.amazonaws.com','securityhub-2026.01','a'*64,payload,transport)
    req,timeout=transport.requests[0]
    h={k.lower():v for k,v in req.header_items()}
    assert req.method=='PUT' and req.data==payload and timeout==10
    assert req.full_url.endswith('/securityhub-2026.01/_doc/'+'a'*64)
    assert 'AWS4-HMAC-SHA256' in h['authorization'] and '/us-east-1/es/aws4_request' in h['authorization']
    assert h['x-amz-security-token']=='testing'
@pytest.mark.parametrize('endpoint',['http://vpc-test.us-east-1.es.amazonaws.com','vpc-test.us-east-1.es.amazonaws.com/escape','vpc-test.us-east-1.es.amazonaws.com.attacker.example','search-public.us-east-1.es.amazonaws.com','vpc-test.us-west-2.es.amazonaws.com'])
def test_invalid_search_destination_never_sends(endpoint):
    t=Transport()
    with pytest.raises(ValueError):ingest.signed_put(session(),endpoint,'securityhub-2026.01','a'*64,b'{}',t)
    assert not t.requests
@pytest.mark.parametrize('index,doc',[('../escape','a'*64),('securityhub-2026.01','../escape')])
def test_invalid_document_path(index,doc):
    with pytest.raises(ValueError):ingest.signed_put(session(),'vpc-test.us-east-1.es.amazonaws.com',index,doc,b'{}',Transport())
@pytest.mark.parametrize('status',[301,302,400,403,429,500,503])
def test_unsuccessful_index_status_raises(status):
    with pytest.raises(RuntimeError):ingest.signed_put(session(),'vpc-test.us-east-1.es.amazonaws.com','securityhub-2026.01','a'*64,b'{}',Transport(status))
def test_no_signing_credentials():
    with pytest.raises(RuntimeError):ingest.signed_put(session(creds=False),'vpc-test.us-east-1.es.amazonaws.com','securityhub-2026.01','a'*64,b'{}',Transport())
def test_redirect_handler_will_not_forward_credentials():
    assert ingest.NoRedirect().redirect_request(None,None,302,'redirect',{},'https://attacker.example') is None

def test_real_transport_is_constructed_with_redirect_and_proxy_protection(monkeypatch):
    transport=Transport();built=[]
    def build(*handlers):built.extend(handlers);return transport
    monkeypatch.setattr(ingest,'build_opener',build)
    ingest.signed_put(session(),'vpc-test.us-east-1.es.amazonaws.com','securityhub-2026.01','a'*64,b'{}')
    assert any(isinstance(h,ingest.NoRedirect) for h in built)
    assert any(isinstance(h,ingest.ProxyHandler) and h.proxies=={} for h in built)

@mock_aws
def test_lambda_entrypoint_rejects_public_search_endpoint(monkeypatch):
    monkeypatch.setenv('OPENSEARCH_ENDPOINT','search-public.us-east-1.es.amazonaws.com')
    with pytest.raises(ValueError):ingest.handler(sh_event(),CTX)
