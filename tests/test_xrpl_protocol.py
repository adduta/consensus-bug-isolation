import os
import pytest
from src.protocols.xrpl import XRPLProtocol
from src.models.messages import Proposal, Validation

SAMPLE_RUN = 'data/buggy-7-1-0-6-small-scope/1686951117'

protocol = XRPLProtocol()

def test_get_num_nodes():
    assert protocol.get_num_nodes() == 7

def test_get_fields_returns_11_entries():
    fields = protocol.get_fields()
    assert len(fields) == 11

def test_get_fields_types():
    fields = protocol.get_fields()
    types = {f[0] for f in fields}
    assert Proposal in types
    assert Validation in types

def test_get_bug_types():
    assert set(protocol.get_bug_types()) == {'Incompatible', 'Insufficient', 'Agreement'}

def test_parse_log_returns_messages():
    path = os.path.join(SAMPLE_RUN, 'validator_0.txt')
    if not os.path.exists(path):
        pytest.fail('sample data not present')
    messages = protocol.parse_log(path)
    assert len(messages) > 0
    assert all(isinstance(m, (Proposal, Validation)) for m in messages)

def test_filter_messages_node_0_uses_low_partition():
    class FakeMsg:
        def __init__(self, peers):
            self.peers = set(peers)
    msgs = [FakeMsg([0, 1]), FakeMsg([5, 6]), FakeMsg([2, 3])]
    filtered = protocol.filter_messages(msgs, node_id=0)
    # node 5 and 6 are NOT in FILTER_SET_LOW, so message with only [5,6] is dropped
    assert all(not m.peers.isdisjoint({0,1,2,3,4}) for m in filtered)

def test_filter_messages_node_6_uses_high_partition():
    class FakeMsg:
        def __init__(self, peers):
            self.peers = set(peers)
    msgs = [FakeMsg([0, 1]), FakeMsg([5, 6])]
    filtered = protocol.filter_messages(msgs, node_id=6)
    # node 0 and 1 are NOT in FILTER_SET_HIGH, so [0,1] message is dropped
    assert all(not m.peers.isdisjoint({2,3,4,5,6}) for m in filtered)

def test_is_successful_correct_run():
    path = os.path.join(SAMPLE_RUN)
    if not os.path.exists(path):
        pytest.fail('sample data not present')
    result = protocol.is_successful(path)
    assert isinstance(result, bool)

def test_wrap_observations_generates_5_thresholds():
    obs = protocol.wrap_observations('some_predicate', observed_nodes={0, 1, 2})
    assert len(obs) == 5
    # All threshold keys must be present
    for t in range(5):
        assert f'"some_predicate" > {t}' in obs
    # 3 nodes in SET_LOW={0..4}: thresholds 0,1,2 are True; 3,4 are False
    assert obs['"some_predicate" > 0'] is True
    assert obs['"some_predicate" > 2'] is True
    assert obs['"some_predicate" > 3'] is False

def test_wrap_observations_empty_nodes():
    obs = protocol.wrap_observations('pred', observed_nodes=set())
    assert all(v is False for v in obs.values())

def test_classify_run_returns_set():
    path = SAMPLE_RUN
    if not os.path.exists(path):
        pytest.fail('sample data not present')
    result = protocol.classify_run(path)
    assert isinstance(result, set)
    assert result.issubset({'Incompatible', 'Insufficient', 'Agreement'})