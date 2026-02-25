# Boundary: UniGuru-Core
from src.uniguru.core import UniGuruCoreRequest, ContextItem, UniGuruCore
from src.uniguru.enforcement import AllowAllEnforcement


def canonical_request():
    return UniGuruCoreRequest(
        requestId='req-123',
        userContext={'userId': 'u1'},
        query={'prompt': 'Explain X', 'type': 'explain'},
        context=[ContextItem(id='c1', type='document', contentHash='h1')],
        flags={'interactive': False, 'mode': 'strict'}
    )


def test_deterministic_core():
    enforcement = AllowAllEnforcement()
    core = UniGuruCore(enforcement)
    req = canonical_request()
    a = core.handle(req)
    b = core.handle(req)
    assert a == b
    assert a.status == 'ok'
    assert 'Answer:' in a.result.get('value','')
