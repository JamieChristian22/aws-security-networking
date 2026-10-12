import base64
import copy
import json
from types import SimpleNamespace
import pytest
from hypothesis import given,settings,strategies as st
from test_application import api,ingest,event,Table,CTX,finding,sh_event,Conflict

@pytest.mark.parametrize('value',[None,[],1,'bad',True])
def test_invalid_event_envelopes(value):
    assert api.handle(value,CTX,Table())['statusCode']==400
@pytest.mark.parametrize('value',[None,[],1,'bad',True,{}])
@pytest.mark.parametrize('path',[('requestContext',),('requestContext','authorizer'),('requestContext','authorizer','claims')])
def test_null_nested_auth(value,path):
    e=event();parent=e
    for k in path[:-1]:parent=parent[k]
    parent[path[-1]]=value
    assert api.handle(e,CTX,Table())['statusCode']==401
@pytest.mark.parametrize('subject',[None,[],{},1,'','a'*129,'\ud800'])
def test_invalid_subject(subject):
    e=event();e['requestContext']['authorizer']['claims']['sub']=subject
    assert api.handle(e,CTX,Table())['statusCode']==401
@pytest.mark.parametrize('headers',[[],['x'],'bad',{'Content-Type':4},{'content-type':'application/json','Content-Type':'application/json'}])
def test_invalid_header_shapes(headers):
    e=event();e['headers']=headers
    assert api.handle(e,CTX,Table())['statusCode']==400
@pytest.mark.parametrize('multiple',[{'Idempotency-Key':['x','y']},{'Content-Type':['text/plain']},{'X-Ignore':'string'},[],{'x':['a'],'X':['a']}])
def test_ambiguous_multivalue_headers(multiple):
    e=event();e['multiValueHeaders']=multiple
    assert api.handle(e,CTX,Table())['statusCode']==400

def test_matching_multivalue_headers_and_only_multivalue():
    e=event();e['multiValueHeaders']={k:[v] for k,v in e['headers'].items()}
    assert api.handle(e,CTX,Table())['statusCode']==201
    e['headers']={}
    assert api.handle(e,CTX,Table())['statusCode']==201
@pytest.mark.parametrize('body',['{"customer_id":"a","customer_id":"b","action":"create"}','{"customer_id":"a","action":"create","action":"review"}','\ud800','['*1500+']'*1500])
def test_duplicate_and_unicode_deep_json(body):
    e=event();e['body']=body
    assert api.handle(e,CTX,Table())['statusCode']==400
@pytest.mark.parametrize('flag',['false',1,None,[]])
def test_invalid_encoding_flag(flag):
    e=event();e['isBase64Encoded']=flag
    assert api.handle(e,CTX,Table())['statusCode']==400

def test_decoded_size_boundary():
    e=event();raw=e['body'];e['body']=raw+' '*(api.MAX_BODY-len(raw))
    assert api.handle(e,CTX,Table())['statusCode']==201
    e['body']+=' '
    assert api.handle(e,CTX,Table())['statusCode']==400
    e['body']=base64.b64encode(e['body'].encode()).decode();e['isBase64Encoded']=True
    assert api.handle(e,CTX,Table())['statusCode']==400

def test_invalid_utf8_base64():
    e=event();e['body']=base64.b64encode(b'\xff').decode();e['isBase64Encoded']=True
    assert api.handle(e,CTX,Table())['statusCode']==400

def test_wrong_method():
    e=event();e['httpMethod']='GET'
    assert api.handle(e,CTX,Table())['statusCode']==400
@pytest.mark.parametrize('existing',[None,{},'bad'])
def test_conflict_without_readable_item_is_retryable(existing):
    class Missing:
        def put_item(self,**kw):raise Conflict()
        def get_item(self,**kw):return {'Item':existing}
    assert api.handle(event(),CTX,Missing())['statusCode']==503

def test_conflict_read_failure():
    class Missing:
        def put_item(self,**kw):raise Conflict()
        def get_item(self,**kw):raise RuntimeError('private detail')
    assert api.handle(event(),CTX,Missing())['statusCode']==503

def test_cross_account_finding_ids_differ():
    f=finding();a=ingest.normalize(f)[1];f['AwsAccountId']='444455556666'
    assert a!=ingest.normalize(f)[1]

def test_timezone_equivalent_finding_ids_match():
    f=finding();a=ingest.normalize(f)[1];f['UpdatedAt']='2025-12-31T19:00:00-05:00'
    assert a==ingest.normalize(f)[1]
@pytest.mark.parametrize('patch',[{'AwsAccountId':'abc'},{'Id':'a'*513},{'ProductArn':'https://untrusted.example'},{'Title':[]},{'Severity':{'Label':[]}},{'Resources':{}},{'Resources':[3]},{'Resources':[{}]*101}])
def test_bad_findings_are_rejected(patch):
    with pytest.raises(ValueError):ingest.normalize({**finding(),**patch})
@pytest.mark.parametrize('detail',[None,[],{},'bad',{'findings':[]},{'findings':[finding()]*101}])
def test_bad_detail(detail):
    e=sh_event();e['detail']=detail
    with pytest.raises(ValueError):ingest.process(e,lambda *a:None,lambda *a:None)

def test_malformed_batch_has_no_partial_writes():
    e=sh_event();e['detail']['findings'].append({'Id':'incomplete'});calls=[]
    with pytest.raises(ValueError):ingest.process(e,lambda *a:calls.append(a),lambda *a:calls.append(a))
    assert not calls

def test_oversize_finding_rejected():
    e=sh_event();e['detail']['findings'][0]['Description']='x'*ingest.MAX_FINDING_BYTES
    with pytest.raises(ValueError):ingest.process(e,lambda *a:None,lambda *a:None)

json_values=st.recursive(st.none()|st.booleans()|st.integers()|st.text(max_size=80),lambda children:st.lists(children,max_size=5)|st.dictionaries(st.text(max_size=15),children,max_size=5),max_leaves=20)
@settings(max_examples=300,derandomize=True,deadline=None)
@given(json_values)
def test_arbitrary_json_body_never_crashes(value):
    e=event();e['body']=json.dumps(value)
    assert api.handle(e,CTX,Table())['statusCode'] in (201,400)
@settings(max_examples=300,derandomize=True,deadline=None)
@given(st.text(max_size=800))
def test_arbitrary_text_body_never_crashes(value):
    e=event();e['body']=value
    assert api.handle(e,CTX,Table())['statusCode'] in (201,400)

@pytest.mark.parametrize('value',[None,[],1,'bad'])
def test_nonobject_finding_is_rejected(value):
    with pytest.raises(ValueError):ingest.normalize(value)
