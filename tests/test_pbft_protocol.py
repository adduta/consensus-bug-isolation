import pytest
from src.protocols.pbft import PBFTProtocol, PrePrepare, Prepare, Commit, ViewChange

protocol = PBFTProtocol()

# operation mutation, validity+agreement
INVALID_OPERATION_FILE = 'out/tests-D0-C1-ss/out95.txt'
# seq-number mutation, agreement only after view-change
SEQ_NO_REPLAY_FILE = 'out/tests-D1-C2-ss/out7.txt'
# view-change fault, termination
VIEW_CHANGE_FAULT_FILE = 'out/tests-D1-C2-ss/out49.txt'
# partition timeout, termination
PARTITION_TIMEOUT_FILE = 'out/tests-D1-C0/out115.txt'
# split-brain, agreement, high viewNo
SPLIT_BRAIN_FILE = 'out/tests-D2-C0/out87.txt'
# correct run (no violation)
CORRECT_FILE = 'out/tests-D1-C0/out1.txt'

def _skip_if_absent(path):
    import os
    if not os.path.exists(path):
        pytest.skip(f'{path} not present')

def test_get_num_nodes():
    assert protocol.get_num_nodes() == 1

def test_get_bug_types():
    assert set(protocol.get_bug_types()) == {
        'Invalid Operation', 'Seq-No Replay', 'View-Change Fault', 'Partition Timeout', 'Split Brain'
    }

def test_get_fields_covers_root_causes():
    fields = protocol.get_fields()
    field_names = [f[1] for f in fields]
    # Invalid Operation / Seq-No Replay require PRE-PREPARE fields
    assert 'operation_first' in field_names
    assert 'seq_no' in field_names
    # View-Change Fault requires VIEW-CHANGE
    assert 'new_view_no' in field_names

def test_classify_run_invalid_operation():
    _skip_if_absent(INVALID_OPERATION_FILE)
    result = protocol.classify_run(INVALID_OPERATION_FILE)
    assert 'Invalid Operation' in result

def test_classify_run_seq_no_replay():
    _skip_if_absent(SEQ_NO_REPLAY_FILE)
    result = protocol.classify_run(SEQ_NO_REPLAY_FILE)
    assert 'Seq-No Replay' in result

def test_classify_run_view_change_fault():
    _skip_if_absent(VIEW_CHANGE_FAULT_FILE)
    result = protocol.classify_run(VIEW_CHANGE_FAULT_FILE)
    assert 'View-Change Fault' in result

def test_classify_run_partition_timeout():
    _skip_if_absent(PARTITION_TIMEOUT_FILE)
    result = protocol.classify_run(PARTITION_TIMEOUT_FILE)
    assert 'Partition Timeout' in result

def test_classify_run_split_brain():
    _skip_if_absent(SPLIT_BRAIN_FILE)
    result = protocol.classify_run(SPLIT_BRAIN_FILE)
    assert 'Split Brain' in result

def test_is_successful_on_non_violation():
    _skip_if_absent(CORRECT_FILE)
    assert protocol.is_successful(CORRECT_FILE) is True

def test_parse_log_returns_preprepare():
    _skip_if_absent(INVALID_OPERATION_FILE)
    messages = protocol.parse_log(INVALID_OPERATION_FILE)
    assert any(isinstance(m, PrePrepare) for m in messages)

def test_filter_messages_is_noop():
    class Msg: pass
    msgs = [Msg(), Msg()]
    assert protocol.filter_messages(msgs, node_id=0) is msgs

def test_wrap_observations_single_entry():
    obs = protocol.wrap_observations('some_pred', observed_nodes={0})
    # PBFT: one threshold entry (observed by >= 1 replica)
    assert '"some_pred" > 0' in obs
    assert obs['"some_pred" > 0'] is True