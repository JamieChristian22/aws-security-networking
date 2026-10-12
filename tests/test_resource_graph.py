"""Source-graph consistency checks, not Terraform expression evaluation."""
import json
import re
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
ROOTS=sorted((ROOT/'projects').glob('*/iac/terraform'))
@pytest.mark.parametrize('root',ROOTS,ids=lambda p:p.parents[1].name)
def test_resource_references_resolve_in_same_root(root):
    configs=[json.loads(p.read_text()) for p in root.glob('*.tf.json')]
    declared={f'{kind}.{name}' for c in configs for kind,items in c.get('resource',{}).items() for name in items}
    references=set()
    for config in configs:
        references.update(re.findall(r'(?<![.\w])(aws_[a-z_]+\.[a-zA-Z_][a-zA-Z_0-9]*)',json.dumps(config)))
    assert not references-declared, sorted(references-declared)
@pytest.mark.parametrize('root',ROOTS,ids=lambda p:p.parents[1].name)
def test_each_s3_bucket_has_explicit_public_access_block(root):
    r=json.loads((root/'resource.tf.json').read_text())['resource']
    blocks=list(r.get('aws_s3_bucket_public_access_block',{}).values())
    for name in r.get('aws_s3_bucket',{}):
        match=[b for b in blocks if b.get('bucket')=='${aws_s3_bucket.'+name+'.id}']
        assert len(match)==1
        assert all(match[0].get(k) is True for k in ('block_public_acls','block_public_policy','ignore_public_acls','restrict_public_buckets'))
def test_every_lambda_handler_points_to_a_real_function():
    import ast
    functions=0
    for root in ROOTS:
        r=json.loads((root/'resource.tf.json').read_text())['resource']
        for config in r.get('aws_lambda_function',{}).values():
            module,function=config['handler'].rsplit('.',1)
            file=root.parents[1]/'lambda'/(module+'.py')
            tree=ast.parse(file.read_text())
            assert any(isinstance(n,ast.FunctionDef) and n.name==function for n in tree.body)
            assert config['source_code_hash'].startswith('${data.archive_file.')
            assert 0<config['reserved_concurrent_executions']<=10
            functions+=1
    assert functions==2
