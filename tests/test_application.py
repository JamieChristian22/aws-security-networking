import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import pytest

ROOT = Path(__file__).resolve().parents[1]
def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
api = load('api', 'projects/04-secure-serverless-api/lambda/handler.py')
ingest = load('ingest', 'projects/03-security-logging-detection/lambda/ingest_securityhub.py')
CTX = SimpleNamespace(aws_request_id='test-only')
class Conflict(Exception):
    response = {'Error': {'Code': 'ConditionalCheckFailedException'}}
class Table:
    def __init__(self): self.items = {}
    def put_item(self, Item, ConditionExpression):
        assert ConditionExpression == 'attribute_not_exists(request_id)'
        if Item['request_id'] in self.items: raise Conflict()
        self.items[Item['request_id']] = Item
    def get_item(self, Key, ConsistentRead):
        assert ConsistentRead
        return {'Item': self.items[Key['request_id']]}
def event():
    return {'httpMethod':'POST','headers':{'Content-Type':'application/json','Idempotency-Key':'unique_request_001'},'body':json.dumps({'customer_id':'customer1','action':'create'}),'requestContext':{'authorizer':{'claims':{'sub':'user-1'}}}}
def test_create_and_replay():
    t = Table(); e = event()
    assert api.handle(e, CTX, t)['statusCode'] == 201
    assert api.handle(e, CTX, t)['statusCode'] == 200
    assert len(t.items) == 1
    e['body'] = json.dumps({'customer_id':'customer2','action':'create'})
    assert api.handle(e, CTX, t)['statusCode'] == 409

def test_users_cannot_collide():
    t=Table();e=event();api.handle(e,CTX,t)
    e['requestContext']['authorizer']['claims']['sub']='user-2'
    assert api.handle(e,CTX,t)['statusCode']==201
    assert len(t.items)==2

@pytest.mark.parametrize('body',[None,'{','[]','null','1','"hello"','{}',json.dumps({'customer_id':5,'action':'create'}),json.dumps({'customer_id':'a'*65,'action':'create'}),json.dumps({'customer_id':'a','action':[]}),json.dumps({'customer_id':'a','action':'delete'}),json.dumps({'customer_id':'a','action':'create','owner_sub':'other'}),'x'*9000])
def test_bad_bodies(body):
    e=event();e['body']=body;t=Table()
    assert api.handle(e,CTX,t)['statusCode']==400
    assert not t.items

def test_missing_auth():
    e=event();e['requestContext']={}
    assert api.handle(e,CTX,Table())['statusCode']==401
@pytest.mark.parametrize('field,value',[('Content-Type','text/plain'),('Idempotency-Key','tiny')])
def test_bad_headers(field,value):
    e=event();e['headers'][field]=value
    assert api.handle(e,CTX,Table())['statusCode']==400

def test_base64():
    import base64
    e=event();e['body']=base64.b64encode(e['body'].encode()).decode();e['isBase64Encoded']=True
    assert api.handle(e,CTX,Table())['statusCode']==201
    e['body']='not base64!'
    assert api.handle(e,CTX,Table())['statusCode']==400

def test_storage_failure_is_retryable_and_sanitized():
    class Broken:
        def put_item(self,**kw): raise RuntimeError('sensitive internal detail')
    r=api.handle(event(),CTX,Broken())
    assert r['statusCode']==503 and 'sensitive' not in r['body']

def finding():
    return {'Id':'test/only/1','ProductArn':'arn:aws:securityhub:us-east-1:111122223333:product/test','AwsAccountId':'111122223333','UpdatedAt':'2026-01-01T00:00:00Z','Severity':{'Label':'HIGH'},'Title':'Synthetic test'}
def sh_event(): return {'source':'aws.securityhub','detail-type':'Security Hub Findings - Imported','detail':{'findings':[finding()]}}
def test_finding_stable_and_versioned_ids():
    f=finding();a=ingest.normalize(f)
    assert a==ingest.normalize(copy.deepcopy(f))
    f['UpdatedAt']='2026-01-02T00:00:00Z'
    assert a[1]!=ingest.normalize(f)[1]
    assert len(a[1])==64 and '/' not in a[1]

def test_archive_before_index_and_retry():
    calls=[]
    def archive(*args):calls.append('archive')
    def index(*args):calls.append('index');raise RuntimeError('temporary outage')
    with pytest.raises(RuntimeError):ingest.process(sh_event(),archive,index)
    assert calls==['archive','index']
    assert ingest.process(sh_event(),lambda *a:None,lambda *a:None)=={'indexed':1}

@pytest.mark.parametrize('field,value',[('Id',None),('UpdatedAt','bad'),('UpdatedAt','2026-01-01'),('Severity',{'Label':'BANANA'}),('Severity','HIGH')])
def test_bad_findings(field,value):
    f=finding();f[field]=value
    with pytest.raises(ValueError):ingest.normalize(f)

def test_archive_failure_does_not_index():
    indexed=[]
    def fail(*args):raise RuntimeError('archive unavailable')
    with pytest.raises(RuntimeError):ingest.process(sh_event(),fail,lambda *a:indexed.append(a))
    assert not indexed

def test_invalid_event_rejected():
    with pytest.raises(ValueError):ingest.process({},lambda *a:None,lambda *a:None)
