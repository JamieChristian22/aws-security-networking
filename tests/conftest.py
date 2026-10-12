"""All automated local tests use synthetic credentials and prohibit network sockets."""
import socket
import pytest

@pytest.fixture(autouse=True)
def no_live_aws(monkeypatch):
    for key,value in {'AWS_ACCESS_KEY_ID':'testing','AWS_SECRET_ACCESS_KEY':'testing','AWS_SESSION_TOKEN':'testing','AWS_DEFAULT_REGION':'us-east-1','AWS_EC2_METADATA_DISABLED':'true'}.items():
        monkeypatch.setenv(key,value)
    def denied(*args,**kwargs):
        raise AssertionError('Offline tests must not create network sockets')
    monkeypatch.setattr(socket,'socket',denied)
